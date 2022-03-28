"""Functions for measuring informativity in efficient communication analyses of languages."""

from abc import abstractmethod
from importlib.metadata import distribution
from altk.language.language import Language
from altk.language.language import Expression
from altk.language.semantics import Meaning
from altk.language.semantics import Universe

##############################################################################
# Classes
##############################################################################

class Informativity_Measure:

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

class Communicative_Agent:

    def __init__(self, language: Language):
        """Takes a language to construct a agent to define the relation between meanings and expressions.
        
        By default initialize to uniform communicative need distribution.
        """
        self.set_language(language)
        self.set_communicative_need({point: 1/len(language.get_universe().get_objects()) for point in language.get_universe().get_objects()})

    def uniform_probability_function(self, expression: Expression, meaning: Meaning):
        """A map from meanings to expressions: the expression a speaker sends to communicate the meaning.
        
        Assume the probability of each expressible meaning point in an expression is equal.

        Args:
            - expression: 

            - meaning: 
        """
        can_express = expression.get_meaning().get_objects()
        if meaning in can_express:
            return 1/len(can_express)
        else:
            return 0

    def set_language(self, language: Language):
        self.__language = language
    def get_language(self):
        return self.__language

    def set_distribution(self, dist: dict):
        self.__distribution = dist
    def get_distribution(self):
        return self.__distribution
    distribution=property(get_distribution, set_distribution)

    def set_communicative_need(self, distribution: dict):
        self.__communicative_need = distribution
    def get_communicative_need(self):
        return self.__communicative_need

class Sender(Communicative_Agent):

    def __init__(self, language: Language):
        super().__init__(language)

    # given an intended meaning, return a distribution over expressions
    def probability_of_expression(meaning: Meaning):
        """A distribution over expressions. 
        
        Given an expression the Receiver heard, the probability of a meaning.

        Args:
            - meaning: 

        Return: 
            - distribution: a distribution over expressions.
        """
        pass

class Receiver(Communicative_Agent):

    def __init__(self, language: Language):
        super().__init__(language)

    def probability_of_meaning(expression: Expression) -> dict:
        """A distribution over meanings. 
        
        Given an expression the Receiver heard, the probability of a meaning.

        Args:
            - expression: 

        Return: 
            - distribution: a distribution over meanings.
        """
        pass

##############################################################################
# Functions
##############################################################################

def communicative_success(
    meanings: list[Meaning], 
    expressions: list[Expression], 
    speaker: Sender, 
    listener: Receiver,
    prior: dict,
    utility
    ) -> float:
    """Helper function to compute the informativity of a language.

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$

    Args:
        - meanings: set M, all meaning points sender/receiver can entertain.

        - expressions: the list of expressions in the language, L

        - speaker: an encoder-like object, representing a map from meanings to expressions

        - listener: an decoder-like object, representing map from expressions to meanings

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
        raise ValueError("communicative success must be in [0,1].")
    return success    