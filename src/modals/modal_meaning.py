from itertools import product
import numpy as np
import pandas as pd
from altk.language.semantics import Universe, Meaning


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

    def __init__(self, forces: set, flavors: set):
        """Construct a meaning space for modals, using two axes of variation.

        A modal meaning space inherits from altk.semantics.Universe, and the set of (force,flavor) pairs is the set of objects in the Universe.

        Args:
            - forces: a set of the modal force names
            - flavors: a set of the modal flavor names
        """
        self.forces = list(forces)
        self.flavors = list(flavors)
        # construct a universe with cartesian product
        super().__init__(
            {f"{force}+{flavor}" for force in forces for flavor in flavors}
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
        """Generates all possible modal meanings for the meaning space.

        Define underspecified meanings equally probable, so that generating meanings is equivalent to generating possible bit-arrays, and the number of them is the size of the powerset of the set of modal meaning points. For example, we only consider:

                    epistemic  deontic  circumstantial
            weak            0.5        0               0
            strong          0.5        0               0

        and not

                    epistemic  deontic  circumstantial
            weak            0.9        1               0
            strong          0.1        0               0

        since the latter suggests defining a modal meaning as a more general distribution over the space and there are infinitely many.
        """
        shape = (len(self.forces), len(self.flavors))
        arrs = [
            np.array(i).reshape(shape)
            for i in product([0, 1], repeat=len(self.objects))
        ]
        arrs = arrs[1:]  # remove the empty array meaning to prevent div by 0
        meanings = [ModalMeaning(self.array_to_points(arr), self) for arr in arrs]
        return meanings

    def array_to_points(self, a: np.ndarray) -> set:
        """Converts a numpy array to a set of points.

        Args:
            - a: numpy array representing a modal meaning.

        Raises:
            ValueError: if the meaning space doesn't match the array shape.axis 0 (rows) are forces, axis 1 (columns) are flavors.
        """
        if a.shape != (len(self.forces), len(self.flavors)):
            raise ValueError(
                f"The size of the numpy array must match the size of the modal meaning space. a.shape={a.shape}, self.forces={len(self.forces)}, self.flavors={len(self.flavors)}"
            )

        return {
            f"{self.forces[pair[0]]}+{self.flavors[pair[1]]}" for pair in np.argwhere(a)
        }

    def __str__(self):
        return str(self.arr)


class ModalMeaning(Meaning):
    """ "A modal meaning is a distribution over Modal_Meaning_Points it can be used to communicate.

    TODO: Design to be immutable.

    Attributes:
        - points: the (force,flavor) pairs a modal can be used to express. Each point is a string, 'force+flavor'.

    Example usage:

        m = Modal_Meaning({'weak+epistemic'}, space)
    """

    def __init__(self, points: set, meaning_space: ModalMeaningSpace):
        self.objects = points
        self.universe = meaning_space

    def to_distribution(self) -> dict:
        """Convert the set of points into a dict representing a uniform distribution over meaning points."""
        can_express = {k: len(self.objects) for k, v in self.objects}
        space = {
            k: 0 for k in self.universe.objects if k not in can_express
        }
        return can_express | space

    def to_array(self):
        """Converts the set of points to a numpy array.

        Example usage:

            m = Modal_Meaning({'weak+epistemic', 'strong+epistemic', 'weak+deontic'}, space)
            m.to_array()
            [[1 1 0],
             [1 0 0]]

        Returns:
            np.ndarray: the array representation of the points instantiated on the modal table of variation
        """
        a = np.array(self.universe.arr)
        for point in self.objects:
            force, flavor = point.split("+")
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
        # return str(self.to_df())
        return str(self.to_array())

    def __hash__(self) -> int:
        return hash(tuple(self.objects))

    def __eq__(self, __o: object) -> bool:
        # return self.get_points() == __o.get_points()
        return self.objects == __o.objects
