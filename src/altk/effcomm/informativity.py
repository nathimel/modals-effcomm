"""Functions for measuring informativity in efficient communication analyses of languages."""

from abc import abstractmethod
from altk.language.language import Language
from altk.language.language import Expression
from altk.language.semantics import Meaning
from altk.effcomm.agent import LiteralListener, LiteralSpeaker

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
        """Measure the informativity of a single language.
        """
        pass
 

##############################################################################
# Functions
##############################################################################

def communicative_success(
    meanings: list[Meaning], 
    expressions: list[Expression], 
    speaker: LiteralSpeaker,
    listener: LiteralListener,
    prior: dict,
    utility
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
    meaning_rewards = 0
    for meaning in meanings:
        meaning_reward = prior[meaning]
        
        speaker_rewards = 0
        # probability a speaker chooses the expression
        for expression in expressions:
            speaker_reward = speaker(expression, meaning)

            # probability a listener recovers the meaning
            listener_reward = 0
            for meaning_ in expression.get_meaning().get_objects():
                reward = listener(meaning_, expression)
                reward *= utility(meaning, meaning_)
                listener_reward += reward
            speaker_reward *= listener_reward
            speaker_rewards += speaker_reward
        meaning_reward *= speaker_rewards
        meaning_rewards += meaning_reward

    success = meaning_rewards
    if success <= 0 or success > 1:
        raise ValueError("communicative success must be in [0,1]. Num expressions: {0}.  Expressions received: {1}".format(len(expressions), expressions))
    return success   