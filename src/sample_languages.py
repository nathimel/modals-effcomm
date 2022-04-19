"""Script for sampling languages."""

"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import random
import numpy as np
from tqdm import tqdm
from modals.modal_language import ModalExpression, ModalLanguage, is_iff
from misc.file_util import set_seed, load_configs, load_expressions, save_languages
from altk.effcomm.sampling import Quasi_Natural_Vocabulary_Sampler
from math import comb
from itertools import combinations

def generate_languages(
    expressions: list[ModalExpression], 
    lang_size: int,
    sample_size: int,
    fixed_wordcount=False,
    ) -> list[ModalLanguage]:
    """Generate languages by randomly sampling bags of expressions.

    If sample size <= nCr, then take a random sample_size set of combinations. Otherwise, to prevent repeat languages, treat nCr as the sample size.

    Args:
        - expressions: a list of the possible modal expressions to sample from

        - configs: the configurations dictionary loaded from .yml file.
    """
    iffs, non_iffs = split_expressions(expressions, is_iff)

    word_amounts = [lang_size] if fixed_wordcount else range(1, lang_size+1)
    total_word_amount = len(expressions)
    sample_size = int(sample_size / lang_size)

    expressions_indices = [i for i in range(total_word_amount)]
    languages = []
    
    # For each language size
    for word_amount in word_amounts:

        # If sample size > all possible languages, sample from latter.
        if sample_size > comb(total_word_amount, word_amount):
            subsets = list(combinations(expressions_indices, word_amount))
            print('Enumerating {0} languages of word amount {1}'.format(len(subsets), word_amount))

            # Construct the languages
            for subset in subsets:
                bag = [expressions[idx] for idx in subset]
                language = ModalLanguage(
                    bag, 
                    name="dummy_lang_{}".format(len(languages))
                    )
                languages.append(language)

        # Otherwise, take random sample
        else:
            print('Sampling {0} languages of size {1}'.format(sample_size, word_amount))
            # rlangs = random_combinations(expressions, sample_size, word_amount)
            rlangs = quasi_natural_sample(
                iffs, non_iffs, word_amount, sample_size)
            languages.extend(rlangs)

    return languages

def random_combinations(expressions, sample_size, lang_size):
    """Sample unique languages by generating unique random combinations of expressions.
    
    Args:
        - expressions: the list of total possible expressions to sample from.

    """
    indices_list = []
    pool = tuple(expressions)
    n = len(pool)
    languages = []

    for i in tqdm(range(sample_size)):
        while True:
            indices = sorted(random.sample(range(n), lang_size))
            if indices not in indices_list:
                # keep track of languages chosen
                indices_list.append(indices)

                # Add language
                bag = [pool[idx] for idx in indices]
                language = ModalLanguage(
                    bag,
                    name="dummy_lang_{}".format(len(languages)),
                )
                languages.append(language)
                break
    return languages

def quasi_natural_sample(
    natural_terms, 
    unnatural_terms, 
    lang_size, 
    sample_size):
    """Turn the knob on degree quasi-naturalness for a sample of random combinations languages."""
    indices_list = []
    natural_terms = tuple(natural_terms)
    unnatural_terms = tuple(unnatural_terms)
    languages = []

    # there are lang_size + 1 degrees of naturalness
    samples = np.resize(np.arange(lang_size+1), sample_size)

    for num_natural in samples:
        while True:
            natural_indices = sorted(random.sample(
                range(len(natural_terms)), num_natural))
            unnatural_indices = sorted(random.sample(
                range(len(unnatural_terms)), lang_size - num_natural))
            indices = (natural_indices, unnatural_indices)
            if indices not in indices_list:
                # keep track of languages chosen
                indices_list.append(indices)

                # Add language
                natural_expressions = [natural_terms[idx] for idx in natural_indices]
                unnatural_expressions = [unnatural_terms[idx] for idx in unnatural_indices]
                expressions = natural_expressions + unnatural_expressions

                language = ModalLanguage(
                    expressions,
                    name="dummy_lang_{}".format(len(languages)),
                )
                languages.append(language)
                break
    assert len(languages) == len(set(languages))

    return languages

    
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
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/sample_languages.py path_to_config_file")
        raise TypeError() #TODO: create an actual error class for the package

    print("Sampling languages ...", sep=' ')

    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs['file_paths']['expressions']
    lang_save_fn = configs['file_paths']['artificial_languages']

    # Load parameters for languages
    lang_size = configs['lang_size']
    sample_size = configs['sample_size']
    set_seed(configs['random_seed'])

    # Turn the knob on iff
    expressions = load_expressions(expression_save_fn)
    languages = generate_languages(expressions, lang_size, sample_size)

    # iffs, non_iffs = split_expressions(expressions, is_iff)
    # languages.extend(generate_languages(iffs, lang_size, sample_size))


    save_languages(lang_save_fn, languages)

    print("done.")

if __name__ == "__main__":
    main()
