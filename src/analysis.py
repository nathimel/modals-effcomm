from re import L
import sys
import scipy
import numpy as np
import pandas as pd
import plotnine as pn
from tqdm import tqdm
from altk.effcomm.analysis import get_dataframe
from altk.effcomm.tradeoff import interpolate_data
from misc.file_util import load_languages, load_configs
from modals.modal_language import ModalLanguage
from scipy.stats import ttest_1samp
from typing import Any


def get_modals_df(languages: list[ModalLanguage], repeats=None) -> pd.DataFrame:
    """Get a pandas DataFrame for a list of languages containing efficient communication data.

    Args:
        languages: the list of languages for which to get efficient communication dataframe.

    Returns:
        data: a pandas DataFrame with rows as individual languages, with the columns specifying their
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
            0.0,  # dummy simplicity placeholder
            lang.informativity,
            lang.optimality,
            "natural" if lang.is_natural() else "artificial",
            1.0 - lang.informativity,
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
    data[["simplicity", "comm_cost", "complexity", "naturalness", "optimality"]] = data[
        ["simplicity", "comm_cost", "complexity", "naturalness", "optimality"]
    ].apply(pd.to_numeric)

    data = data.round(3)

    # drop duplicates without counting
    if repeats == 'drop':
        data = data.drop_duplicates(subset=["complexity", "comm_cost"])

    # drop but count duplicates
    elif repeats == 'count':
        vcs = data.value_counts(subset=["complexity", "comm_cost"])
        data = data.drop_duplicates(subset=["complexity", "comm_cost"])
        data = data.sort_values(by=["complexity", "comm_cost"])
        data["counts"] = vcs.values

    elif repeats is not None:
        raise ValueError(f"the argument `repeats' must be either 'drop' or 'count'. Received: {repeats}")

    return data


def get_modals_plot(
    data: pd.DataFrame, pareto_data: pd.DataFrame,
counts=False, ) -> pn.ggplot:
    """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

    Args:
        data: a DataFrame representing all the measurements of a tradeoff.

        pareto_data: a DataFrame representing the measurements of the best solutions to the tradeoff.

    Returns:
        plot: a plotnine 2D plot of the trade-off.
    """
    natural_data = data[data["Language"] == "natural"]

    # smooth pareto curve
    pareto_df = pareto_data[["comm_cost", "complexity"]]
    pareto_df["complexity"] / data["complexity"].max()
    pareto_points = pareto_df.to_records(index=False).tolist()
    pareto_points = interpolate_data(list(set(pareto_points)))
    pareto_smoothed = pd.DataFrame(pareto_points, columns=["comm_cost", "complexity"])

    if counts:
        kwargs = {"color":"naturalness", "size":"counts"}
    else:
        kwargs = {"color":"naturalness"}


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
            shape="x",
            size=4,
        )
        + pn.geom_line(size=1, data=pareto_smoothed)
        + pn.xlab("Communicative cost of languages")
        + pn.ylab("Complexity of languages")
        + pn.scale_color_cmap("cividis")
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

    return {
        "rho": r, 
        "confidence_intervals": confidence_intervals_df
        }


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


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/analysis.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

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
    ttest_fn = analysis_fns["ttest"]

    # Load languages
    langs = load_languages(langs_fn)
    nat_langs = load_languages(nat_langs_fn)
    dom_langs = load_languages(dom_langs_fn)

    # Main analysis
    data = get_modals_df(langs, repeats='drop')
    pareto_data = get_modals_df(dom_langs, repeats='drop')
    natural_data = get_modals_df(nat_langs)
    data = data.append(natural_data)
    print(f"Length of DataFrame: {len(data)}")

    # Plot
    plot = get_modals_plot(data, pareto_data, counts=False)
    plot.save(plot_fn, width=10, height=10, dpi=300)    

    # scale complexity to measure simplicity
    max_complexity = data["complexity"].max()
    simplicity = lambda x: 1 - (x["complexity"] / max_complexity)
    data["simplicity"] = simplicity(data)
    natural_data["simplicity"] = simplicity(natural_data)

    print("Some random sampled data: ")
    print(data[:10])
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
            predictor="naturalness",
            property=prop,         
            )
        rhos.append(d["rho"])
        confidence_intervals.append(d["confidence_intervals"])

    # Means and ttest for natural vs population
    natural_means = trade_off_means("natural_means", natural_data, properties)
    population_means = trade_off_means("population_means", data, properties)
    means_df = pd.concat([natural_means, population_means]).set_index("name")
    ttest_df = trade_off_ttest(natural_data, population_means, properties)

    # visualize
    print("IFF pearson correlations:")
    [
        print(f"{prop}: {rho}")
        for rho, prop in zip(*[rhos, properties])
    ]

    print()
    print("MEANS")
    print(means_df)
    print()

    print("TTEST STATS")
    print(ttest_df)
    print()

    # Save results
    means_df.to_csv(means_fn)
    ttest_df.to_csv(ttest_fn, index=False)
    [intervals.to_csv(
        f"{correlations_fn.replace('property', prop)}", index=False
    ) for prop, intervals in zip(*[properties, confidence_intervals])]
    data.to_csv(df_fn)
    pareto_data.to_csv(pareto_df_fn)


if __name__ == "__main__":
    main()
