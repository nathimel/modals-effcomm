"""Functions for measuring informativity in efficient communication analyses of languages."""
import sys
from abc import abstractmethod
from typing import Callable
from altk.language.language import Language
from altk.language.semantics import Meaning
from altk.effcomm.agent import Speaker, Listener

##############################################################################
# Classes
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


##############################################################################
# Functions
##############################################################################


def communicative_success(
    # meanings: list[Meaning],
    # expressions: list[Expression],
    speaker: Speaker,
    listener: Listener,
    prior: dict,
    utility: Callable[[Meaning, Meaning], float],
) -> float:
    """Helper function to compute the literal informativity of a language.

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$

    Args:
        - meanings: set M, all meaning points sender/receiver can entertain.

        - expressions: the list of expressions in the language, L

        - speaker: an encoder-like object, representing a map from meanings to expressions. Is a literal speaker in terms of the RSA framework.

        - listener: an decoder-like object, representing map from expressions to meanings. Is a literal listener in terms of the RSA framework.

        - prior: p(m), distribution over meanings representing communicative need

        - utility: a function u(m, m') representing similarity of meanings.
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
