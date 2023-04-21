"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_language_of_thought import ExpressionTree, ModalLOT
from modals.modal_meaning import ModalMeaningPoint

##############################################################################
# Complexity measure for modals
##############################################################################

"""Defines the complexity measures for measuring modals as minimum description length in a modal language of thought.
"""


def language_complexity(language: ModalLanguage, mlot: ModalLOT) -> float:
    """Sum of the language's item complexities."""
    return sum([item_complexity(e, mlot) for e in language.expressions])


def item_complexity(item: ModalExpression, mlot: ModalLOT) -> int:
    """Measure the complexity of a single item."""
    return mlot.expression_complexity(ExpressionTree.from_string(item.lot_expression))

