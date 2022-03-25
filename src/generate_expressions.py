"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

from ast import operator
import sys
import yaml
import itertools
import numpy as np
from modals.modal_meaning import Modal_Meaning_Space
from modals.modal_language_of_thought import Modal_Language_of_Thought
from modals.modal_language import Modal_Expression
from misc.file_util import load_space, load_configs, save_expressions

def generate_expressions(space: Modal_Meaning_Space, configs: dict):
    """Short description.
    
    Generate all possible meanings specified by the modal meaning space. For each meaning find an appropriate form. Store this information in a modal expression.

    Args:
        - space: a Modal Meaning Space constraining the set of possible meanings to generate expressions for.
    Returns:
        - expressions: a list of Modal_Expressions
    """

    mlot = Modal_Language_of_Thought(space, configs['language_of_thought'])
    meanings = [x for x in space.generate_meanings()]
    lot_expressions = mlot.minimum_lot_descriptions(meanings)
    modal_expressions = [
        Modal_Expression(
            form="dummy_form_{}".format(i),
            meaning=meaning,
            lot_expression=lot_expressions[i]
            ) for i, meaning in enumerate(meanings)]
    return modal_expressions


def main():
    if len(sys.argv) != 4:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/generat_expressions.py path_to_config_file path_to_save_meaning_space path_to_save_expresions")
        raise TypeError() #TODO: create an actual error class for the package

    # TODO: probably use tqdm in generate_expressions function
    print("Generating expressions ...", sep=' ')

    config_fn = sys.argv[1]
    meaning_space_fn = sys.argv[2]
    expression_save_fn = sys.argv[3]

    configs = load_configs(config_fn)
    space = load_space(meaning_space_fn)
    expressions = generate_expressions(space, configs)
    save_expressions(expression_save_fn, expressions)

    print("done.")

if __name__ == "__main__":
    main()
