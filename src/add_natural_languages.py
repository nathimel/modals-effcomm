"""Script for extracting natural language modals data and adding to efficient communication experiment."""

import hydra
import os
import sys
import yaml
from typing import Any
import pandas as pd

from experiment import Experiment
from misc.file_util import set_seed, get_original_fp
from omegaconf import DictConfig
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_meaning import ModalMeaning, ModalMeaningPoint

ALLOWED_REFERENCE_TYPES = ["paper-journal", "elicitation"]
REFERENCE_GRAMMAR = "reference-grammar"
REFERENCE_TYPES = [REFERENCE_GRAMMAR] + ALLOWED_REFERENCE_TYPES
REFERENCE_TYPE_KEY = "Reference-type"
LANGUAGE_IS_COMPLETE_KEY = "Complete-language"
FAMILY_KEY = "Family"

METADATA_FN = "metadata.yml"
MODALS_FN = "modals.csv"


def process_can_express(val: Any, can_express: dict):
    """For an observation of whether a modal can_express a force-flavor pair, interpret ? as 1.

    Note that the existence of ? in the csv confuses pandas, and causes the type of can_express to be str.

    Args:
        val: the value of the can_express column, possibly an int or str

    Returns:
        boolean representing 'yes' if the value should be interpreted as True, False otherwise
    """
    if isinstance(val, int):
        return val
    if val.isnumeric():
        return bool(int(val))

    # different results depending on interpretation of '?'
    if val in can_express[True]:
        return True
    return False


# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python3 src/add_natural_languages.py path_to_config_file")
#         raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    ##########################################################################
    # Load in languages from cloned database
    ##########################################################################

    language_data_dir = get_original_fp(config.filepaths.typological_data)
    dirs = [
        x
        for x in os.listdir(language_data_dir)
        if os.path.isdir(os.path.join(language_data_dir, x))
    ]


    dataframes = dict()
    for dir in dirs:
        # Ensure that is one of allowed reference types
        dirpath = os.path.join(language_data_dir, dir)
        metadata_path = os.path.join(dirpath, METADATA_FN)

        with open(metadata_path, "r") as stream:
            metadata = yaml.safe_load(stream) # dict

        reference_type = metadata[REFERENCE_TYPE_KEY]
        # must be paper-journal or elicitation
        if reference_type in ALLOWED_REFERENCE_TYPES:
                modals_fn = os.path.join(dirpath, MODALS_FN)
                if FAMILY_KEY not in metadata:
                    pass
                    # breakpoint()
                data = {
                    "df": pd.read_csv(modals_fn),
                    # "family": metadata[FAMILY_KEY],
                }
                dataframes[dir] = data
        else:
            # Skip reference-grammar obtained data if incomplete.
            print(f"Data for {dir} is of type {reference_type}; skipping.")

    ##########################################################################
    # Convert DataFrames to ModalLanguages
    ##########################################################################

    # Load possible expressions and meaning space to map natural vocabularies into
    experiment = Experiment(config, load_files=["expressions"])
    expressions = experiment.expressions
    universe = experiment.universe

    # Construct ModalLanguages for each natural language
    experiment_languages = []
    for language_name, data_dict in dataframes.items():
        print(f"Adding {language_name}")
        vocabulary = {}

        df = data_dict["df"]
        # family = data_dict["family"]
        # only look at positive polarity modals
        if "polarity" in df:
            df_positive = df[df["polarity"] == "positive"]
        else:
            df_positive = df

        # add each observation
        for _, row in df_positive.iterrows():
            modal = row["expression"]
            # initialize an expression's set of meanings
            if modal not in vocabulary:
                vocabulary[modal] = set()

            # Add only the flavors specified as possible for the experiment
            if (
                row["flavor"] in universe.flavors
                and row["force"] in universe.forces
            ):
                if process_can_express(row["can_express"], config.typology.can_express):
                    observation = f"{row['force']}+{row['flavor']}"
                    vocabulary[modal].add(observation)

        # Convert vocabulary into list of ModalExpressions
        experiment_vocabulary = []
        for modal in vocabulary:
            form = modal
            meaning = ModalMeaning(
                points=tuple(
                    ModalMeaningPoint.from_yaml_rep(name) for name in vocabulary[modal]
                ),
                meaning_space=universe,
            )
            if not meaning.referents: # often there will be no usable referents due to can_express being False, above
                continue
            # search for a matching recorded meaning to reuse LoT solutions
            for expression in expressions:
                if expression.meaning == meaning:
                    experiment_modal = ModalExpression(
                        form, meaning, expression.lot_expression
                    )
                    experiment_vocabulary.append(experiment_modal)
                    break
        
        if experiment_vocabulary:
            lang = ModalLanguage(expressions=experiment_vocabulary, name=language_name)
            lang.natural = True
            # lang.data["family"] = family
            experiment_languages.append(lang)

    # save for analysis
    experiment.natural_languages = {"languages": experiment_languages, "id_start": None}
    experiment.write_files(["natural_languages"], kinds=["natural"])


if __name__ == "__main__":
    main()
