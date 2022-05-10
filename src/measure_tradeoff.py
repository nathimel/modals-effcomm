"""Script for analyzing the results of the trade-off."""

import sys
from misc.file_util import load_configs
from misc.file_util import load_languages
from modals.modal_measures import ModalComplexityMeasure
from modals.modal_language_of_thought import ModalLOT
from misc.file_util import set_seed, load_space, save_languages
from modals.modal_language import degree_iff, degree_sav
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
    sampled_languages = load_languages(sampled_languages_fn)
    print("dominant...")
    dominant_languages = load_languages(dominant_languages_fn)
    print("natural...")
    natural_languages = load_languages(natural_languages_fn)
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
    langs, dom_langs = tradeoff(
        languages=langs,
        comp_measure=comp_measure,
        inf_measure=inf_measure,
        degree_naturalness=degree_iff,
        # degree_naturalness=degree_sav
    )

    

    save_languages(sampled_languages_fn, langs, kind="sampled")
    save_languages(dominant_languages_fn, dom_langs, kind="dominant")
    save_languages(natural_languages_fn, natural_languages, kind="natural")

    # df = get_dataframe(langs)
    # df = get_modals_df(langs)
    # plot = get_tradeoff_plot(langs, dom_langs)

    print("done.")

    # write results
    # df.to_csv(df_fn, index=False)


if __name__ == "__main__":
    main()
