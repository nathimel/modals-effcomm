"""Script for sampling languages."""

"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import numpy as np
from modals.modal_language import Modal_Expression, Modal_Language, is_iff
from misc.file_util import load_configs, load_expressions, save_languages
from altk.effcomm.sampling import Quasi_Natural_Vocabulary_Sampler

def generate_languages(
    expressions: list[Modal_Expression], 
    lang_size: int,
    sample_size: int,
    ) -> list[Modal_Language]:
    """Generate languages by randomly sampling bags of expressions.

    There is nothing to prevent repeat bags from being sampled.

    Args:
        - expressions: a list of the possible modal expressions to sample from

        - configs: the configurations dictionary loaded from .yml file.
    """

    iffs, non_iffs = split_expressions(expressions, is_iff)
    sampler = Quasi_Natural_Vocabulary_Sampler(iffs, non_iffs)
    
    # TODO: use shane's more intelligent sampling alg to get unique langs.

    # Turn the knob on degree-iff
    degrees = np.resize(np.arange(lang_size+1)/lang_size, sample_size)
    langs = []
    for i in range(sample_size):
        bag = sampler.sample_vocabulary(degree=degrees[i], size=lang_size)
        lang = Modal_Language(bag)
        lang.set_name("dummy_lang_{}".format(i))
        langs.append(lang)

    return langs

def split_expressions(expressions, criterion) -> tuple:
    """Split a list of expressions into two groups based on a criterion.

    The criterion is satisfaction with a semantic universal.

    Args:
        - expressions: a list of Modal_Expressions.

        - criterion: a boolean function returning True only if an expression satisfies a criterion, e.g. a semantic universal such as the Independence of Force and Flavors, or Single-Axis of Variability.
    
    Returns: 
        - good: the expressions satisfying the criterion.

        - bad: the expressions not satisfying the criterion.
    """
    good = []
    bad = []
    for x in expressions:
        good.append(x) if criterion(x) else bad.append(x)
    return (good, bad)

def main():
    if len(sys.argv) != 4:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/sample_languages.py path_to_config_file  path_to_save_expresions path_to_save_artificial_languages")
        raise TypeError() #TODO: create an actual error class for the package

    # probably use tqdm above
    print("Sampling languages ...", sep=' ')

    config_fn = sys.argv[1]
    expression_save_fn = sys.argv[2]
    lang_save_fn = sys.argv[3]

    configs = load_configs(config_fn)
    lang_size = configs['lang_size']
    sample_size = configs['sample_size']    

    expressions = load_expressions(expression_save_fn)
    languages = generate_languages(expressions, lang_size, sample_size)
    save_languages(lang_save_fn, languages)

    print("done.")

if __name__ == "__main__":
    main()
