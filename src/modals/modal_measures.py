"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

import numpy as np

from altk.effcomm.complexity import Complexity_Measure
from altk.effcomm.informativity import Informativity_Measure
from modals.modal_language import Modal_Expression, Modal_Language
from modals.modal_language_of_thought import Modal_Language_of_Thought
from modals.modal_language_of_thought import ExpressionTree
from modals.modal_meaning import Modal_Meaning_Space
from altk.effcomm.informativity import Receiever, Sender
from modals.modal_meaning import Modal_Meaning

class Modal_Complexity_Measure(Complexity_Measure):

    """Defines the complexity measures for measuring modals.

    Attributes:
        complexity_measure: a string representing the kind of complexity measure. Specified from the configs file. Default is minimum description length in a modal language of thought. Future work will explore informations rate as complexity measure.
    """

    def __init__(self, mlot: Modal_Language_of_Thought=None):
        self.set_lot(mlot)

    def set_lot(self, mlot: Modal_Language_of_Thought):
        """Set the Modal Language of Thought for the complexity measure."""
        self.__mlot = mlot
    def get_lot(self):
        return self.__mlot
    mlot=property(get_lot, set_lot)

    def batch_complexity(self, langs: list[Modal_Language]) -> list[float]:
        return super().batch_complexity(langs)

    def language_complexity(self, language: Modal_Language) -> float:
        """Sum of the language's item complexities.
        
        For information-theoretic measures, summing the individual items may not be the correct measure of a language's total complexity. In general we can also consider an average, instead of a sum.
        """
        return sum(
            [self.item_complexity(e) for e in language.get_expressions()]
            )

    def item_complexity(self, item: Modal_Expression) -> int:
        """Measure the complexity of a single item.

        Necessary when the complexity metric is  minimum description length.
        """
        mlot = self.get_lot()
        return mlot.expression_complexity(
            ExpressionTree.from_string(item.get_lot_expression()))

class Modal_Sender(Sender):

    def __init__(self, space: Modal_Meaning_Space):
        super().__init__(space)

    def probability_of_expression(self, expression: Modal_Expression, meaning: Modal_Meaning):
        return self.uniform_probability_function(expression, meaning)

class Modal_Receiver(Receiever):

    def __init__(self, space: Modal_Meaning_Space):
        super().__init__(space)

    def probability_of_meaning(self, meaning: Modal_Meaning, expression: Modal_Expression) -> dict:
        return self.uniform_probability_function(expression, meaning)

class Modal_Informativity_Measure(Informativity_Measure):

    """Defines the measure of informativeness for a modal language."""

    def __init__(self):
        pass

    def batch_communicative_cost(self, langs: list[Modal_Language]) -> list[float]:
        return super().batch_communicative_cost(langs)

    def batch_informativity(self, langs: list[Modal_Language]) -> list[float]:
        return super().batch_informativity(langs)

    def communicative_success(
        self, 
        meanings: list[Modal_Meaning], 
        expressions: list[Modal_Expression], 
        speaker: Modal_Sender, 
        listener: Modal_Receiver, 
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
        success = []
        for meaning in meanings:
            for expression in expressions:
                # probability a speaker chooses the expression
                speaker_reward = speaker(expression, meaning)

                # probability a listener recovers the meaning
                listener_reward = []
                for meaning_ in expression.get_meaning().get_points():
                    reward = listener(meaning_, expression)
                    reward *= utility(meaning, meaning_)
                    listener_reward.append(reward)
                
                success.append(
                    prior[meaning] * speaker_reward * sum(listener_reward)
                    )

            success = sum(success)
            if success < 0 or success > 1:
                raise ValueError("communicative success must be in [0,1].")
            return success

    def language_informativity(self, language: Modal_Language) -> float:
        """The informativity of a language is based on the successful communication between a Sender and a Receiver.

        The Sender can be thought of as a conditional distribution over expressions given meanings. The Receiver is likewise a conditional distribution over meanings given expressions. The communicative need, or cognitive source, is a prior probability over meanings representing how frequently agents need to use certain meanings in communication. The utility function represents the similarity, or appropriateness, of the Receiver's guess m' about the Sender's intended meaning m.

        For the case of modals, the informativity of a language $L$ with meaning space $M$ is:

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$
        """
        expressions = language.get_expressions()
        space = language.get_meaning_space()
        meanings = space.get_objects()

        speaker = Modal_Sender(language)
        listener = Modal_Receiver(language)
        
        prior = speaker.get_communicative_need()
        utility = lambda m, m_: m == m_

        return self.communicative_success(
            meanings,
            expressions,
            speaker.probability_of_expression,
            listener.probability_of_meaning,
            prior,
            utility
            )
