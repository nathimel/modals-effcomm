"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import yaml
from modal_meaning import Modal_Meaning, Modal_Meaning_Point, Modal_Meaning_Space
from modal_expression import Modal_Expression
from file_util import load_modal_meaning_space

def generate_expressions(space: Modal_Meaning_Space):
    """Short description.
    
    Generate all possible meanings specified by the modal meaning space. Then, for each meaning find an appropriate form. Store each of these pairs in a modal expression.

    Args:

    Returns:
        expressions: a list of Modal_Expressions
    """
    dist = {point: 1/space.size() for point in space.get_points()}
    # meaning_example = Modal_Meaning(dist)

def save_expressions(fn, expressions):
    """Saves the set of all possible modal expressions to a .yml file."""
    with open(fn, 'w') as outfile:
        yaml.dump(expressions, outfile)

def main():
    if len(sys.argv) != 4:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/build_meaning_space.py path_to_config_file path_to_save_meaning_space path_to_save_expresions")
        sys.exit(1)
    config_fn = sys.argv[1]
    meaning_space_fn = sys.argv[2]
    expression_save_fn = sys.argv[3]

    mms = load_modal_meaning_space(meaning_space_fn)
    expressions = generate_expressions(mms)
    save_expressions(expression_save_fn, expressions)

if __name__ == "__main__":
    main()
