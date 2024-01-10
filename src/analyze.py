import hydra
import os
import pandas as pd
import plotnine as pn
from ultk.effcomm.tradeoff import interpolate_data
from ultk.effcomm.analysis import (
    pearson_analysis,
    trade_off_means,
    trade_off_ttest,
)
from misc.file_util import set_seed, ensure_dir, get_subdir_fn, get_original_fp
from omegaconf import DictConfig


def get_modals_plot(
    data: pd.DataFrame,
    pareto_data: pd.DataFrame,
    lexeme_property: str = None,
    natural_data: pd.DataFrame = None,
    counts=False,
    axis_titles = True,
    lexicon_property: str = None,
) -> pn.ggplot:
    """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

    Args:
        data: a DataFrame representing all the measurements of a tradeoff.

        pareto_data: a DataFrame representing the measurements of the best solutions to the tradeoff.

        lexeme_property: {'iff', 'sav'}; the lexeme-level universal property to measure as a continuous aesthetic

        natural_data: a DataFrame representing the measurements of the natural languages.

        counts: whether to add the counts of (complexity, comm_cost) as an aesthetic.

        axis_titles: whether to include axis titles. True by default, but pass False to obtain plot for main paper figure.

        lexicon_property: {'dlsav', 'deontic_priority'}; the categorical, language-level universal property to add as a discrete aesthetic

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
        # "color": lexeme_property,
    }

    kwargs["shape"] = lexicon_property
    # kwargs["size"] = lexicon_property
    kwargs["color"] = lexicon_property

    if counts:
        kwargs["size"] = "counts"

    plot = (
        # Set data and the axes
        pn.ggplot(mapping=pn.aes(x="complexity", y="comm_cost"))
        # + pn.scale_y_continuous(limits=[0, 1])
        + pn.geom_line(data=pareto_data)
        + pn.geom_point(  # all langs
            data=data,
            stroke=0,
            # alpha=.5,
            mapping=pn.aes(**kwargs),
            size=4,
        )
        # + pn.scale_color_cmap("cividis")
        + pn.scale_color_discrete()
        + pn.theme_classic()
    )

    if axis_titles:
        plot = (
        plot
        + pn.xlab("Complexity")
        + pn.ylab("Communicative cost")        
        )
    else:
        plot = (
        plot
        + pn.theme(
            axis_title_x=pn.element_blank(),
            axis_title_y=pn.element_blank(),
        )
        )

    # wataru sanity check
    # plot = plot + pn.geom_point(data=df_wataru, size=10, shape="X",)

    if natural_data is not None:
        plot = (
            plot
            + pn.geom_point(  # The natural languages
                data=natural_data,
                # mapping=pn.aes(**kwargs),
                # color="red",
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


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    # tell pandas to output all columns
    pd.set_option("display.max_columns", None)

    ensure_dir(get_original_fp(config.filepaths.analysis_subdir))
    get_analysis_fn = lambda fn: get_subdir_fn(config, config.filepaths.analysis_subdir, fn)

    # Load analysis files
    analysis_fns = config.filepaths.analysis
    df_fn = get_analysis_fn(analysis_fns.data)
    pareto_df_fn = get_analysis_fn(analysis_fns.pareto_data)
    plot_fn = get_analysis_fn(analysis_fns.plot)
    correlations_fn = get_analysis_fn(analysis_fns.correlations)
    means_fn = get_analysis_fn(analysis_fns.means)
    ttest_natural_fn = get_analysis_fn(analysis_fns.ttest_natural)
    ttest_dlsav_fn = get_analysis_fn(analysis_fns.ttest_dlsav)
    ttest_dp_fn = get_analysis_fn(analysis_fns.ttest_dp)

    # TODO: parameterize stat tests and legends, instead of hardcoding dlsav, so we can test deontic_priority

    ############################################################################
    # Fetch main dataframe and plot
    ############################################################################

    # Record all observations, including duplicates, for statistical analyses
    data = pd.read_csv(df_fn)
    pareto_data = data[data["dominant"] == True]
    natural_data = data[data["natural"] == True]

    print("Excluding Thai from final analysis.")
    natural_data = natural_data[natural_data["name"] != "Thai"]

    # TEMP: add a column for which kind of dp is satisfied
    # DP-restricted, DP-nontriial, DP-trivial, and DP-false
    def label_dp(row):
        if row["dp_restricted"] == True:
            return "dp_restricted"
        if row["dp_trivial"] == True:
            return "trivial"
        if row["dp_nontrivial"] == True:
            return "nontrivial"
        if row["deontic_priority"] == False:
            return "false"
    
    dp = data.apply(label_dp, axis=1)
    data["dp"] = dp

    # Plot
    lexeme_property = config.plot.lexeme_property
    lexicon_property = config.plot.lexicon_property

    # lexicon_property = "dp"
    # lexicon_property = "dp_restricted"

    # wataru sanity check
    df_wataru = data[data["name"].isin(["wataru_language_1", "wataru_language_2"])]
    df_wataru["counts"] = 1

    # Add counts only for plot
    plot_data = data.copy()
    subset = ["complexity", "comm_cost"]
    vcs = plot_data.value_counts(subset=subset, sort=False)
    plot_data = data.drop_duplicates(subset=subset)  # drop dupes from original
    plot_data = plot_data.sort_values(by=subset)
    plot_data["counts"] = vcs.values

    plot_data = pd.concat([plot_data, df_wataru])

    plot = get_modals_plot(
        data=plot_data,
        pareto_data=pareto_data,
        natural_data=natural_data,
        lexeme_property=lexeme_property,
        counts=config.plot.counts,
        lexicon_property=lexicon_property,
        # axis_titles=False,
    )
    plot.save(plot_fn, width=10, height=10, dpi=300)
    print(f"Saved plot to {plot_fn}.")

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
            predictor=lexeme_property,
            property=prop,
        )
        rhos.append(d["rho"])
        confidence_intervals.append(d["confidence_intervals"])

    # Means and ttest for natural, dlsav, population
    dlsav_data = data[data["dlsav"] == True]
    dp_data = data[data["deontic_priority"] == True]
    ep_data = data[data["epistemic_priority"] == True]
    cp_data = data[data["circ_priority"] == True]
    dpr_data = data[data["dp_restricted"] == True] 

    dlsav_means = trade_off_means("dlsav_means", dlsav_data, properties)
    dp_means = trade_off_means("deontic_priority_means", dp_data, properties)
    ep_means = trade_off_means("epistemic_priority_means", ep_data, properties)
    cp_means = trade_off_means("circ_priority_means", cp_data, properties)
    dpr_means = trade_off_means("dp_restricted_means", dpr_data, properties)

    natural_means = trade_off_means("natural_means", natural_data, properties)
    population_means = trade_off_means("population_means", data, properties)
    means_df = pd.concat([
        natural_means, 
        dlsav_means, 
        dp_means, 
        ep_means, 
        cp_means, 
        dpr_means, 
        population_means,
    ]).set_index(
        "name"
    )
    pop_means_dict = population_means.iloc[0].to_dict()
    ttest_natural_df = trade_off_ttest(natural_data, pop_means_dict, properties)
    ttest_dlsav_df = trade_off_ttest(dlsav_data, pop_means_dict, properties)
    ttest_dp_df = trade_off_ttest(dp_data, pop_means_dict, properties)
    ttest_ep_df = trade_off_ttest(ep_data, pop_means_dict, properties)
    ttest_cp_df = trade_off_ttest(cp_data, pop_means_dict, properties)
    ttest_dpr_df = trade_off_ttest(dpr_data, pop_means_dict, properties)

    ############################################################################
    # Print report to stdout and save
    ############################################################################

    # visualize
    print(f"Degree {lexeme_property} pearson correlations:")
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
    print(f"deontic priority languages ({len(dp_data)}) against population ({len(data)})")
    print(ttest_dp_df)
    print()    
    print()
    print(f"epistemic priority languages ({len(ep_data)}) against population ({len(data)})")
    print(ttest_ep_df)
    print()        
    print(f"circ priority languages ({len(cp_data)}) against population ({len(data)})")
    print(ttest_cp_df)
    print()
    print(f"deontic priority restricted languages ({len(cp_data)}) against population ({len(data)})")
    print(ttest_cp_df)
    print()    

    # Save results
    means_df.to_csv(means_fn)
    ttest_natural_df.to_csv(ttest_natural_fn)
    ttest_dlsav_df.to_csv(ttest_dlsav_fn)
    ttest_dp_df.to_csv(ttest_dp_fn)
    ensure_dir(os.path.abspath(os.path.join(correlations_fn, os.pardir)))
    [
        intervals.to_csv(f"{correlations_fn.replace('correlation_property', prop)}", index=False)
        for prop, intervals in zip(*[properties, confidence_intervals])
    ]
    pareto_data.to_csv(pareto_df_fn, index=False)
    data.to_csv(df_fn, index=False)


if __name__ == "__main__":
    main()
