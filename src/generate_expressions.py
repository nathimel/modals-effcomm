"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import ModalExpression
from misc.file_util import load_space, load_configs, save_expressions


def generate_expressions(space: ModalMeaningSpace, configs: dict):
    """Generate and measure complexity of all possible expressions for a meaning space.

    Enumerate all possible meanings specified by the modal meaning space. For each meaning find an appropriate form. Store this information in a modal expression.

    Args:
        - space: a Modal Meaning Space constraining the set of possible meanings to generate expressions for.
    Returns:
        - expressions: a list of Modal_Expressions
    """

    mlot = ModalLOT(space, configs["language_of_thought"])
    meanings = [x for x in space.generate_meanings()]
    lot_expressions = mlot.minimum_lot_descriptions(meanings)
    modal_expressions = [
        ModalExpression(
            form=f"dummy_form_{i}",
            meaning=meaning,
            lot_expression=lot_expressions[i],
        )
        for i, meaning in enumerate(meanings)
    ]
    return modal_expressions


def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/generate_expressions.py path_to_config_file")
        raise TypeError()  # TODO: create an actual error class for the package

    # TODO: probably use tqdm in generate_expressions function
    print("Generating expressions ...", sep=" ")

    # Load parameters for expression generation
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    meaning_space_fn = configs["file_paths"]["meaning_space"]
    expression_save_fn = configs["file_paths"]["expressions"]

    # Generate expressions, measure them, and save
    space = load_space(meaning_space_fn)
    expressions = generate_expressions(space, configs)
    save_expressions(expression_save_fn, expressions)

    print("done.")


if __name__ == "__main__":
    main()
