"""Classes and functions for measuring the simplicity and informativeness of modal languages."""

from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_language_of_thought import ExpressionTree, ModalLOT
from modals.modal_meaning import ModalMeaningPoint, ModalMeaningSpace

import numpy as np
from typing import Callable

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


##############################################################################
# Utility (reward) functions for informativity measure
##############################################################################


def indicator(m: ModalMeaningPoint, m_: ModalMeaningPoint, **kwargs) -> int:
    """Utility function that rewards only perfect recovery of meaning point m.

    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns:
        an integer, 1 if meaning points are the same and 0 otherwise.
    """
    return int(m == m_)


def half_credit(m: ModalMeaningPoint, m_: ModalMeaningPoint, **kwargs) -> float:
    """Utility function that awards 0.5 credit for each correctly recovered feature (force or flavor) of meaning point m.

    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns:
        an float, either 0, 0.5, or 1.0 corresponding to the fraction of correctly recovered features of the speaker's meaning point.
    """
    # intended = m.name.split("+")
    # guess = m_.name.split("+")
    intended = m.data
    guess = m_.data
    score = 0.0
    for feature in intended:
        if feature in guess:
            score += 0.5
    return score

def deontic_over_epistemic_utility(m: ModalMeaningPoint, m_: ModalMeaningPoint, weight: float = 2., utility_func: Callable[[ModalMeaningPoint, ModalMeaningPoint], float] = half_credit, space: ModalMeaningSpace = None, **kwargs) -> float:
    """Utility function that awards interpreting m as m_, subject to the constraint that deontic flavors receive more reward than epistemic.

    Args:
        utility_func: {indicator, half_credit} a utility function on modal meanings.

        weight: how much more to weight deontic over epistemic flavors

    We use the following cost function

        u(m, m_) \propto exp( C(m, m_) )
        = C_{force}(force(m), force(m_))  + C_{flavor}(flavor(m), flavor(m_))
        = (1 - u'(...) + C_{>}(...)

    where u' is another pairwise utility function independent of a deontic > epistemic asymmetry, such as half_credit or indicator, and C_{>} encodes the asymmetry:

    C_{>}(.,.) = 
        {
            C1   if flavor(m) = deontic and flavor(m_) = epistemic
            C2   if flavor(m) = epistemic and flavor(m_) = deontic
            u'   otherwise
        }

    And we normalize all pairwise utility values to the range [0,1]. The  Uegaki hypothesis is that C1 is high, and C2 is low.


    Question: why don't you do a grid search of parameters, as richard does?

    That might be a good idea in the end, but for now it still makes sense to do a simple check of this more hard-coded implementation.

    """
    space = kwargs["space"]

    # construct basic matrix using the passed utility_func
    mat = np.array([[utility_func(x, y) for x in space.referents] for y in space.referents])

    x = 1.0
    # re-weight based on deontic > epistemic
    for x in space.referents:
        for y in space.referents:
            _, flavor = x
            _, flavor_ = y
            # encode the costs