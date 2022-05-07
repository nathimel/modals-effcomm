import sys
import scipy
import numpy as np
import pandas as pd
import plotnine as pn
from tqdm import tqdm
from altk.effcomm.analysis import get_dataframe
from misc.file_util import load_languages, load_configs
from modals.modal_language import ModalLanguage


def get_modals_df(languages: list[ModalLanguage]) -> pd.DataFrame:
    """Get a pandas DataFrame for a list of languages containing efficient communication data.

    Args:
        - languages: the list of languages for which to get efficient communication dataframe.

    Returns:
        - data: a pandas DataFrame with rows as individual languages, with the columns specifying their
            - communicative cost
            - cognitive complexity
            - satisfaction of the iff universal
            - Language type (natural or artificial)
    """
    data = []
    for lang in languages:
        point = (
            lang.name,   
            lang.naturalness,            
            0,
            lang.informativity,
            lang.optimality,
            "natural" if lang.is_natural() else "artificial",
            1 - lang.informativity,
            lang.complexity,
        )
        data.append(point)

    data = pd.DataFrame(
        data=data,
        columns=[
            "name",
            "naturalness",            
            "simplicity",
            "informativity",
            "optimality",      
            "Language",
            "comm_cost",
            "complexity",            
        ],
    )

    # Pandas confused by mixed types int and string, so convert back.
    data[["comm_cost", "complexity", "naturalness", "optimality"]] = data[
        ["comm_cost", "complexity", "naturalness", "optimality"]
    ].apply(pd.to_numeric)

    return data


def get_modals_plot(
    languages: list[ModalLanguage], dominating_languages: list[ModalLanguage]
) -> pn.ggplot:
    """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

    Returns:
        - plot: a plotnine 2D plot of the trade-off.
    """
    data = get_dataframe(languages)
    pareto_df = get_dataframe(dominating_languages)

    natural_data = data[data["Language"] == "natural"]

    plot = (
        pn.ggplot(data=data, mapping=pn.aes(x="comm_cost", y="complexity"))
        + pn.scale_x_continuous(limits=[0, 1])
        + pn.geom_point(  # all langs
            stroke=0,
            alpha=1,
            mapping=pn.aes(color="naturalness"),
        )
        + pn.geom_point(  # The natural languages
            natural_data,
            color="red",
            shape="x",
            size=4,
        )
        + pn.geom_line(size=1, data=pareto_df)
        + pn.xlab("Communicative cost of languages")
        + pn.ylab("Complexity of languages")
        + pn.scale_color_cmap("cividis")
    )
    return plot


def full_analysis(
    data, predictor: str, property: str, num_bootstrap_samples=100
) -> str:
    """Measures pearson correlation coefficient for nauze-ness, optimality.
    Use nonparametric bootstrap for multiple confidence intervals."""
    min_percent = 0.01  # must be > 2/ len(data)
    intervals = 5
    boots = [int(item * 100) for item in np.geomspace(min_percent, 1.0, intervals)]
    confidence_intervals_df = pd.DataFrame(
        {"bootstrap_sample_percent": boots, "low": None, "high": None}
    )

    r, _ = scipy.stats.pearsonr(data[property], data[predictor])
    for i, bootstrap_sample_percent in enumerate(
        np.geomspace(min_percent, 1.0, num=intervals)
    ):
        rhos = []
        for _ in range(num_bootstrap_samples):
            bootstrap_sample = data.sample(
                n=int(bootstrap_sample_percent * len(data)), replace=True
            )
            try:
                rho, _ = scipy.stats.pearsonr(
                    bootstrap_sample[property],
                    bootstrap_sample[predictor],
                )
            except ValueError:
                print("MINIMUM SIZE OF DATA: ", int(2 / min_percent))
                print("SIZE OF DATA: ", len(data.index))
                sys.exit(1)
            rhos.append(rho)
        interval = scipy.stats.scoreatpercentile(rhos, (2.5, 97.5))
        confidence_intervals_df.iloc[
            i, confidence_intervals_df.columns.get_loc("low")
        ] = interval[0]
        confidence_intervals_df.iloc[
            i, confidence_intervals_df.columns.get_loc("high")
        ] = interval[1]
        # save_confidence_intervals(results_df, property)

    return r, confidence_intervals_df


def means_and_t_test(data: pd.DataFrame, properties: list) -> str:

    # TODO: get a dataframe of the population, and the naturals.
    # Then report the sim, inf, and opt of each natural, followed by the mean natural and the mean population. 


    # vanderklok
    vks_df = data[data["Language"] == 'natural']
    s_mean = np.mean(list(data["simplicity"]))
    i_mean = np.mean(list(data["informativity"]))
    # m_mean = np.mean(list(data["simplicity * informativity"]))
    o_mean = np.mean(list(data["optimality"]))

    # population
    res_sim = scipy.stats.ttest_1samp(vks_df["simplicity"], s_mean)
    res_inf = scipy.stats.ttest_1samp(vks_df["informativity"], i_mean)
    # res_m = scipy.stats.ttest_1samp(vks_df["simplicity * informativity"], m_mean)
    res_o = scipy.stats.ttest_1samp(vks_df["optimality"], o_mean)

    means_data = {
        "simplicity": [vks_df["simplicity"].mean(), s_mean],
        "informativity": [vks_df["informativity"].mean(), i_mean],
        "optimality": [vks_df["optimality"].mean(), o_mean],
    }

    means_data = pd.DataFrame(means_data, index=["natural", "population"])
    print(means_data)

    # report = "{0} natural, {1} total languages\n".format(
    #     len(vks_df.index), len(data.index)
    # )
    # report += "*" * 90 + "\n"
    # report += "T-TEST STATISTICS:\n"
    # report += "simplicity: {:.2f}\n".format(res_sim.statistic)
    # report += "informativity: {:.2f}\n".format(res_inf.statistic)
    # # report += "simplicity * informativity: {:.2f}\n".format(res_m.statistic)
    # report += "pareto optimality: {:.2f}\n".format(res_o.statistic)
    # report += "*" * 90 + "\n"
    # report += "\n"
    # return report


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/analysis.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")


if __name__ == "__main__":
    main()
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

    # Load languages
    langs_fn = configs["file_paths"]["artificial_languages"]
    dom_langs_fn = configs["file_paths"]["dominant_languages"]

    # Load analysis files
    analysis_fns = configs["file_paths"]["analysis"]
    df_fn = analysis_fns["dataframe"]
    plot_fn = analysis_fns["plot"]
    correlations_fn = analysis_fns["correlations"]

    # Load languages
    langs = load_languages(langs_fn)
    dom_langs = load_languages(dom_langs_fn)

    # Plot
    plot = get_modals_plot(langs, dom_langs)
    plot.save(plot_fn, width=10, height=10, dpi=300)

    # Main analysis
    data = get_modals_df(langs)

    # scale complexity and add columns
    maxc = data["complexity"].max()
    data["simplicity"] = 1 - data["complexity"] / maxc
    data["informativity"] = 1 - data["comm_cost"]
    data.to_csv(df_fn)
    print(data[:10])
    print(data[data['Language']=='natural'])

    print("opt max and min")
    print(data["optimality"].max())
    print(data["optimality"].min())

    properties = [
        "simplicity",
        "informativity",
        "optimality",
    ]
    correlations = {
        prop: full_analysis(data=data, predictor="naturalness", property=prop)
        for prop in properties
    }
    for prop, analysis_pair in correlations.items():
        print(f"IFF correlation with {prop}: {analysis_pair[0]}")
        analysis_pair[1].to_csv(
            f"{correlations_fn.replace('property', prop)}", index=False
        )

    means = means_and_t_test(data, properties)
    print(means)
