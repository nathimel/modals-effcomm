"""Script for analyzing the results of the trade-off."""

import sys
from misc.file_util import load_configs
from misc.file_util import load_languages
from modals.modal_measures import ModalComplexityMeasure
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import iff, sav, dlsav
from misc.file_util import set_seed, load_space, save_languages
from altk.effcomm.informativity import *
from altk.effcomm.tradeoff import tradeoff
from misc.file_util import load_utility


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/measure_tradeoff.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Measuring tradeoff ...")

    # Load the experimental data and paths to save results
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

    paths = configs["file_paths"]
    space_fn = paths["meaning_space"]
    sampled_languages_fn = paths["artificial_languages"]
    natural_languages_fn = paths["natural_languages"]
    dominant_languages_fn = paths["dominant_languages"]
    df_fn = paths["analysis"]["data"]

    set_seed(configs["random_seed"])

    # load languages
    print("Loading all languages ...")
    print("sampled...")
    sampled_result = load_languages(sampled_languages_fn)
    print("dominant...")
    dominant_result = load_languages(dominant_languages_fn)
    print("natural...")
    natural_result = load_languages(natural_languages_fn)
    sampled_languages, dominant_languages, natural_languages, id_start = (
        sampled_result["languages"],
        dominant_result["languages"],
        natural_result["languages"],
        sampled_result["id_start"],
    )
    langs = list(set(sampled_languages + dominant_languages + natural_languages))
    print(f"{len(langs)} total langs.")

    # Load trade-off criteria
    space = load_space(space_fn)
    comp_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    inf_measure = SST_Informativity_Measure(
        prior=uniform_prior(space),
        utility=build_utility_matrix(space, load_utility(configs["utility"])),
        agent_type=configs["agent_type"],
    )

    # Get trade-off results
    properties_to_measure = {
        "complexity": comp_measure.language_complexity,
        "informativity": inf_measure.language_informativity,
        "comm_cost": lambda lang: 1 - inf_measure.language_informativity(lang),
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

    save_languages(sampled_languages_fn, langs, id_start, kind="sampled")
    save_languages(dominant_languages_fn, dom_langs, id_start, kind="dominant")
    save_languages(natural_languages_fn, natural_languages, id_start=None, kind="natural")

    print("done.")


if __name__ == "__main__":
    main()
