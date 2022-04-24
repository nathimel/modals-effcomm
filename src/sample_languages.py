"""Script for sampling languages."""

"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
from itertools import combinations
from altk.effcomm.sampling import generate_quasi_natural_sample
from modals.modal_language import ModalExpression, ModalLanguage, is_iff
from misc.file_util import *
from math import comb


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
    # split the expressions based on satisfaction with the semantic universal
    iffs = []
    non_iffs = []
    for x in expressions:
        iffs.append(x) if is_iff(x) else non_iffs.append(x)

    word_amounts = [lang_size] if fixed_wordcount else range(1, lang_size + 1)
    total_word_amount = len(expressions)
    sample_size = int(sample_size / lang_size)

    expressions_indices = [i for i in range(total_word_amount)]
    languages = []

    # For each language size
    for word_amount in word_amounts:

        # If sample size > all possible languages, sample from latter.
        if sample_size > comb(total_word_amount, word_amount):
            subsets = list(combinations(expressions_indices, word_amount))
            print(f"Enumerating {len(subsets)} languages of word amount {word_amount}")

            # Construct the languages
            for subset in subsets:
                bag = [expressions[idx] for idx in subset]
                language = ModalLanguage(
                    bag, name=f"dummy_lang_{len(languages)}"
                )
                languages.append(language)

        # Otherwise, take random sample
        else:
            print(f"Sampling {sample_size} languages of size {word_amount}")
            rlangs = generate_quasi_natural_sample(
                ModalLanguage, iffs, non_iffs, word_amount, sample_size
            )
            languages.extend(rlangs)

    return languages


def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/sample_languages.py path_to_config_file")
        raise TypeError()  # TODO: create an actual error class for the package

    print("Sampling languages ...", sep=" ")

    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs["file_paths"]["expressions"]
    lang_save_fn = configs["file_paths"]["artificial_languages"]

    # Load parameters for languages
    lang_size = configs["lang_size"]
    sample_size = configs["sample_size"]
    set_seed(configs["random_seed"])

    # Turn the knob on iff
    expressions = load_expressions(expression_save_fn)
    languages = generate_languages(expressions, lang_size, sample_size)

    # unique and save langs
    languages = list(set(languages))
    save_languages(lang_save_fn, languages)
    print("done.")


if __name__ == "__main__":
    main()
