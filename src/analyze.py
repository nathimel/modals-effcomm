"""Script for analyzing the results of the trade-off."""

from random import sample
import sys
from misc.file_util import load_configs
from misc.file_util import load_languages
from modals.modal_measures import ModalComplexityMeasure, ModalInformativityMeasure
from modal_effcomm_analyzer import Modal_EffComm_Analyzer
from modals.modal_language_of_thought import ModalLOT
from misc.file_util import set_seed, load_space, save_languages


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
    print("{} total langs...".format(len(langs)), sep=" ")

    ##########################################################################
    # Analysis
    ##########################################################################

    space = load_space(space_fn)
    comp_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    inf_measure = ModalInformativityMeasure()

    print("Measuring languages ...", sep=" ")
    analyzer = Modal_EffComm_Analyzer(langs, comp_measure, inf_measure)
    langs, dom_langs = analyzer.measure_languages()

    save_languages(sampled_languages_fn, langs)
    save_languages(dominant_languages_fn, dom_langs)

    # Estimate pareto frontier curve
    df, plot = analyzer.get_results()
    print("done.")

    # write results
    df.to_csv(df_fn, index=False)
    plot.save(plot_fn, width=10, height=10, dpi=300)


if __name__ == "__main__":
    main()
