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

