"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

import numpy as np

from altk.effcomm.complexity import Complexity_Measure
from altk.effcomm.informativity import Informativity_Measure
from modals.modal_language import Modal_Expression, Modal_Language
from modals.modal_language_of_thought import Modal_Language_of_Thought
from modals.modal_language_of_thought import ExpressionTree
from modals.modal_meaning import Modal_Meaning_Space

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
        return super().language_complexity(language)

    def item_complexity(self, item: Modal_Expression) -> int:
        """Measure the complexity of a single item.

        Necessary when the complexity metric is  minimum description length.
        """
        if self.get_measure() != 'lot':
            raise ValueError("called item complexity for non-LoT-based complexity measure.")
        mlot = self.get_lot()
        return mlot.expression_complexity(
            ExpressionTree.from_string(item.get_lot_expression()))
        

class Modal_Informativity_Measure(Informativity_Measure):

    """Defines the measure of informativeness for a modal language."""

    def __init__(self):
        pass

    def batch_communicative_cost(self, langs: list[Modal_Language]) -> list[float]:
        return super().batch_communicative_cost(langs)

    def batch_informativity(self, langs: list[Modal_Language]) -> list[float]:
        return super().batch_informativity(langs)

    def language_informativity(self, language: Modal_Language) -> float:
        # return super().language_informativity(language)
        return np.random.uniform() # dummy