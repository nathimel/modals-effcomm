"""Script for analyzing the results of the trade-off."""

import hydra
import pandas as pd

from altk.effcomm.analysis import get_dataframe
from altk.effcomm.tradeoff import tradeoff

from experiment import Experiment
from misc.file_util import set_seed, get_subdir_fn
# from modals.modal_language import iff, sav, dlsav, deontic_priority, dp_trivial, dp_nontrivial
from modals import modal_language as ml
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    print("Measuring tradeoff ...")

    # Load the experimental data and paths to save results

    df_fn = get_subdir_fn(config, config.filepaths.analysis_subdir, config.filepaths.analysis.data)

    experiment = Experiment(config)

    # load languages
    print("sampled...")
    experiment.load_files(["artificial_languages"])    
    # print("dominant...") # these aren't that important
    # experiment.load_files(["dominant_languages"])
    print("natural...")
    experiment.load_files(["natural_languages"])

    id_start = experiment.artificial_languages["id_start"]
    sampled_languages = experiment.artificial_languages["languages"]
    # dominant_languages = experiment.dominant_languages["languages"]
    natural_languages = experiment.natural_languages["languages"] if experiment.natural_languages is not None else []

    langs = list(set(sampled_languages + natural_languages))

    # wataru sanity check
    from modals.modal_language import ModalExpression, ModalLanguage, ModalMeaning, ModalMeaningPoint
    lang1 = ModalLanguage(
        expressions=[
            ModalExpression(
                form=f"wataru_expression_1", 
                meaning=ModalMeaning([
                    ModalMeaningPoint(force="possibility", flavor="epistemic"),
                    ModalMeaningPoint(force="impossibility", flavor="epistemic")
                    ],
                    meaning_space=experiment.universe,
                    ),
                lot_expression="(epistemic )",
            )
        ],
        name="wataru_language_1",
    )
    lang2 = ModalLanguage(
        expressions=[
            ModalExpression(
                form=f"wataru_expression_2", 
                meaning=ModalMeaning([
                    ModalMeaningPoint(force="possibility", flavor="deontic"),
                    ModalMeaningPoint(force="impossibility", flavor="deontic")
                    ],
                    meaning_space=experiment.universe,
                    ),
                lot_expression="(deontic )",
            )
        ],
        name="wataru_language_2",
    )
    langs = langs + [lang1, lang2]

    print(f"{len(langs)} total langs.")

    comp = experiment.complexity_measure
    inf = experiment.informativity_measure

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
    }

    result = tradeoff(
        languages=langs,
        properties=properties_to_measure,
        x="comm_cost",
        y="complexity",
    )
    dom_langs = result["dominating_languages"]
    langs = result["languages"]

    nat_langs = [lang for lang in langs if lang.natural]

    print("Saving languages...")
    experiment.artificial_languages = {"languages": langs, "id_start": id_start}
    experiment.dominant_languages = {"languages": dom_langs, "id_start": id_start}
    experiment.natural_languages = {"languages": nat_langs, "id_start": None}
    save_files = ["artificial_languages", "dominant_languages"]
    kinds = ["explored", "dominant"]
    if nat_langs:
        save_files += ["natural_languages"]
        kinds += ["natural"]
    experiment.write_files(save_files, kinds=kinds)
    print("saved languages.")

    # TODO: store the language.data fields in a common spot for repeat access in a uniform way
    all_data = get_dataframe(
        langs, 
        columns=list(properties_to_measure.keys()) + ["optimality"] # + ["family"]
    )
    # TODO: make this more efficient
    all_data["natural"] = [lang.natural for lang in langs]
    all_data["dominant"] = [lang in dom_langs for lang in langs]
    all_data["name"] = [lang.data["name"] for lang in langs]
    all_data.to_csv(df_fn, index=False)
    print("saved df.")


if __name__ == "__main__":
    main()
