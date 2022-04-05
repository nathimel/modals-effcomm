"""Classes for representing communicative agents, such as Senders and Receivers figuring in Lewis-Skyrms signaling games, or literal and pragmatic agents in the Rational Speech Act framework."""

from altk.language.language import Expression, Language
from altk.language.semantics import Meaning

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
        self._language = language
    def get_language(self):
        return self._language

    def set_distribution(self, dist: dict):
        self._distribution = dist
    def get_distribution(self):
        return self._distribution

    def set_communicative_need(self, distribution: dict):
        self._communicative_need = distribution
    def get_communicative_need(self):
        return self._communicative_need

class Speaker(Communicative_Agent):

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

class Listener(Communicative_Agent):

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


"""In the RSA framework, communicative agents reason recursively about each other's literal and pragmatic interpretations of utterances."""

class LiteralListener(Listener):
    """A naive literal listener interprets utterances without any reasoning about other agents. """

    def __init__(self, language: Language):
        super().__init__(language)

class LiteralSpeaker(Speaker):

    def __init__(self, language: Language):
        super().__init__(language)

class PragmaticSpeaker(LiteralListener):
    """A pragmatic speaker chooses utterances based on how a naive, literal listener would interpret them."""

    def __init__(self, language: Language):
        super().__init__(language)

class PragmaticListener(PragmaticSpeaker):
    """A pragmatic listener interprets utterances based on their expectations about a pragmatic speaker's decisions."""
    
    def __init__(self, language: Language):
        super().__init__(language)