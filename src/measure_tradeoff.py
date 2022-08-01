"""Script for analyzing the results of the trade-off."""

import sys
from misc import file_util
from modals.modal_measures import language_complexity
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import iff, sav, dlsav
from altk.effcomm.informativity import informativity
from altk.effcomm.tradeoff import tradeoff


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/measure_tradeoff.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Measuring tradeoff ...")

    # Load the experimental data and paths to save results
    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)

    paths = configs["file_paths"]
    space_fn = paths["meaning_space"]
    prior_fn = paths["prior"]
    sampled_languages_fn = paths["artificial_languages"]
    natural_languages_fn = paths["natural_languages"]
    dominant_languages_fn = paths["dominant_languages"]

    file_util.set_seed(configs["random_seed"])

    # load languages
    print("Loading all languages ...")
    print("sampled...")
    sampled_result = file_util.load_languages(sampled_languages_fn)
    print("dominant...")
    dominant_result = file_util.load_languages(dominant_languages_fn)
    print("natural...")
    natural_result = file_util.load_languages(natural_languages_fn)

    id_start = sampled_result["id_start"]
    sampled_languages = sampled_result["languages"]
    dominant_languages = dominant_result["languages"]
    natural_languages = natural_result["languages"]

    langs = list(set(sampled_languages + dominant_languages + natural_languages))
    print(f"{len(langs)} total langs.")

    # Load trade-off criteria
    space = file_util.load_space(space_fn)
    prior = file_util.load_prior(prior_fn)

    comp_measure = lambda lang: language_complexity(
        language=lang, mlot=ModalLOT(space, configs["language_of_thought"])
    )

    inf_measure = lambda lang: informativity(
        language=lang,
        prior=space.prior_to_array(prior),
        utility=file_util.load_utility(configs["utility"]),
        agent_type=configs["agent_type"],
    )

    # Get trade-off results
    properties_to_measure = {
        "complexity": comp_measure,
        "simplicity": lambda lang: None,  # reset simplicity from evol alg exploration
        "informativity": inf_measure,
        "comm_cost": lambda lang: 1 - inf_measure(lang),
        "iff": lambda lang: lang.degree_property(iff),
        "sav": lambda lang: lang.degree_property(sav),
        "dlsav": dlsav,
    }

    result = tradeoff(
        languages=langs,
        properties=properties_to_measure,
        x="comm_cost",
        y="complexity",
    )
    dom_langs = result["dominating_languages"]
    langs = result["languages"]

    nat_langs = [lang for lang in langs if lang.is_natural()]

    file_util.save_languages(sampled_languages_fn, langs, id_start, kind="sampled")
    file_util.save_languages(
        dominant_languages_fn, dom_langs, id_start, kind="dominant"
    )
    file_util.save_languages(
        natural_languages_fn, nat_langs, id_start=None, kind="natural"
    )
    print("done.")


if __name__ == "__main__":
    main()
