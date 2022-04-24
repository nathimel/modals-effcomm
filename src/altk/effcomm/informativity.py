"""Functions for measuring informativity in efficient communication analyses of languages."""

import sys
import numpy as np
from abc import abstractmethod
from typing import Callable, Iterable
from altk.language.language import Language
from altk.language.semantics import Meaning
from altk.effcomm.agent import Speaker, Listener
from altk.effcomm.agent import LiteralListener, LiteralSpeaker
from altk.language.semantics import Universe

##############################################################################
# Informativity Classes
##############################################################################


class InformativityMeasure:
    def __init__(self):
        raise NotImplementedError()

    def batch_communicative_cost(self, langs: list[Language]) -> list[float]:
        """Measure the (1 - informativity) of a list of languages."""
        return [1 - self.language_informativity(lang) for lang in langs]

    def batch_informativity(self, langs: list[Language]) -> list[float]:
        """Measure the informativity of a list of languages."""
        return [self.language_informativity(lang) for lang in langs]

    @abstractmethod
    def language_informativity(self, language: Language) -> float:
        """Measure the informativity of a single language."""
        pass


class SST_Informativity_Measure(InformativityMeasure):

    """Class for computing the measure of informativeness for a language based on the communicative success of speakers and listeners as described in Steinert-Threlkeld (2021)."""

    def __init__(self, prior: Iterable, utility: np.ndarray, kind="literal"):
        """Initialize the informativity measure with a utility function and prior.

        Args:
            prior: a probability distribution representing communicative need (frequency) for meanings.

            utility: a 2d numpy array of size |meanings| by |meanings|, containing the function representing the usefulness of listener guesses about speaker meanings, e.g. meaning similarity. For exact recovery, specify an identity matrix.

            kind: Whether to measure informativity using literal or pragmatic agents, as canonically described in the Rational Speech Act framework.
        """

        self.prior = prior
        self.utility = utility
        self.kind = kind

    def batch_communicative_cost(self, langs: list[Language]) -> list[float]:
        return super().batch_communicative_cost(langs)

    def batch_informativity(self, langs: list[Language]) -> list[float]:
        return super().batch_informativity(langs)

    def language_informativity(self, language: Language) -> float:
        """The informativity of a language is based on the successful communication between a Sender and a Receiver.

        The Sender can be thought of as a conditional distribution over expressions given meanings. The Receiver is likewise a conditional distribution over meanings given expressions. The communicative need, or cognitive source, is a prior probability over meanings representing how frequently agents need to use certain meanings in communication. The utility function represents the similarity, or appropriateness, of the Receiver's guess m' about the Sender's intended meaning m.

        The informativity of a language $L$ with meaning space $M$ is defined:

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$
        """
        if not language.get_expressions():
            raise ValueError(f"language empty: {language}")

        if self.kind == "literal":
            speaker = LiteralSpeaker(language)
            listener = LiteralListener(language)
        elif self.kind == "pragmatic":
            raise NotImplementedError
        else:
            raise ValueError("kind must be either 'literal' or 'pragmatic.")

        return vectorized_communicative_success(
            speaker, listener, self.prior, self.utility
        )


##############################################################################
# Main and utility functions for informativity calculation
##############################################################################


def uniform_prior(space: Universe) -> np.ndarray:
    """Return a 1-D numpy array of size |space| reprsenting uniform distribution."""
    return np.array(
        [1 / len(space.get_objects()) for _ in range(len(space.get_objects()))]
    )


def indicator(m, m_) -> int:
    """Utility function that rewards only perfect recovery of meanings."""
    return int(m == m_)


def build_utility_matrix(
    space: Universe, utility: Callable[[Meaning, Meaning], float]
) -> np.ndarray:
    """Construct the square matrix specifying the utility function defined for pairs of meanings."""
    return np.array(
        [
            [utility(meaning, meaning_) for meaning_ in space.get_objects()]
            for meaning in space.get_objects()
        ]
    )


def communicative_success(
    speaker: Speaker,
    listener: Listener,
    prior: dict,
    utility: np.ndarray,
) -> float:
    """Helper function to compute the literal informativity of a language.

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$

    Args:
        - speaker: an encoder-like object, representing a map from meanings to expressions. Is a literal speaker in terms of the RSA framework.

        - listener: an decoder-like object, representing map from expressions to meanings. Is a literal listener in terms of the RSA framework.

        - prior: p(m), distribution over meanings representing communicative need

        - utility: a matrix specifying the function u(m, m') representing usefulness of listener guesses about speaker meanings.
    """
    meanings = speaker.get_language().get_universe().get_objects()
    expressions = speaker.get_language().get_expressions()
    meaning_rewards = 0
    for meaning in meanings:
        prob_m = prior[meaning]
        for meaning_ in meanings:
            utility_m_m_pair = utility(meaning, meaning_)
            # compute P(m, m') = sum_expr speaker(expr | m) * listener(m' | expr)
            prob_m_m_pair = 0.0
            for expression in expressions:
                speaker_prob = speaker.probability_of_expression_given_meaning(
                    expression, meaning
                )
                listener_prob = listener.probability_of_meaning_given_expression(
                    meaning_, expression
                )
                prob_m_m_pair += speaker_prob * listener_prob

            reward_m_m_pair = prob_m_m_pair * prob_m * utility_m_m_pair
            meaning_rewards += reward_m_m_pair

    success = meaning_rewards
    if success <= 0 or success > 1:
        [print(e) for e in expressions]
        raise ValueError(
            f"communicative success must be in [0,1]. Communicative success: {success}"
        )
    return success


def vectorized_communicative_success(
    speaker: Speaker,
    listener: Listener,
    prior: np.ndarray,
    utility: np.ndarray,
) -> float:
    """Helper function to compute the literal informativity of a language.

        I(L) = P(m, m') * u(m, m')

             = \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')

             = trace(diag(p)SR)

    Args:
        - speaker: an encoder-like object, containing a matrix S for P(e | m)

        - listener: an decoder-like object, containing a matrix R for P(m | e)

        - prior: p(m), distribution over meanings representing communicative need

        - utility: a function u(m, m') representing similarity of meanings, or pair-wise usefulness of listener guesses about speaker meanings.
    """
    return float(np.trace(np.diag(prior) @ speaker.S @ listener.R * utility))
