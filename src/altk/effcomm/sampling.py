"""Classes and functions for sampling pools of languages.
"""

import numpy as np

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
        self.natural_terms = natural_terms
        self.unnatural_terms = unnatural_terms

    def sample_vocabulary(self, degree: float, size: int, allow_synonymy=True,  nat_dist=None, unnat_dist=None) -> list:
        """Sample a bag of expressions with a specified degree of quasi-naturalness.

        See the documentation for np.random.choice for typical usage errors.

        Args:
            - degree: a float in $[0,1]$ representing the fraction of natural terms to unnatural terms.

            - size: the size of the bag of expressions to sample.

            - allow_synonymy: Whether the sample is with or without replacement. Default is True, meaning the resulting bag of expressions can have repeated objects.

            - nat_dist: optionally specify the distribution over natural expressions.

            - unnat_dist: optionally specify the distribution over unnatural expressions.

        Returns:
            - expressions: the sampled bag of expressions.
        """

        num_nats = int(np.floor(size * degree))
        num_unnats = size - num_nats

        # if allow_synonymy=False and the sample size is greater than the population size
        if not allow_synonymy and num_nats < len(self.natural_terms):
            raise ValueError("Not enough expressions in {0} to construct a {1}-sized language without synonymy.".format('self.natural_terms', num_nats))
        nats = np.random.choice(
            a=self.natural_terms, 
            size=num_nats, 
            p=nat_dist, 
            replace=allow_synonymy
        )

        if not allow_synonymy and num_unnats < len(self.unnatural_terms):
            raise ValueError("Not enough expressions in {0} to construct a {1}-sized language without synonymy.".format('self.unnatural_terms', num_unnats))
        unnats = np.random.choice(
            a=self.unnatural_terms, 
            size=num_unnats, 
            p=unnat_dist, 
            replace=allow_synonymy
        )
        expressions = list(nats) + list(unnats)
        return expressions