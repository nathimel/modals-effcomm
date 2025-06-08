"""Script for analyzing the results of the trade-off."""

import hydra
import re
import pandas as pd

from ultk.effcomm.analysis import get_dataframe
from ultk.effcomm.tradeoff import tradeoff

from experiment import Experiment
from misc.file_util import set_seed, get_subdir_fn
# from modals.modal_language import iff, sav, dlsav, deontic_priority, dp_trivial, dp_nontrivial
from modals import modal_language as ml
from omegaconf import DictConfig

from extended_analysis import IBCommCostMeasurer, num_words_complexity, entropy_words

@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    print("Measuring tradeoff ...")

    # Load the experimental data and paths to save results

    df_fn = get_subdir_fn(config, config.filepaths.analysis_subdir, config.filepaths.analysis.data)

    extended_analysis = config.experiment.effcomm.inf.agent_type
    # config.experiment.effcomm.inf.agent_type = "literal" # messes up filepaths

    comm_cost_measure = "comm_cost"
    complexity_measure = "complexity"
    if "ib" in extended_analysis:
        comm_cost_measure = "ib_comm_cost"
    if "_hw" in extended_analysis:
        complexity_measure = "entropy_words"
    if "_num_words" in extended_analysis:
        complexity_measure = "num_words_complexity"

    experiment = Experiment(config)

    # # DEBUG
    # experiment.load_files(["natural_languages"])
    # ib_comm_cost = IBCommCostMeasurer(
    #     experiment.universe, 
    #     utility_func=experiment.utility,
    # ).generate_ib_comm_cost_func()

    # tlingit, = [lang for lang in experiment.natural_languages["languages"] if lang.data["name"] == "Tlingit"]

    # # ib_comm_cost(tlingit)

    # breakpoint()

    # load languages
    print("sampled...")
    experiment.load_files(["artificial_languages"])    
    print("dominant...")
    experiment.load_files(["dominant_languages"])
    print("natural...")
    experiment.load_files(["natural_languages"])

    id_start = experiment.artificial_languages["id_start"]
    sampled_languages = experiment.artificial_languages["languages"]
    dominant_languages = experiment.dominant_languages["languages"]
    natural_languages = experiment.natural_languages["languages"] if experiment.natural_languages is not None else []

    # TODO: removing this uniqueness condition for the comparison w variants

    langs = list(set(sampled_languages + natural_languages + dominant_languages))
    # langs = sampled_languages + natural_languages + dominant_languages

    print(f"{len(langs)} total langs.")

    comp = experiment.complexity_measure
    inf = experiment.informativity_measure

    # Extended analysis
    ib_measurer = IBCommCostMeasurer(
        experiment.universe, 
        utility_func=experiment.utility,
    )
    ib_comm_cost = ib_measurer.generate_ib_comm_cost_func()

    # Get trade-off results
    # TODO: outsource this to config
    properties_to_measure = {
        "complexity": comp,
        "simplicity": lambda lang: None,  # reset simplicity from evol alg exploration
        "informativity": inf,
        "comm_cost": lambda lang: 1 - inf(lang),
        "iff": lambda lang: lang.degree_property(ml.iff),
        "sav": lambda lang: lang.degree_property(ml.sav),
        "dlsav": ml.dlsav,
        "deontic_priority": ml.deontic_priority,
        "dp_trivial": ml.dp_trivial,
        "dp_nontrivial": ml.dp_nontrivial,
        "epistemic_priority": ml.epistemic_priority,
        "circ_priority": ml.circ_priority,
        "dp_restricted": ml.dp_restricted,
        "dp_medium": ml.dp_medium,

        # Extended analysis
        "ib_comm_cost": ib_comm_cost,
        "ib_accuracy": lambda lang: ib_measurer.memory_cap - ib_comm_cost(lang),
        "num_words_complexity": num_words_complexity,
        "entropy_words": entropy_words,
    }

    # breakpoint() # TODO: first lets check ib_comm_cost and num_words_complexity on a single lang

    result = tradeoff(
        languages=langs,
        properties=properties_to_measure,
        x=comm_cost_measure,
        y=complexity_measure,
    )
    dom_langs = result["dominating_languages"]
    langs = result["languages"]

    # breakpoint()

    nat_langs = [lang for lang in langs if lang.natural]

    print("Saving languages...")
    experiment.artificial_languages = {"languages": langs, "id_start": id_start}
    experiment.dominant_languages = {"languages": dom_langs, "id_start": id_start}
    experiment.natural_languages = {"languages": nat_langs, "id_start": None}
    save_files = [
        "artificial_languages", 
        "dominant_languages",
    ]
    if nat_langs:
        save_files += ["natural_languages"]
    # breakpoint()
    experiment.write_files(save_files)
    print("saved languages.")

    all_data = get_dataframe(
        langs, 
        columns=list(properties_to_measure.keys()) + ["optimality"] # + ["family"]
    )
    all_data["natural"] = [lang.natural for lang in langs]
    all_data["dominant"] = [lang in dom_langs for lang in langs]
    all_data["name"] = [lang.data["name"] for lang in langs]

    # FOR DP ONLY
    # For each of the perturbed variants, record the name of the original natural language
    # get_orig = lambda name: re.sub( r"_variant_\d+", "", name )
    # all_data["original_name"] = [get_orig(lang.data["name"]) for lang in langs]

    all_data.to_csv(df_fn, index=False)
    print("saved df.")


if __name__ == "__main__":
    main()
