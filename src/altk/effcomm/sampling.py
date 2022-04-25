"""Functions for sampling expressions into languages.
"""

import random
import numpy as np
from altk.language.language import Language, Expression
from typing import Type
from tqdm import tqdm


def quasi_natural_sample(
    language_class: Type,
    natural_terms: list[Expression],
    unnatural_terms: list[Expression],
    lang_size,
    sample_size,
) -> list[Language]:
    """Turn the knob on degree quasi-naturalness for a sample of random combinations languages.

    Args:
        natural_terms: expressions satisfying some criteria of quasi-naturalness, e.g, a semantic universal.

        unnatural_terms: expressions not satisfying the criteria.

        lang_size: the exact number of expressions a language must have.

        sample_size: how many languages to sample.

    """
    indices_list = []
    languages = []

    # there are lang_size + 1 degrees of naturalness
    samples = np.resize(np.arange(lang_size + 1), sample_size)

    for num_natural in tqdm(samples):
        while True:
            natural_indices = sorted(
                random.sample(range(len(natural_terms)), num_natural)
            )

            if unnatural_terms:
                unnatural_indices = sorted(
                    random.sample(range(len(unnatural_terms)), lang_size - num_natural)
                )
            else:
                unnatural_indices = []
            indices = (natural_indices, unnatural_indices)
            if indices not in indices_list:
                # keep track of languages chosen
                indices_list.append(indices)

                # Add language
                natural_expressions = [natural_terms[idx] for idx in natural_indices]
                unnatural_expressions = [
                    unnatural_terms[idx] for idx in unnatural_indices
                ]
                expressions = natural_expressions + unnatural_expressions

                language = language_class(
                    expressions,
                    name=f"dummy_lang_{len(languages)}"
                )
                languages.append(language)
                break
    assert len(languages) == len(set(languages))
    return languages


def random_combinations_sample(
    language_class: Type,
    expressions: list[Expression],
    lang_size,
    sample_size,
) -> list[Language]:
    """Get a sample of random combinations languages for a specific language size.

    Args:
        language_class: a Language class

        expressions: list of expressions to sample from.

        lang_size: the exact number of expressions a language must have.

        sample_size: how many languages to sample.

    Returns:
        a list of languages representing the sample
    """
    indices_list = []
    languages = []

    for i in tqdm(range(sample_size)):
        while True:
            indices = sorted(random.sample(range(len(expressions)), lang_size))
            if indices not in indices_list:
                # keep track of languages chosen
                indices_list.append(indices)

                # add language
                words = [expressions[idx] for idx in indices]
                language = language_class(
                    words,
                    name=f"dummy_lang_{len(languages)}"
                )
                languages.append(language)
                break
    assert len(languages) == len(set(languages))
    return languages
