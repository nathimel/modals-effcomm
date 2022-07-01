import sys
import scipy
import numpy as np
import pandas as pd
import plotnine as pn
from tqdm import tqdm
from altk.effcomm.tradeoff import interpolate_data
from altk.effcomm.analysis import get_dataframe
from misc.file_util import load_languages, load_configs, set_seed
from modals.modal_language import ModalLanguage
from scipy.stats import ttest_1samp
from typing import Any

def get_modals_plot(
    data: pd.DataFrame,
    pareto_data: pd.DataFrame,
    naturalness="iff",
    counts=False,
) -> pn.ggplot:
    """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

    Args:
        data: a DataFrame representing all the measurements of a tradeoff.

        pareto_data: a DataFrame representing the measurements of the best solutions to the tradeoff.

    Returns:
        plot: a plotnine 2D plot of the trade-off.
    """
    natural_data = data[data["Language"] == "natural"]

    # smooth pareto curve again
    pareto_df = pareto_data[["comm_cost", "complexity"]]
    pareto_points = pareto_df.to_records(index=False).tolist()
    pareto_points = interpolate_data(pareto_points)
    pareto_smoothed = pd.DataFrame(pareto_points, columns=["comm_cost", "complexity"])

    kwargs = {
        "color": naturalness, 
        "shape": "dlsav", 
        "size": "dlsav",
    }
    if counts:
        kwargs["size"] = "counts"

    plot = (
        pn.ggplot(data=data, mapping=pn.aes(x="comm_cost", y="complexity"))
        + pn.scale_x_continuous(limits=[0, 1])
        + pn.geom_point(  # all langs
            stroke=0,
            alpha=1,
            mapping=pn.aes(**kwargs),
        )
        + pn.geom_point(  # The natural languages
            natural_data,
            color="red",
            shape="+",
            size=4,
        )
        + pn.geom_text(natural_data, pn.aes(label="name"), ha="left", size=9, nudge_x=1)
        + pn.geom_line(size=1, data=pareto_smoothed)
        + pn.xlab("Communicative cost")
        + pn.ylab("Complexity")
        + pn.scale_color_cmap("cividis")
        # + pn.theme_classic()
    )
    return plot


def pearson_analysis(
    data, predictor: str, property: str, num_bootstrap_samples=100
) -> dict[str, Any]:
    """Measures pearson correlation coefficient for naturalness with a property.

    Use nonparametric bootstrap for confidence intervals.

    Args:
        data: a DataFrame representing the pool of measured languages

        predictor: a string representing the column to measure pearson r with

        property: a string representing a column to measure pearson r with the predictor column

        num_bootstrap_samples: how many samples to bootstrap from the original data
    """
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
                assert False
            rhos.append(rho)
        interval = scipy.stats.scoreatpercentile(rhos, (2.5, 97.5))
        confidence_intervals_df.iloc[
            i, confidence_intervals_df.columns.get_loc("low")
        ] = interval[0]
        confidence_intervals_df.iloc[
            i, confidence_intervals_df.columns.get_loc("high")
        ] = interval[1]

    return {"rho": r, "confidence_intervals": confidence_intervals_df}


def trade_off_means(name: str, df: pd.DataFrame, properties: list) -> pd.DataFrame:
    """Get a dataframe with the population and natural mean tradeoff data."""
    means_dict = {prop: [df[prop].mean()] for prop in properties} | {"name": name}
    means_df = pd.DataFrame(data=means_dict)
    return means_df


def trade_off_ttest(
    natural_data: pd.DataFrame, population_means: pd.DataFrame, properties: list
) -> pd.DataFrame:
    """Get a dataframe with the population and natural (mean) t-test results.

    Since the property of 'being a natural language' is categorical, we use a single-samples T test.
    """
    data = {}
    for prop in properties:
        result = ttest_1samp(natural_data[prop], population_means.iloc[0][prop])
        data[prop] = [result.statistic, result.pvalue]

    df = pd.DataFrame(data)
    df["stat"] = ["t-statistic", "Two-sided p-value"]
    return df.set_index("stat")


##############################################################################
# Main driver code
##############################################################################

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/analysis.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    set_seed(configs["random_seed"])
    # tell pandas to output all columns
    pd.set_option("display.max_columns", None)

    # Load languages
    langs_fn = configs["file_paths"]["artificial_languages"]
    nat_langs_fn = configs["file_paths"]["natural_languages"]
    dom_langs_fn = configs["file_paths"]["dominant_languages"]

    # Load analysis files
    analysis_fns = configs["file_paths"]["analysis"]
    df_fn = analysis_fns["data"]
    pareto_df_fn = analysis_fns["pareto_data"]
    plot_fn = analysis_fns["plot"]
    correlations_fn = analysis_fns["correlations"]
    means_fn = analysis_fns["means"]
    ttest_natural_fn = analysis_fns["ttest_natural"]
    ttest_dlsav_fn = analysis_fns["ttest_dlsav"]

    # Load languages
    result_sampled = load_languages(langs_fn)
    result_natural = load_languages(nat_langs_fn)
    result_dominant = load_languages(dom_langs_fn)
    langs, nat_langs, dom_langs = (
        result_sampled["languages"],
        result_natural["languages"],
        result_dominant["languages"],
    )

    # Main analysis
    data = get_dataframe(langs, subset=["complexity", "comm_cost"])
    pareto_data = get_dataframe(dom_langs, subset=["complexity", "comm_cost"])
    natural_data = get_dataframe(nat_langs, subset=["complexity", "comm_cost"])
    data = data.append(natural_data)

    # Plot
    naturalness = configs["universal_property"]
    plot = get_modals_plot(data, pareto_data, naturalness=naturalness, counts=False)
    plot.save(plot_fn, width=10, height=10, dpi=300)

    # scale complexity to measure simplicity
    max_complexity = data["complexity"].max()
    simplicity = lambda x: 1 - (x["complexity"] / max_complexity)
    data["simplicity"] = simplicity(data)
    natural_data["simplicity"] = simplicity(natural_data)

    print("first 10 of sampled data: ")
    print(data.head(10))
    print()

    print("the natural languages")
    print(natural_data)
    print()

    # Run statistics on tradeoff properties
    properties = ["simplicity", "complexity", "informativity", "optimality"]

    # Pearson correlations
    rhos = []
    confidence_intervals = []
    for prop in properties:
        d = pearson_analysis(
            data=data,
            predictor=naturalness,
            property=prop,
        )
        rhos.append(d["rho"])
        confidence_intervals.append(d["confidence_intervals"])

    # Means and ttest for natural, dlsav, population
    dlsav_data = natural_data[natural_data["dlsav"] == True]
    dlsav_means = trade_off_means("dlsav_means", dlsav_data, properties)
    natural_means = trade_off_means("natural_means", natural_data, properties)
    population_means = trade_off_means("population_means", data, properties)
    means_df = pd.concat([natural_means, dlsav_means, population_means]).set_index("name")
    ttest_natural_df = trade_off_ttest(natural_data, population_means, properties)
    ttest_dlsav_df = trade_off_ttest(dlsav_data, population_means, properties)

    # visualize
    print(f"Degree {naturalness} pearson correlations:")
    [print(f"{prop}: {rho}") for rho, prop in zip(*[rhos, properties])]

    print()
    print("MEANS")
    print(means_df)
    print()

    print("TTEST STATS")
    print("natural languages against population")
    print(ttest_natural_df)
    print()
    print("dlsav languages against population")
    print(ttest_dlsav_df)
    print()

    # Save results
    means_df.to_csv(means_fn)
    ttest_natural_df.to_csv(ttest_natural_fn, index=False)
    ttest_dlsav_df.to_csv(ttest_dlsav_fn, index=False)
    [
        intervals.to_csv(f"{correlations_fn.replace('property', prop)}", index=False)
        for prop, intervals in zip(*[properties, confidence_intervals])
    ]
    data.to_csv(df_fn)
    pareto_data.to_csv(pareto_df_fn)


if __name__ == "__main__":
    main()
