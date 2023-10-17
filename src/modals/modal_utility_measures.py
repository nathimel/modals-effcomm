import pandas as pd

from typing import Callable
from modals.modal_meaning import ModalMeaningPoint

##############################################################################
# Utility (reward) functions for informativity measure
##############################################################################

def indicator(m: ModalMeaningPoint, m_: ModalMeaningPoint) -> int:
    """Utility function that rewards only perfect recovery of meaning point m.

    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns:
        an integer, 1 if meaning points are the same and 0 otherwise.
    """
    return int(m == m_)


def half_credit(m: ModalMeaningPoint, m_: ModalMeaningPoint) -> float:
    """Utility function that awards 0.5 credit for each correctly recovered feature (force or flavor) of meaning point m.

    Args:
        m: a string representing the speaker's intended meaning point, e.g. 'weak+epistemic'

        m_: a string representing the listener's guess about m.

    Returns:
        an float, either 0, 0.5, or 1.0 corresponding to the fraction of correctly recovered features of the speaker's meaning point.
    """
    intended = m.name.split("+")
    guess = m_.name.split("+")
    score = 0.
    for feature in intended:
        if feature in guess:
            score += 0.5
    return score

def utility_func_from_csv(
        fn: str, 
        base_util: Callable[[ModalMeaningPoint, ModalMeaningPoint], int] = half_credit) -> Callable[[ModalMeaningPoint, ModalMeaningPoint], int]:
    """Load a utility function from a csv file containing nonnegative weights for modal meaning points. Will be normalized so that the maximum utility is 1.
    
    Args:
        fn: the csv file to read in, which must specify weights for correctly identifying meaning points

        base_util: the 'base' utility function to construct a utility function with.
            if 'half_credit', the utility function is
                u(m, m') \propto w_{m} * [ fo(m) == fo(m') + fl(m) == fl(m') ]
            if 'indicator', the utility function is
                u(m, m') \propto w_{m} * ( m == m' )
    """
    df = pd.read_csv(fn)

    # Normalize weights of flavors in df so maximum is 1.
    weights = {
        (force, flavor):  df.loc[
            (df['force'] == force) & (df['flavor'] == flavor), 
            "weight"
            ].iloc[0]
        for force in set(df.force.values) for flavor in set(df.flavor.values)
    }
    total = max(list(weights.values())) # Heaviest weight is 1.
    weights = {point: weight / total for point, weight in weights.items()}

    def utility(m: ModalMeaningPoint, m_: ModalMeaningPoint) -> float:
        force, flavor = m.name.split("+")

        if base_util == half_credit:
            reward = half_credit(m, m_)
        if base_util == indicator:
            reward = indicator(m, m_)

        # get w_{m}, the weight for the speaker's meaning point
        return weights[(force, flavor)] * reward

    return utility
