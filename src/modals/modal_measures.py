"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_language_of_thought import ExpressionTree, ModalLOT
from modals.modal_meaning import ModalMeaningPoint

from ultk.language.grammar import Grammar, GrammaticalExpression

##############################################################################
# Complexity measure for modals
##############################################################################

"""Defines the complexity measures for measuring modals as minimum description length in a modal language of thought.
"""


# def language_complexity(language: ModalLanguage, mlot: ModalLOT) -> float:
#     """Sum of the language's item complexities."""
#     return sum([item_complexity(e, mlot) for e in language.expressions])

# Helper function because _len_ of GrammaticalExpression is not the number of atoms.
def num_atoms(expression: GrammaticalExpression) -> int:

    if expression.rule_name in ["and", "or", "not"]:
        length = 0
    else:
        length = 1

    if expression.children is not None:
        length += sum(len(child) for child in expression.children)
    return length    


# TODO: this is so hacky, clean it up
def language_complexity(language: ModalLanguage, mlot: ModalLOT, grammar: Grammar, config) -> float:
    """Sum of all the language's item's (prerecorded) complexitites."""
    if config.experiment.lot_estimation == 'ultk':
        return sum([num_atoms(grammar.parse(e.lot_expression)) for e in language.expressions])
    elif config.experiment.lot_estimation == 'homebuilt':
        return sum([item_complexity(e, mlot) for e in language.expressions])


def item_complexity(item: ModalExpression, mlot: ModalLOT) -> int:
    """Measure the complexity of a single item."""
    return mlot.expression_complexity(ExpressionTree.from_string(item.lot_expression))

