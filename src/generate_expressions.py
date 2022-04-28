"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import ModalExpression
from misc.file_util import load_space, load_configs, save_expressions
from multiprocess import Pool
from tqdm import tqdm


if __name__ == "__main__":
    # Everything must be outside of main() otherwise Pool gets mad
    if len(sys.argv) != 2:
        print("Usage: python3 src/generate_expressions.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    # Load parameters for expression generation
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    meaning_space_fn = configs["file_paths"]["meaning_space"]
    expression_save_fn = configs["file_paths"]["expressions"] #TODO: consider checking if expressions already exist instead of regenerating every time

    # Generate expressions, measure them, and save
    space = load_space(meaning_space_fn)

    print("Generating expressions...")
    mlot = ModalLOT(space, configs["language_of_thought"])
    meanings = [x for x in space.generate_meanings()]

    with Pool(configs["processes"]) as p:
        lot_expressions = list(
            tqdm(p.imap(mlot.minimum_lot_description, meanings), total=len(meanings))
        )

    modal_expressions = [
        ModalExpression(
            form=f"dummy_form_{i}",
            meaning=meaning,
            lot_expression=lot_expressions[i],
        )
        for i, meaning in enumerate(meanings)
    ]

    save_expressions(expression_save_fn, modal_expressions)
    print("done.")
