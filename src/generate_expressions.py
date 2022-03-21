"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import yaml

def generate_expressions():
    """Short description.
    
    Elaboration.

    Args:

    Returns:
        expressions: a list of Modal_Expressions
    """
    pass

def save_expressions(fn, expressions):
    """Saves the set of all possible modal expressions to a .yml file."""
    with open(fn, 'w') as outfile:
        yaml.dump(expressions, outfile)

def main():
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/build_meaning_space.py path_to_config_file path_to_save_expresions")
        sys.exit(1)
    config_fn = sys.argv[1]
    expression_save_fn = sys.argv[2]


if __name__ == "__main__":
    main()
