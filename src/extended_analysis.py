"""comparing the results with the original efficiency measures against simple alternative measures of complexity and informativity."""

import numpy as np
from scipy.stats import entropy
from typing import Callable

from ultk.language.semantics import Referent, Universe
from modals.modal_utility_measures import half_credit, indicator, utility_func_from_csv
from ultk.language.language import Language, aggregate_expression_complexity
from ultk.effcomm.agent import LiteralSpeaker, LiteralListener


# broader comparison against other options would help evaluate the importance of specific design choices. One relevant comparison would be to the informativeness measure used in the Information Bottleneck approach (specifically, as it is applied to a discrete meaning space in Zaslavsky, Maldonado, Culbertson 2021).

# say distance is 1 if force or flavor is diff, 2 if both are, then do ye olde distance->similarity->probability pathway

# Probability helpers

def rows_zero_to_uniform(matrix: np.ndarray) -> np.ndarray:
    matrix = matrix.copy()
    row_sums = matrix.sum(axis=1, keepdims=True)
    zero_rows = (row_sums == 0).flatten()
    
    # Fill zero rows with uniform distribution
    matrix[zero_rows] = 1.0 / matrix.shape[1]
    
    return matrix


def distance_to_probability(distance_matrix: np.ndarray) -> np.ndarray:
    # prob(m, m') \propto \exp(- dist(m, m') ). Softmax with temp 1.
    values = np.exp(-distance_matrix)
    probs = values / np.sum(values, axis=1, keepdims=True)
    return probs

def lang_to_encoder(language: Language) -> np.ndarray:
    """Return p(w|m) Simplifying assumption here that p(w) is uniform."""
    pW_M = LiteralSpeaker(language,).normalized_weights()
    # TODO: fill 0 rows to uniform
    pW_M_filled = rows_zero_to_uniform(pW_M)
    return pW_M_filled

def bayes(pY_X: np.ndarray, pX: np.ndarray) -> np.ndarray:
    pXY = pY_X * pX[:, None]
    pY = pY_X.T @ pX
    return np.where(pY > 1e-20, pXY / pY, 1 / pXY.shape[0]).T    

def kl_divergence(p: np.ndarray, q: np.ndarray, axis=None, base=2) -> float:
    return entropy(
        p,
        q,
        axis=axis,
        base=base,
    )

def mutual_info(pXY: np.ndarray) -> float:
    return float(entropy(pXY.sum(axis=0), base=2) + entropy(pXY.sum(axis=1), base=2) - entropy(pXY, base=2, axis=None))


class IBCommCostMeasurer:

    def __init__(
        self, 
        universe: Universe,
        utility_func: Callable[[Referent, Referent], float] = half_credit,
        ):

        self.universe = universe
        self.utility_matrix = np.array(
            [
                [
                    utility_func(m, m_)
                    for m_ in universe.referents
                ]
                for m in universe.referents
            ]
        )
        # self.distances = (1 - self.utility_matrix) * 2
        self.distances = (1 - self.utility_matrix)        
        self.confusion_probs = distance_to_probability(self.distances)
        self.pr = self.universe.prior_numpy()
        self.memory_cap = mutual_info(self.confusion_probs * self.pr[:, None])


    def generate_ib_comm_cost_func(self) -> Callable[[Language], float]:

        def ib_comm_cost(language: Language) -> float:
            """Return D[ p(u|m) || p(u|w) ]."""
            pW_M = lang_to_encoder(language)
            pr = self.pr

            pM_W = bayes(pW_M, pr)
            pU_W = np.sum(self.confusion_probs[None, :, :] * pM_W[:, :, None], axis=1)
            # print(pU_W)
            # breakpoint()
            # alternative: check I(M;U) - I(U;W)
            kl_dist_mat = kl_divergence(
                self.confusion_probs[:, None, :], 
                pU_W[None, :, :],
                axis=2,
            )
            # print(kl_dist_mat)
            # if language.data["name"] == "Tlingit":
                # breakpoint()
            edkl = float( # make sure to cast to float bc yaml hates numpy
                np.sum(pr @ (pW_M * kl_dist_mat))
            )
            # breakpoint()
            return edkl
        
        return ib_comm_cost
        
    


# Complexity

def num_words_complexity(lang: Language) -> int:
    """Get complexity of a language defined as the number of words."""
    return len(lang)

# H(W)
def entropy_words(lang: Language) -> float:
    pW_M = lang_to_encoder(lang)
    pM = lang.universe.prior_numpy()
    pW = pW_M.T @ pM
    hW = float(entropy(pW, base=2))
    # I found very small numerical (1e-16) differences screw up pareto points, so lets round to 5 digits. We report everything in 3 digits anyway
    hW_rounded = round(hW, ndigits=5)
    return hW_rounded