"""Script for analyzing the results of the trade-off, taking command-line arguments to vary utility and or communicative need."""

import argparse
import os
import numpy as np
from misc import file_util
from modals.modal_measures import language_complexity
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import iff, sav, dlsav, uegaki, cogsci_universal
from altk.effcomm.informativity import informativity
from altk.effcomm.tradeoff import tradeoff


def main(args):

    # Load the experimental data and paths to save results
    config_fn = args.config

    configs = file_util.load_configs(config_fn)    
    paths = configs["file_paths"]

    # Common to all experiments
    space_fn = paths["meaning_space"]    
    sampled_languages_fn = paths["artificial_languages"]
    natural_languages_fn = paths["natural_languages"]    

    # Experiment specific stuff

    # Paths to save files
    experiment_dirname = args.experiment_dirname
    experiment_paths = {
        "prior": f"{experiment_dirname}/prior.yml",
        "utility": f"{experiment_dirname}/utility.yml",
        "dominant": f"{experiment_dirname}/dominant.yml",
        "sampled": f"{experiment_dirname}/sampled.yml",
        "natural": f"{experiment_dirname}/natural.yml",
    }

    file_util.set_seed(configs["random_seed"])

    # load languages
    print("Loading all languages ...")
    print("sampled...")
    sampled_result = file_util.load_languages(sampled_languages_fn)
    print("natural...")
    natural_result = file_util.load_languages(natural_languages_fn)

    id_start = sampled_result["id_start"]
    sampled_languages = sampled_result["languages"]
    natural_languages = natural_result["languages"]

    langs = list(set(sampled_languages + natural_languages))
    print(f"{len(langs)} total langs.")

    # Load trade-off criteria
    space = file_util.load_space(space_fn)

    comp_measure = lambda lang: language_complexity(
        language=lang, mlot=ModalLOT(space, configs["language_of_thought"])
    )

    # Load prior and utility
    if os.path.isfile(experiment_paths["prior"]):
        print("Using specific prior")
        prior = file_util.load_prior(experiment_paths["prior"])
    else:
        prior = file_util.load_prior(configs["file_paths"]["prior"])

    prior = space.prior_to_array(prior)

    base_utility = file_util.load_utility(configs["utility"])

    if os.path.isfile(experiment_paths["utility"]):
        print("Using weighted utility function.")
        # Note that has the same form as prior, so use load_prior
        utility_weights = file_util.load_prior(experiment_paths["utility"])

        # normalize so that informativity <= 1
        # total = sum([float(weight) for weight in utility_weights.values()])
        z = max([float(weight) for weight in utility_weights.values()])
        weights_normed = {}
        for point in space.referents:
            weight_normed = float(utility_weights[point.data]) / z
            weights_normed[point.data] = weight_normed
        # reassign

        utility_weights = weights_normed
        
        # Weight utility function
        # u(p, p') weight(p) * ( fo(p) = fo(p') + fo(p) = fo(p') )
        utility = lambda m, m_: utility_weights[m.data] * base_utility(m, m_)

    else:
        print("Using unweighted utility function.")
        utility = base_utility


    inf_measure = lambda lang: informativity(
        language=lang,
        prior=prior,
        utility=utility,
        agent_type=configs["agent_type"],
    )

    # Get trade-off results
    properties_to_measure = {
        "complexity": comp_measure,
        "simplicity": lambda _: None,  # reset simplicity from evol alg exploration
        "informativity": inf_measure,
        "comm_cost": lambda lang: 1 - inf_measure(lang),
        "uegaki": uegaki,
        "cogsci_universal": cogsci_universal,
    }

    print("Measuring tradeoff ...")
    result = tradeoff(
        languages=langs,
        properties=properties_to_measure,
        x="comm_cost",
        y="complexity",
    )
    dom_langs = result["dominating_languages"]
    langs = result["languages"]

    nat_langs = [lang for lang in langs if lang.natural]

    file_util.save_languages(experiment_paths["sampled"], langs, id_start, kind="sampled")
    file_util.save_languages(
        experiment_paths["dominant"], dom_langs, id_start, kind="dominant"
    )
    file_util.save_languages(
        experiment_paths["natural"], nat_langs, id_start=None, kind="natural"
    )
    print("done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config",
        type=str,
        help="base config file for the experiment parameters held fixed, i.e. pool of languages, meaning space, etc."
    )

    parser.add_argument(
        "experiment_dirname",
        type=str,
        help="name of subfolder in outputs/cogsci/base associated with one analysis. "
    )

    args = parser.parse_args()
    main(args)