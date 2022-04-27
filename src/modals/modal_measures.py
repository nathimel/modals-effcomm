"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

from altk.effcomm.complexity import ComplexityMeasure
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_language_of_thought import ExpressionTree, ModalLOT


class ModalComplexityMeasure(ComplexityMeasure):

    """Defines the complexity measures for measuring modals as minimum description length in a modal language of thought. Future work will explore informations rate as complexity measure.
    """

    def __init__(self, mlot: ModalLOT):
        self.mlot = mlot

    def batch_complexity(self, langs: list[ModalLanguage]) -> list[float]:
        return super().batch_complexity(langs)

    def language_complexity(self, language: ModalLanguage) -> float:
        """Sum of the language's item complexities.

        For information-theoretic measures, summing the individual items may not be the correct measure of a language's total complexity. For example, we can also take an average.
        """
        return sum([self.item_complexity(e) for e in language.expressions])

    def item_complexity(self, item: ModalExpression) -> int:
        """Measure the complexity of a single item.

        Necessary when the complexity metric is  minimum description length.
        """
        return self.mlot.expression_complexity(
            ExpressionTree.from_string(item.lot_expression)
        )

##############################################################################
# Utility (reward) functions for informativity measure
##############################################################################

def indicator(m: str, m_: str) -> int:
    """Utility function that rewards only perfect recovery of meaning point m.
    
    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns: 
        an integer, 1 if meaning points are the same and 0 otherwise.
    """
    return int(m == m_)

def half_credit(m: str, m_: str) -> float:
    """Utility function that awards 0.5 credit for each correctly recovered feature (force or flavor) of meaning point m.
    
    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns: 
        an float, either 0, 0.5, or 1.0 corresponding to the fraction of correctly recovered features of the speaker's meaning point.
    """
    intended = m.split("+")
    guess = m_.split("+")
    score = 0.0
    for feature in intended:
        if feature in guess:
            score += 0.5
    return score