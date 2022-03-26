"""Functions for measuring informativity in efficient communication analyses of languages."""

from abc import abstractmethod
from importlib.metadata import distribution
from altk.language.language import Language
from altk.language.language import Expression
from altk.language.semantics import Meaning
from altk.language.semantics import Universe

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
        can_express = expression.get_meaning().get_points()
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

class Receiever(Communicative_Agent):

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