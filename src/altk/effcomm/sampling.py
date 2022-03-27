"""Classes and functions for sampling pools of languages.
"""

import random
import numpy as np
from tqdm import tqdm
from modals.modal_language import Modal_Language


class Quasi_Natural_Vocabulary_Sampler:

    """For turning the knob on the degree of (quasi) naturalness for a language.
    
    This class is used for sampling expressions into a language.
    """

    def __init__(self, natural_terms, unnatural_terms):
        """
            Args: 
                - natural_terms: expressions satisfying some criteria of quasi-naturalness, e.g, a semantic universal.

                - unnatural_terms: expressions not satisfying the criteria.
        """
        self.natural_terms = tuple(natural_terms)
        self.unnatural_terms = tuple(unnatural_terms)

    def generate_quasi_natural_languages():
        # Turn the knob on degree-iff
        # degrees = np.resize(np.arange(lang_size+1)/lang_size, sample_size)
        pass


    def random_combinations(self, expressions, sample_size, lang_size):
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
                    language = Modal_Language(
                        bag,
                        name="dummy_lang_{}".format(len(languages)),
                    )
                    languages.append(language)
                    break

        assert len(languages) == len(set(languages))

        return languages


    def indices_to_vocabulary(self, indices_natural, indices_unnatural):
        """Construct a mixed vocabulary of natural and unnatural terms."""
        natural_words = [
            self.natural_terms[idx] for idx in indices_natural
            ]
        unnatural_words = [
            self.unnatural_terms[idx] for idx in indices_unnatural
            ]
        return list(natural_words) + list(unnatural_words)
        