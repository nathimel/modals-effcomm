"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

from typing import Callable
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

    def __init__(self, mlot):
        self.mlot = mlot

    def batch_complexity(self, langs: list[ModalLanguage]) -> list[float]:
        return super().batch_complexity(langs)

    def language_complexity(self, language: ModalLanguage) -> float:
        """Sum of the language's item complexities.

        For information-theoretic measures, summing the individual items may not be the correct measure of a language's total complexity. For example, we can also take an average.
        """
        return sum([self.item_complexity(e) for e in language.get_expressions()])

    def item_complexity(self, item: ModalExpression) -> int:
        """Measure the complexity of a single item.

        Necessary when the complexity metric is  minimum description length.
        """
        return self.mlot.expression_complexity(
            ExpressionTree.from_string(item.get_lot_expression())
        )
