"""Script for analyzing the results of the trade-off."""

import sys
from misc.file_util import load_configs
from misc.file_util import load_languages
from modals.modal_measures import Modal_Complexity_Measure, Modal_Informativity_Measure
from modal_effcomm_analyzer import Modal_EffComm_Analyzer
from modals.modal_language_of_thought import Modal_Language_of_Thought
from modals.modal_meaning import Modal_Meaning_Space
from misc.file_util import load_space
from misc.file_util import save_languages

def main():
    if len(sys.argv) != 8:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/analyze.py path_to_config path_to_space path_to_artificial_languages path_to_natural_languages path_to_dominant_languages path_to_save_dataframe path_to_save_plot")
        print("got argv: ", sys.argv)
        raise TypeError() #TODO: create an actual error class for the package

    print("Analyzing ...", sep=' ')

    config_fn = sys.argv[1]
    space_fn = sys.argv[2]
    sampled_languages_fn = sys.argv[3]
    natural_languages_fn = sys.argv[4]
    dominant_languages_fn = sys.argv[5]
    df_fn = sys.argv[6]
    plot_fn = sys.argv[7]
    configs = load_configs(config_fn)
    space = load_space(space_fn)


    # load languages
    sampled_languages = load_languages(sampled_languages_fn)
    # natural_languages = load_languages(natural_languages_fn)
    # langs = list(set(sampled_languages))
    langs = sampled_languages
    print("{} total langs...".format(len(langs)), sep=' ')

    ##########################################################################
    # Analysis
    ##########################################################################  

    comp_measure = Modal_Complexity_Measure(
        Modal_Language_of_Thought(
            space,
            configs['language_of_thought']
            ))
    inf_measure = Modal_Informativity_Measure()

    analyzer = Modal_EffComm_Analyzer(langs, comp_measure, inf_measure)
    langs, dom_langs = analyzer.measure_languages()

    save_languages(sampled_languages_fn, langs)
    save_languages(dominant_languages_fn, dom_langs)

    # Estimate pareto frontier curve
    df, plot = analyzer.get_results()

    # write results
    df.to_csv(df_fn, index=False)
    plot.save(plot_fn, width=10, height=10, dpi=300)
    

    print("done.")

if __name__ == "__main__":
    main()