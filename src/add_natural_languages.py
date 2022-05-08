"""Script for extracting natural language modals data and adding to efficient communication experiment."""

import sys
from typing import Any
import pandas as pd
from misc.file_util import load_configs, load_expressions
from misc.file_util import load_space, save_languages
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_meaning import ModalMeaning


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
    space_fn = configs['file_paths']["meaning_space"]    
    lang_save_fn = configs["file_paths"]["natural_languages"]

    # Load csv files
    dataframes = {
        language_name: pd.read_csv(configs['file_paths']["data"][language_name])
        for language_name in configs['file_paths']["data"]
    }

    # Load possible expressions and meaning space to map natural vocabularies into
    expressions = load_expressions(expression_save_fn)
    space = load_space(space_fn)

    # Construct ModalLanguages for each natural language
    experiment_languages = []
    for language_name, df in dataframes.items():
        print(f"Adding {language_name}")
        vocabulary = {}
        # add each observation
        for _, row in df.iterrows():
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
            meaning = ModalMeaning(vocabulary[modal], space)
            # search for a matching recorded meaning to reuse LoT solutions
            for expression in expressions:
                if expression.meaning == meaning:
                    experiment_modal = ModalExpression(
                        form, meaning, expression.lot_expression
                    )
                    experiment_vocabulary.append(experiment_modal)
                    break
        experiment_languages.append(ModalLanguage(experiment_vocabulary, language_name))

    # save for analysis
    save_languages(lang_save_fn, experiment_languages, kind='natural')

if __name__ == "__main__":
    main()
