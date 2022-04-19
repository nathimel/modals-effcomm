"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

import numpy as np

from altk.effcomm.complexity import ComplexityMeasure
from altk.effcomm.informativity import InformativityMeasure
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language_of_thought import ExpressionTree
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_meaning import ModalMeaning
from altk.effcomm.informativity import communicative_success
from altk.effcomm.agent import LiteralListener, LiteralSpeaker

class ModalComplexityMeasure(ComplexityMeasure):

    """Defines the complexity measures for measuring modals.

    Attributes:
        complexity_measure: a string representing the kind of complexity measure. Specified from the configs file. Default is minimum description length in a modal language of thought. Future work will explore informations rate as complexity measure.
    """

    def __init__(self, mlot: ModalLOT=None):
        self.set_lot(mlot)

    def set_lot(self, mlot: ModalLOT):
        """Set the Modal Language of Thought for the complexity measure."""
        self.__mlot = mlot
    def get_lot(self):
        return self.__mlot

    def batch_complexity(self, langs: list[ModalLanguage]) -> list[float]:
        return super().batch_complexity(langs)

    def language_complexity(self, language: ModalLanguage) -> float:
        """Sum of the language's item complexities.
        
        For information-theoretic measures, summing the individual items may not be the correct measure of a language's total complexity. In general we can also consider an average, instead of a sum.
        """
        return sum(
            [self.item_complexity(e) for e in language.get_expressions()]
            )

    def item_complexity(self, item: ModalExpression) -> int:
        """Measure the complexity of a single item.

        Necessary when the complexity metric is  minimum description length.
        """
        mlot = self.get_lot()
        return mlot.expression_complexity(
            ExpressionTree.from_string(item.get_lot_expression()))

class ModalSpeaker(LiteralSpeaker):

    def __init__(self, space: ModalMeaningSpace):
        super().__init__(space)

    def probability_of_expression(self, expression: ModalExpression, meaning: ModalMeaning):
        return self.uniform_probability_function(expression, meaning)

class ModalListener(LiteralListener):

    def __init__(self, space: ModalMeaningSpace):
        super().__init__(space)

    def probability_of_meaning(self, meaning: ModalMeaning, expression: ModalExpression) -> dict:
        return self.uniform_probability_function(expression, meaning)

class ModalInformativityMeasure(InformativityMeasure):

    """Defines the measure of informativeness for a modal language."""

    def __init__(self):
        pass

    def batch_communicative_cost(self, langs: list[ModalLanguage]) -> list[float]:
        return super().batch_communicative_cost(langs)

    def batch_informativity(self, langs: list[ModalLanguage]) -> list[float]:
        return super().batch_informativity(langs)

    def language_informativity(self, language: ModalLanguage) -> float:
        """The informativity of a language is based on the successful communication between a Sender and a Receiver.

        The Sender can be thought of as a conditional distribution over expressions given meanings. The Receiver is likewise a conditional distribution over meanings given expressions. The communicative need, or cognitive source, is a prior probability over meanings representing how frequently agents need to use certain meanings in communication. The utility function represents the similarity, or appropriateness, of the Receiver's guess m' about the Sender's intended meaning m.

        For the case of modals, the informativity of a language $L$ with meaning space $M$ is:

        $I(L) := \sum_{m \in M} p(m) \sum_{i \in L} p(i|m) \sum_{m' \in i} p(m'|i) * u(m, m')$
        """
        if not language.get_expressions():
            raise ValueError("language empty: {}".format(language))

        speaker = ModalSpeaker(language)
        listener = ModalListener(language)
        
        prior = speaker.get_communicative_need()
        utility = lambda m, m_: m == m_

        return communicative_success(
            speaker,
            listener,
            prior,
            utility
            )
