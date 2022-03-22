"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import yaml
import itertools
import numpy as np
from modal_meaning import Modal_Meaning, Modal_Meaning_Point, Modal_Meaning_Space
from modal_expression import Modal_Expression
from heuristic import estimate_shortest_lot_expressions
from file_util import load_modal_meaning_space, load_configs

def generate_expressions(space: Modal_Meaning_Space):
    """Short description.
    
    Generate all possible meanings specified by the modal meaning space. Then, for each meaning find an appropriate form. Store each of these pairs in a modal expression.

    Args:
        space: a Modal Meaning Space constraining the set of possible meanings to generate expressions for.
    Returns:
        expressions: a list of Modal_Expressions
    """
    possible_meanings = enumerate_possible_meanings(space)
    forms = estimate_shortest_lot_expressions(possible_meanings)

    return []


def enumerate_possible_meanings(space: Modal_Meaning_Space):
    """Enumerate the possible subsets of the meaning space, 2^|space| total.

    Restrict to the case when the nonzero probability meaning points are equally likely and sum to 1. E.g, if just one meaning point is possible, it has probability 1. This is equivalent to enumerating the bit-arrays, or the powerset of the meaning space.

    Args:
        space: the modal meaning space.

    Returns:
        meanings: a list of the possible modal meanings.
    """
    results = [
        np.array(i) for i in itertools.product([0, 1], repeat=len(space))
        ]
    results = results[1:] # remove the empty meaning
    distributions = [arr/arr.sum() for arr in results]
    meanings = [Modal_Meaning({k:v for k,v in list(zip(space.get_points(), arr))}) for arr in distributions]
    return meanings


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

    configs = load_configs(config_fn)
    mms = load_modal_meaning_space(meaning_space_fn)
    expressions = generate_expressions(configs, mms)
    save_expressions(expression_save_fn, expressions)

if __name__ == "__main__":
    main()
