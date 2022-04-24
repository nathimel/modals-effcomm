"""Script for analyzing the results of the trade-off."""

import sys
from misc.file_util import load_configs
from misc.file_util import load_languages
from modals.modal_measures import ModalComplexityMeasure
from modals.modal_language_of_thought import ModalLOT
from misc.file_util import set_seed, load_space, save_languages
from modals.modal_language import degree_iff
from altk.effcomm.informativity import *
from altk.effcomm.tradeoff import tradeoff
from altk.effcomm.analysis import get_dataframe, get_tradeoff_plot

def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/analyze.py path_to_config")
        raise TypeError()  # TODO: create an actual error class for the package

    print("Analyzing ...", sep=" ")

    # Load the experimental data and paths to save results
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

    paths = configs["file_paths"]
    space_fn = paths["meaning_space"]
    sampled_languages_fn = paths["artificial_languages"]
    natural_languages_fn = paths["natural_languages"]
    dominant_languages_fn = paths["dominant_languages"]
    df_fn = paths["dataframe"]
    plot_fn = paths["plot"]

    set_seed(configs["random_seed"])

    # load languages
    print("Loading all languages ...", sep=" ")
    sampled_languages = load_languages(sampled_languages_fn)
    natural_languages = load_languages(natural_languages_fn)
    langs = sampled_languages + natural_languages
    print(f"{len(langs)} total langs...")

    # Load trade-off criteria
    space = load_space(space_fn)
    comp_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    inf_measure = SST_Informativity_Measure(
        prior=uniform_prior(space),
        utility=build_utility_matrix(space, indicator),
    )

    # Get trade-off results
    print("Measuring languages ...", sep=" ")
    langs, dom_langs = tradeoff(
        languages=langs,
        comp_measure=comp_measure,
        inf_measure=inf_measure,
        degree_naturalness=degree_iff
    )

    save_languages(sampled_languages_fn, langs)
    save_languages(dominant_languages_fn, dom_langs)

    df = get_dataframe(langs)
    plot = get_tradeoff_plot(langs, dom_langs)

    print("done.")

    # write results
    df.to_csv(df_fn, index=False)
    plot.save(plot_fn, width=10, height=10, dpi=300)


if __name__ == "__main__":
    main()
