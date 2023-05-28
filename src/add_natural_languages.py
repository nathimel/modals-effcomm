"""Script for extracting natural language modals data and adding to efficient communication experiment."""

import os
import sys
import yaml
from typing import Any
import pandas as pd
from misc.file_util import load_configs, load_expressions
from misc.file_util import load_space, save_languages
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_meaning import ModalMeaning, ModalMeaningPoint


ALLOWED_REFERENCE_TYPES = ["paper-journal", "elicitation"]
REFERENCE_TYPES = ["reference-grammar"] + ALLOWED_REFERENCE_TYPES
REFERENCE_TYPE_KEY = "Reference-type"

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


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/add_natural_languages.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs["file_paths"]["expressions"]
    space_fn = configs["file_paths"]["meaning_space"]
    lang_save_fn = configs["file_paths"]["natural_languages"]

    ##########################################################################
    # Load in languages from cloned database
    ##########################################################################

    language_data_dir = configs["file_paths"]["data"]
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
            metadata = yaml.safe_load(stream)  # a list of dicts
        
        # Extract reference type dict
        # (reference_type_metadata,) = [
            # d for d in metadata if d == REFERENCE_TYPE_KEY
        # ]
        # reference_type = reference_type_metadata[REFERENCE_TYPE_KEY]
        reference_type = metadata[REFERENCE_TYPE_KEY]

        if reference_type in REFERENCE_TYPES:
            # Add to dataframes, only if paper journal or elicitation. Skip reference-grammar obtained data.
            if reference_type in ALLOWED_REFERENCE_TYPES:
                modals_fn = os.path.join(dirpath, MODALS_FN)
                dataframes[dir] = pd.read_csv(modals_fn)
        else:
            raise ValueError(
                f"The field 'Reference-type' should only contain one of {ALLOWED_REFERENCE_TYPES}. Received: {reference_type}"
            )

    ##########################################################################
    # Convert DataFrames to ModalLanguages
    ##########################################################################

    # Load possible expressions and meaning space to map natural vocabularies into
    expressions = load_expressions(expression_save_fn)
    space = load_space(space_fn)

    # Construct ModalLanguages for each natural language
    experiment_languages = []
    for language_name, df in dataframes.items():
        print(f"Adding {language_name}")
        vocabulary = {}

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
                row["flavor"] in configs["flavor_names"]
                and row["force"] in configs["force_names"]
            ):
                if process_can_express(row["can_express"], configs["can_express"]):
                    observation = f"{row['force']}+{row['flavor']}"
                    vocabulary[modal].add(observation)

        # Convert vocabulary into list of ModalExpressions
        experiment_vocabulary = []
        for modal in vocabulary:
            form = modal
            meaning = ModalMeaning(
                points=[
                    ModalMeaningPoint.from_yaml_rep(name) for name in vocabulary[modal]
                ],
                meaning_space=space,
            )
            # search for a matching recorded meaning to reuse LoT solutions
            for expression in expressions:
                if expression.meaning == meaning:
                    experiment_modal = ModalExpression(
                        form, meaning, expression.lot_expression
                    )
                    experiment_vocabulary.append(experiment_modal)
                    break
        lang = ModalLanguage(expressions=experiment_vocabulary, name=language_name)
        lang.natural = True
        experiment_languages.append(lang)

    # save for analysis
    save_languages(lang_save_fn, experiment_languages, id_start=None, kind="natural")


if __name__ == "__main__":
    main()
