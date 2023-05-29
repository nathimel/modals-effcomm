import sys
import pandas as pd
import plotnine as pn
from altk.effcomm.tradeoff import interpolate_data
from altk.effcomm.analysis import (
    pearson_analysis,
    trade_off_means,
    trade_off_ttest,
)
from misc.file_util import load_configs, set_seed


def get_modals_plot(
    data: pd.DataFrame,
    pareto_data: pd.DataFrame,
    naturalness: str,
    natural_data: pd.DataFrame = None,
    counts=False,
    dlsav=False,
) -> pn.ggplot:
    """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

    Args:
        data: a DataFrame representing all the measurements of a tradeoff.

        pareto_data: a DataFrame representing the measurements of the best solutions to the tradeoff.

        natural_data: a DataFrame representing the measurements of the natural languages.

        counts: whether to add the counts of (complexity, comm_cost) as an aesthetic.

        dlsav: whether to add the categorical DLSAV universal property as an aesthetic.

    Returns:
        plot: a plotnine 2D plot of the trade-off.
    """

    print("NATURAL DATA")
    print(natural_data)

    # smooth pareto curve again
    # pareto_df = pareto_data[["comm_cost", "complexity"]]
    # pareto_points = pareto_df.to_records(index=False).tolist()
    # pareto_points = interpolate_data(pareto_points)
    # pareto_smoothed = pd.DataFrame(pareto_points, columns=["comm_cost", "complexity"])

    # aesthetics for all data
    kwargs = {
        "color": naturalness,
    }

    if dlsav:
        kwargs["shape"] = dlsav
        kwargs["size"] = dlsav

    if counts:
        kwargs["size"] = "counts"

    plot = (
        # Set data and the axes
        pn.ggplot(mapping=pn.aes(x="complexity", y="comm_cost"))
        + pn.scale_y_continuous(limits=[0, 1])
        + pn.geom_point(data=pareto_data)
        + pn.geom_point(  # all langs
            data=data,
            stroke=0,
            alpha=1,
            mapping=pn.aes(**kwargs),
        )
        + pn.xlab("Complexity")
        + pn.ylab("Communicative cost")
        + pn.scale_color_cmap("cividis")
        + pn.theme_classic()
    )
    if natural_data is not None:
        plot = (
            plot
            + pn.geom_point(  # The natural languages
                natural_data,
                color="red",
                shape="+",
                size=4,
            )
            + pn.geom_text(
                natural_data,
                pn.aes(label="name"),
                ha="left",
                size=6,  # orig 9
                nudge_x=1,
            )
        )
    return plot


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

    # Load analysis files
    analysis_fns = configs["file_paths"]["analysis"]
    df_fn = analysis_fns["data"]
    pareto_df_fn = analysis_fns["pareto_data"]
    plot_fn = analysis_fns["plot"]
    correlations_fn = analysis_fns["correlations"]
    means_fn = analysis_fns["means"]
    ttest_natural_fn = analysis_fns["ttest_natural"]
    ttest_dlsav_fn = analysis_fns["ttest_dlsav"]

    ############################################################################
    # Fetch main dataframe and plot
    ############################################################################

    # Record all observations, including duplicates, for statistical analyses
    data = pd.read_csv(df_fn)
    pareto_data = data[data["dominant"] == True]
    natural_data = data[data["natural"] == True]

    print("Excluding Thai from final analysis.")
    natural_data = natural_data[natural_data["name"] != "Thai"]

    # Plot
    naturalness = configs["universal_property"]

    # Add counts only for plot
    plot_data = data.copy()
    subset = ["complexity", "comm_cost"]
    vcs = plot_data.value_counts(subset=subset, sort=False)
    plot_data = data.drop_duplicates(subset=subset)  # drop dupes from original
    plot_data = plot_data.sort_values(by=subset)
    plot_data["counts"] = vcs.values

    plot = get_modals_plot(
        data=plot_data,
        pareto_data=pareto_data,
        natural_data=natural_data,
        naturalness=naturalness,
        counts=True,
    )
    plot.save(plot_fn, width=10, height=10, dpi=300)

    ############################################################################
    # Statistics
    ############################################################################

    # scale complexity to measure simplicity
    max_complexity = data["complexity"].max()
    simplicity = lambda x: 1 - (x["complexity"] / max_complexity)
    data["simplicity"] = simplicity(data)
    natural_data["simplicity"] = simplicity(natural_data)

    # tradeoff properties
    properties = ["simplicity", "informativity", "optimality"]

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
    dlsav_data = data[data["dlsav"] == True]
    dlsav_means = trade_off_means("dlsav_means", dlsav_data, properties)
    natural_means = trade_off_means("natural_means", natural_data, properties)
    population_means = trade_off_means("population_means", data, properties)
    means_df = pd.concat([natural_means, dlsav_means, population_means]).set_index(
        "name"
    )
    pop_means_dict = population_means.iloc[0].to_dict()
    ttest_natural_df = trade_off_ttest(natural_data, pop_means_dict, properties)
    ttest_dlsav_df = trade_off_ttest(dlsav_data, pop_means_dict, properties)

    ############################################################################
    # Print report to stdout and save
    ############################################################################

    # visualize
    print(f"Degree {naturalness} pearson correlations:")
    [print(f"{prop}: {rho}") for rho, prop in zip(*[rhos, properties])]

    print()
    print("MEANS")
    print(means_df)
    print()

    print("TTEST STATS")
    print(f"natural languages ({len(natural_data)}) against population ({len(data)})")
    print(ttest_natural_df)
    print()
    print(f"dlsav languages ({len(dlsav_data)}) against population ({len(data)})")
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
    pareto_data.to_csv(pareto_df_fn)


if __name__ == "__main__":
    main()
