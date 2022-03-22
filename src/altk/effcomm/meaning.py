"""Classes for representing semantic spaces of languages as a set of points.

    In efficient communication analyses, literal meanings are given a unified analysis as the objects that are picked out by words. Note that a word or linguistic form will often refer to more than one literal meaning. 

    These literal meanings are modeled in maximal generality: a Meaning_Point object does not require or prohibit any additional data storage beyond a __name which is used to pick it out from the Meaning_Space of a language.

    Typical usage example:

    point = Meaning_Point('foo')
    space = Meaning_Space({point})
"""
from altk.language.language import Meaning

class Meaning_Space(Meaning):
    """A container for meaning points.

    Attributes:
        points: a set containing meaning point names or indices as keys and Meaning_Points as values.
    """
    
    def __init__(self, points):
        # super().__init__()
        self.__points = set()
        self.set_points(points)
        # raise NotImplementedError()

    def set_points(self, points: set):
        self.__points = points
    def get_points(self):
        return self.__points
    points=property(get_points, set_points)

    def __len__(self):
        return len(self.get_points())


class Meaning_Point(Meaning):
    """An object of reference.

    Examples of meaning points include 'weak+deontic' meaning for modals, or 
    a color-chip number for colors.

    Attributes:
        name: a string that uniquely identifies the meaning point.
    """
    def __init__(self, name=None):
        # super().__init__()
        self.__name = str()
        self.__data = None
        self.set_name(name)
        # raise NotImplementedError()

    def set_name(self, name):
        self.__name = name
    def get_name(self):
        return self.__name
    name=property(get_name, set_name)

    def set_data(self, data):
        self.__data = data
    def get_data(self):
        return self.__data
    data=property(get_data, set_data)
