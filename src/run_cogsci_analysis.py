import argparse
import sys
import pandas as pd
import plotnine as pn
from altk.effcomm.tradeoff import interpolate_data
from altk.effcomm.analysis import (
    get_dataframe,
    pearson_analysis,
    trade_off_means,
    trade_off_ttest,
)
from misc.file_util import load_languages, load_configs, set_seed
from modals.modal_language import uegaki

def main(args):

    prefix = "/Users/nathanielimel/clms/projects/modals-effcomm/"

    config_fn = prefix + "configs/cogsci/base.yml"
    configs = load_configs(config_fn)
    set_seed(configs["random_seed"])
    # tell pandas to output all columns
    pd.set_option("display.max_columns", None)


    folder = f"weighted_utility_linear_search/ratio={args.ratio}"

    langs_fn = f"/Users/nathanielimel/clms/projects/modals-effcomm/outputs/cogsci/base/{folder}/sampled.yml"
    dom_langs_fn = f"/Users/nathanielimel/clms/projects/modals-effcomm/outputs/cogsci/base/{folder}/dominant.yml"

    print("Loading languages...")
    result_sampled = load_languages(langs_fn)
    result_dominant = load_languages(dom_langs_fn)
    langs = result_sampled["languages"]
    dom_langs = result_dominant["languages"]
    print("done.")


    # Record all observations, including duplicates, for statistical analyses
    subset = ["complexity", "comm_cost"]
    kwargs = {"subset": subset, "duplicates": "leave"}

    data = get_dataframe(langs, **kwargs)
    pareto_data = get_dataframe(dom_langs, **kwargs)

    naturalness = configs["universal_property"]

    # Add counts only for plot
    plot_data = data.copy()
    vcs = plot_data.value_counts(subset=subset, sort=False)
    plot_data = data.drop_duplicates(subset=subset)  # drop dupes from original
    plot_data = plot_data.sort_values(by=subset)
    plot_data["counts"] = vcs.values

    # smooth pareto curve again
    pareto_df = pareto_data[["comm_cost", "complexity"]]
    pareto_points = pareto_df.to_records(index=False).tolist()
    # pareto_points = interpolate_data(pareto_points)
    pareto_smoothed = pd.DataFrame(pareto_points, columns=["comm_cost", "complexity"])    

    # redo plot with "Deontic Priority"

    data["Deontic Priority"] = data["uegaki"]


    kwargs = {}
    kwargs["shape"] = "Deontic Priority"
    kwargs["size"] = "Deontic Priority"
    kwargs["color"] = "Deontic Priority"

    # if counts:
    #     kwargs["size"] = "counts"

    plot = (
        # Set data and the axes
        pn.ggplot(data=data, mapping=pn.aes(x="complexity", y="comm_cost"))
        # + pn.scale_y_continuous(limits=[0, 1])
        + pn.geom_point(  # all langs
            stroke=0,
            alpha=1,
            mapping=pn.aes(**kwargs),
        )
        + pn.geom_line(size=1, data=pareto_smoothed)
        + pn.xlab("Complexity")
        + pn.ylab("Communicative cost")
        # + pn.scale_color_cmap("cividis")
        + pn.theme_classic()
    )


    fn = f"/Users/nathanielimel/clms/projects/modals-effcomm/outputs/cogsci/base/{folder}/plot.png"
    plot.save(filename=fn, width=10, height=10, dpi=300)


    # tradeoff properties
    properties = ["complexity", "comm_cost", "optimality"]

    uegaki_true = data[data["uegaki"] == True]
    uegaki_false = data[data["uegaki"] == False]
    uegaki_true_means = trade_off_means("uegaki_true", uegaki_true, properties)
    uegaki_false_means = trade_off_means("uegaki_false", uegaki_false, properties)

    population_means = trade_off_means("population_means", data, properties)

    means_df = pd.concat([uegaki_true_means, uegaki_false_means, population_means]).set_index("name")

    means_df["N"] = [len(uegaki_true), len(uegaki_false), len(data)]
    means_df.index = ["Deontic Priority true", "Deontic Priority false", "population"]
    print(means_df)

    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    pop_means_dict = population_means.iloc[0].to_dict()
    ttest_uegaki_df = trade_off_ttest(uegaki_true, pop_means_dict, properties)

    means_fn = f"/Users/nathanielimel/clms/projects/modals-effcomm/outputs/cogsci/base/{folder}/means.csv"
    ttest_fn =  f"/Users/nathanielimel/clms/projects/modals-effcomm/outputs/cogsci/base/{folder}/ttest.csv"

    means_df.to_csv(means_fn)
    ttest_uegaki_df.to_csv(ttest_fn)




if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ratio",
        type=int,
        help="ratio of deontic weight corresponding to folder name, e.g. ratio=15"
    )

    args = parser.parse_args()

    main(args)

