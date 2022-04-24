"""Classes for representing communicative agents, such as Senders and Receivers figuring in Lewis-Skyrms signaling games, or literal and pragmatic agents in the Rational Speech Act framework."""

import numpy as np
from altk.language.language import Expression, Language
from altk.language.semantics import Meaning


def cond_prob_matrix(language: Language, agent: str) -> np.ndarray:
    """Create and return the matrix representing the conditional distribution relevant to the agent.

    _Sender_
        The distribution P(e | m) represents the probability that a sender (speaker) chooses expression e to communicate her intended meaning m. The row vector S_i represents the distribution over expressions for meaning i.

    _Receiver_
        The distribution P(m | e) represents the probability that a receiver (listener) guesses that the spekaer meant to communicate m using e. The row vector R_i represents the distribution over meanings for expression i.

    Assume that for a particular meaning, every expression that can denote it is equiprobable.

    Args:
        language: an Language from which to define the distributions

        agent: a string, either 'speaker' or 'listener'

    Returns:
        mat: the matrix representing the conditional distribution.
    """
    expressions = tuple(language.get_expressions())
    meanings = tuple(language.get_universe().get_objects())

    len_e = len(expressions)
    len_m = len(meanings)

    mat = np.zeros((len_m, len_e))
    for i, m in enumerate(meanings):
        for j, e in enumerate(expressions):
            mat[i, j] = float(e.can_express(m))

    # The sum of p(e | intended m) must be in [0,1]
    if agent == "speaker":
        for i in range(len_m):
            # Sometimes a language cannot express a particular meaning at all, resulting in a row sum of 0.
            if mat[i].sum():
                mat[i] = mat[i] / mat[i].sum()

    # The sum of p(m | heard e) must be 1
    elif agent == "listener":
        mat = mat.T
        for i in range(len_e):
            # Every expression must have at least one meaning.
            mat[i] = mat[i] / mat[i].sum()

    return mat


class Communicative_Agent:
    def __init__(self, language: Language):
        """Takes a language to construct a agent to define the relation between meanings and expressions.

        By default initialize to uniform communicative need distribution.
        """
        self.set_language(language)
        self.set_communicative_need(
            {
                point: 1 / len(language.get_universe().get_objects())
                for point in language.get_universe().get_objects()
            }
        )

    def set_language(self, language: Language):
        self._language = language

    def get_language(self) -> Language:
        return self._language

    def set_distribution(self, dist: dict[dict]):
        self._distribution = dist

    def get_distribution(self):
        return self._distribution

    def set_communicative_need(self, distribution: dict[dict]):
        self._communicative_need = distribution

    def get_communicative_need(self):
        return self._communicative_need


class Speaker(Communicative_Agent):
    def __init__(self, language: Language):
        super().__init__(language)

    # given an intended meaning, return a distribution over expressions
    def probability_of_expression_given_meaning(
        self, expression: Expression, meaning: Meaning
    ) -> float:
        """Return the conditional probability of an speaker choosing an expression, given their intended meaning."""
        raise NotImplementedError


class Listener(Communicative_Agent):
    def __init__(self, language: Language):
        super().__init__(language)

    def probability_of_meaning_given_expression(
        self, meaning: Meaning, expression: Expression
    ) -> float:
        """Return the conditional probability of an listener interpreting an expression as a specific meaning."""
        raise NotImplementedError


"""In the RSA framework, communicative agents reason recursively about each other's literal and pragmatic interpretations of utterances."""


class LiteralSpeaker(Speaker):
    def __init__(self, language: Language):
        super().__init__(language)
        # initialize uniform distribution
        # self.set_distribution(self.uniform())
        self.S = cond_prob_matrix(language, "speaker")

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
                expression: 0 for expression in self.get_language().get_expressions()
            }
            for meaning in self.get_language().get_universe().get_objects()
        }

        # uniform if the expression can express the meaning
        for m in dist:
            total = sum(e.can_express(m) for e in dist[m])
            if total:
                for e in dist[m]:
                    if e.can_express(m):
                        dist[m][e] = 1 / total

            # make sure not greater than 1
            diff = sum([dist[m][e] for e in dist[m]]) - 1.0
            tolerance = 1e-5
            if diff > tolerance:
                print("over tolerance: ")
                print(sum([dist[m][e] for e in dist[m]]))
                print([dist[m][e] for e in dist[m]])
                assert False

        return dist

    def probability_of_expression_given_meaning(
        self, expression: Expression, meaning: Meaning
    ) -> float:
        # P(expression | meaning)
        return self.get_distribution()[meaning][expression]


class LiteralListener(Listener):
    """A naive literal listener interprets utterances without any reasoning about other agents."""

    def __init__(self, language: Language):
        super().__init__(language)
        # initialize uniform distribution
        # self.set_distribution(self.uniform())
        self.R = cond_prob_matrix(language, "listener")

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
                        dist[e][m] = 1 / total

            # make sure not greater than 1
            diff = sum([dist[e][m] for m in dist[e]]) - 1.0
            tolerance = 1e-5
            if diff > tolerance:
                print("over tolerance: ")
                print(sum([dist[e][m] for m in dist[e]]))
                print([dist[e][m] for m in dist[e]])
                assert False

        return dist

    def probability_of_meaning_given_expression(
        self, meaning: Meaning, expression: Expression
    ) -> float:
        # P(meaning | expression)
        return self.get_distribution()[expression][meaning]


class PragmaticSpeaker(LiteralListener):
    """A pragmatic speaker chooses utterances based on how a naive, literal listener would interpret them."""

    def __init__(self, language: Language):
        super().__init__(language)


class PragmaticListener(PragmaticSpeaker):
    """A pragmatic listener interprets utterances based on their expectations about a pragmatic speaker's decisions."""

    def __init__(self, language: Language):
        super().__init__(language)
