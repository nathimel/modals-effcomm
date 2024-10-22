from itertools import product
from typing import Iterable, Callable
import numpy as np
import pandas as pd
from altk.language.semantics import Universe, Meaning, Referent


class ModalMeaningPoint(Referent):
    # def __init__(self, name: str, weight: float = None) -> None:
    def __init__(self, force: str, flavor: str) -> None:
        self.data = (force, flavor)
        self.force = force
        self.flavor = flavor
        super().__init__(self.name)

    @property
    def data(self) -> tuple[str]:
        return self._data

    @data.setter
    def data(self, pair: tuple[str]):
        self._data = pair
        self.name = f"{pair[0]}+{pair[1]}"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, __o: object) -> bool:
        return self.name == __o.name

    @classmethod
    def from_yaml_rep(cls, name: str):
        """Takes a yaml representation and returns the corresponding ModalMeaningPoint

        Args:
            name: the string representation of the force, flavor pair of the form "force+flavor".
        """
        force, flavor = name.split("+")
        return cls(force=force, flavor=flavor)


class ModalMeaningSpace(Universe):
    """Represents the set of possible modal (force, flavor) pairs.

    Attributes:
        points: the raw set of expressible (force, flavor) pairs.

        table: a 2D numpy array representing the table of possible modal variation.

        df: a pandas DataFrame representing the table.

    Example usage:
        points = {'weak+epistemic', 'weak+deontic'}
        space = Modal_Meaning_Space(points)
        space

    """

    def __init__(self, forces: list[str], flavors: list[str]):
        """Construct a meaning space for modals, using two axes of variation.

        A modal meaning space inherits from altk.semantics.Universe, and the set of (force,flavor) pairs is the set of objects in the Universe.

        Args:
            forces: a list of the modal force string names
            flavors: a list of the modal flavor string names
        """
        self.forces = list(forces)
        self.flavors = list(flavors)
        # construct a universe with cartesian product
        super().__init__(
            referents={
                # ModalMeaningPoint(name=f"{force}+{flavor}")
                ModalMeaningPoint(force=force, flavor=flavor)
                for force in forces
                for flavor in flavors
            }
        )
        self.arr = np.zeros((len(forces), len(flavors)))

    def force_to_index(self, force: str):
        """Converts a force name to a table row index.

        Args:
            - force: the name of the modal force
        Returns:
            - index: an integer representing the row of the table of modal variation corresponding to the force passed.

        Example usage:

            space = Modal_Meaning_Space({'weak'}, {'epistemic'})
            space.force_to_index('weak')
            0
        """
        return self.forces.index(force)

    def flavor_to_index(self, flavor: str):
        """Converts a flavor name to a table row index.

        Args:
            - flavor: the name of the modal force
        Returns:
            - index: an integer representing the row of the table of modal variation corresponding to the force passed.

        Example usage:

            space = Modal_Meaning_Space({'weak'}, {'epistemic'})
            space.force_to_index('epistemic')
            0
        """
        return self.flavors.index(flavor)

    def get_df(self) -> pd.DataFrame:
        """Get a pandas DataFrame of the modal table of variation.

        The advantage of using this data structure is that it shows information about both point names and the 2 axes of variability.
        """
        return pd.DataFrame(self.arr, index=self.forces, columns=self.flavors)

    def generate_meanings(self) -> list:
        """Generates all possible subsets of the meaning space."""
        shape = (len(self.forces), len(self.flavors))
        arrs = [
            np.array(i).reshape(shape)
            for i in product([0, 1], repeat=len(self.referents))
        ]
        arrs = arrs[1:]  # remove the empty array meaning to prevent div by 0
        meanings = [ModalMeaning(self.array_to_points(arr), self) for arr in arrs]
        return meanings

    def array_to_points(self, a: np.ndarray) -> set:
        """Converts a numpy array to a set of points.

        Args:
            a: numpy array representing a modal meaning.

        Raises:
            ValueError: if the meaning space doesn't match the array shape.axis 0 (rows) are forces, axis 1 (columns) are flavors.
        """
        if a.shape != (len(self.forces), len(self.flavors)):
            raise ValueError(
                f"The size of the numpy array must match the size of the modal meaning space. a.shape={a.shape}, self.forces={len(self.forces)}, self.flavors={len(self.flavors)}"
            )

        # return {
        #     ModalMeaningPoint(name=f"{self.forces[pair[0]]}+{self.flavors[pair[1]]}")
        #     for pair in np.argwhere(a)
        # }
        return {
            ModalMeaningPoint(force=self.forces[pair[0]], flavor=self.flavors[pair[1]])
            for pair in np.argwhere(a)
        }

    def prior_to_array(
        self,
        prior: dict[str, float],
    ) -> np.ndarray:
        """Given a dict corresponding to a (possibly not normalized) prior distribution over meaning points, return the normalized numpy array.

        Args:
            prior: a dict representing the distribution over meaning points with
                string keys = meaning point names,
                float values = weights e.g. frequencies or probabilities.

        """
        keys = set(prior.keys())
        points = set([point.data for point in self.referents])
        if keys != points:
            raise ValueError(
                f"The set of keys in of dict storing prior over meaning points must be identical to the set of meaning points of the ModalMeaningSpace. keys={prior.keys()}, meaningspace={points}"
            )

        p = np.array([float(prior[point.data]) for point in self.referents])

        if np.any(p < 0):
            raise ValueError(
                "The prior probability distribution over meaning points may not be constructed with negative weights."
            )

        if np.sum(p) == 0:
            raise ValueError(
                "Th prior probability distribution over meaning points may not be constructed with all zero weights."
            )

        # normalize if necessary
        if np.sum(p) != 1:
            p /= p.sum()

        return p

    def __str__(self):
        return str(self.arr)

    def __hash__(self) -> int:
        return hash((tuple(self.forces), tuple(self.flavors)))


class ModalMeaning(Meaning):
    """ "A modal meaning is a distribution over Modal_Meaning_Points it can be used to communicate.

    Attributes:
        points: the (force,flavor) pairs a modal can be used to express. Each point is a string, 'force+flavor'.

    Example usage:

        m = Modal_Meaning({'weak+epistemic'}, space)
    """

    def __init__(
        self,
        points: Iterable[ModalMeaningPoint],
        meaning_space: ModalMeaningSpace,
    ):
        """
        Args:
            points: the points in meaning space that are actually expressed with nonzero probability

            meaning_space: the modal meaning space of all possible points that can be expressed
        """
        super().__init__(referents=points, universe=meaning_space)

    def to_array(self) -> np.ndarray:
        """Converts the set of points to a numpy array.

        Example usage:

            m = Modal_Meaning({'weak+epistemic', 'strong+epistemic', 'weak+deontic'}, space)\n
            m.to_array()
            [[1 1 0],
             [1 0 0]]

        Returns:
            np.ndarray: the array representation of the points instantiated on the modal table of variation, with array elements equal to 1 if the point can be expressed and 0 otherwise.
        """
        a = np.array(self.universe.arr)
        for point in self.referents:
            # force, flavor = point.name.split("+")
            force, flavor = point.data
            indices = (
                self.universe.force_to_index(force),
                self.universe.flavor_to_index(flavor),
            )
            a[indices] = 1
        return a

    def to_df(self):
        """Converts to set of points to a pandas DataFrame.

        Example usage:

            m = Modal_Meaning({'weak+epistemic', 'strong+epistemic', 'weak+deontic'}, space)
            m.to_df()
                    epistemic  deontic  circumstantial
            weak            1        1               0
            strong          1        0               0

        Returns:
            pd.DataFrame: the dataframe representation of the points instantiated on the modal table of variation
        """
        return pd.DataFrame(
            data=self.to_array(),
            index=self.universe.forces,
            columns=self.universe.flavors,
        )

    def __str__(self) -> str:
        return str(self.referents)

    def __hash__(self) -> int:
        return hash(tuple(sorted([point.data for point in self.referents])))

    def __eq__(self, __o: object) -> bool:
        return set(self.referents) == set(__o.referents)

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
    score = 0.0
    for feature in intended:
        if feature in guess:
            score += 0.5
    return score


##############################################################################
# Meaning distributions for Information Bottleneck analysis
##############################################################################
DEFAULT_DECAY = 0.1
DEFAULT_UTILITY = half_credit

def generate_meaning_distributions(
    space: ModalMeaningSpace, 
    decay: float = DEFAULT_DECAY, 
    cost: Callable[[Referent, Referent], float] = lambda x,y: 1 - DEFAULT_UTILITY(x, y),
) -> np.ndarray:
    """Generate a conditional distribution over world states given meanings, $p(u|m)$, for each meaning.

    Args:
        space: the ModalMeaningSpace on which meanings are defined

        decay: a float in [0,1]. controls informativity, by decaying how much probability mass is assigned to perfect recoveries. As decay approaches 0, only perfect recovery is rewarded (which overrides any partial credit structure built into the utility/cost function). As decay approaches 1, the worst guesses become most likely.

        cost: a cost function defining the pairwise communicative cost for confusing one Referent in the Universe with another. If you have a (scaled) communicative utility matrix, a natural choice for cost might be `lambda x, y: 1 - utility(x, y)`.

    Returns:
        p_u_m: an array of shape `(|space.referents|, |space.referents|)`
    """

    # construct p(u|m) for each meaning
    meaning_distributions = np.array(
        [[decay ** cost(m, u) for u in space.referents] for m in space.referents]
    )
    # each row sums to 1.0
    np.seterr(divide="ignore", invalid="ignore")
    meaning_distributions = np.nan_to_num(
        meaning_distributions / meaning_distributions.sum(axis=1, keepdims=True)
    )
    return meaning_distributions