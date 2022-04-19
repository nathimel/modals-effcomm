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

    def set_language(self, language: Language):
        self._language = language
    def get_language(self) -> Language:
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
    def probability_of_expression_given_meaning(self, expression: Expression, meaning: Meaning) -> float:
        """Return the conditional probability of an speaker choosing an expression, given their intended meaning."""
        raise NotImplementedError

class Listener(Communicative_Agent):

    def __init__(self, language: Language):
        super().__init__(language)

    def probability_of_meaning_given_expression(self, meaning: Meaning, expression: Expression) -> float:
       """Return the conditional probability of an listener interpreting an expression as a specific meaning."""
       raise NotImplementedError

"""In the RSA framework, communicative agents reason recursively about each other's literal and pragmatic interpretations of utterances."""

class LiteralSpeaker(Speaker):

    def __init__(self, language: Language):
        super().__init__(language)
        # initialize uniform distribution
        self.dist = self.uniform()

    def uniform(self) -> dict[dict]:
        """Assume that for a particular meaning, every expression that can denote it is equiprobable.
        
        Args:
            meaning: the object that can be expressed by n>=0 expressions.
        
        Returns:
            a dict representing the distribution over expressions.
        """
        # initialize conditional probability function as dict of dicts to 0s
        dist = {
            meaning: {
                expression: 0
                for expression in self.get_language().get_expressions()
            }
            for meaning in self.get_language().get_universe().get_objects()
        }

        # uniform if the expression can express the meaning
        for m in dist:
            total = sum(e.can_express(m) for e in dist[m])
            if total:
                for e in dist[m]:
                    if e.can_express(m):
                        dist[m][e] = 1/total
        
        return dist

    def probability_of_expression_given_meaning(self, expression: Expression, meaning: Meaning) -> float:
        # P(expression | meaning)
        return self.dist[meaning][expression]

class LiteralListener(Listener):
    """A naive literal listener interprets utterances without any reasoning about other agents. """

    def __init__(self, language: Language):
        super().__init__(language)
        # initialize uniform distribution
        self.dist = self.uniform()
    
    def uniform(self) -> dict[dict]:
        """Assume the probability of each expressible meaning point in an expression is equal. All inexpressible meanings have probability 0.
        
        Args:
            expression: the expression for which to generate a distribution.
        
        Returns:
            a dict representing the distribution over meanings.
        """
        # initialize conditional probability function as dict of dicts
        dist = {
            expression: {
                meaning: 0
               for meaning in self.get_language().get_universe().get_objects()
               }
           for expression in self.get_language().get_expressions()
        }

        # uniform if the expression can express the meaning
        for e in dist:
            total = sum(e.can_express(m) for m in dist[e])
            if total:
                for m in dist[e]:
                    if e.can_express(m):
                        dist[e][m] = 1/total

        return dist

    def probability_of_meaning_given_expression(self, meaning: Meaning, expression: Expression) -> float:
        # P(meaning | expression)
        return self.dist[expression][meaning]

class PragmaticSpeaker(LiteralListener):
    """A pragmatic speaker chooses utterances based on how a naive, literal listener would interpret them."""

    def __init__(self, language: Language):
        super().__init__(language)

class PragmaticListener(PragmaticSpeaker):
    """A pragmatic listener interprets utterances based on their expectations about a pragmatic speaker's decisions."""
    
    def __init__(self, language: Language):
        super().__init__(language)