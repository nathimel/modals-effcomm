"""Classes for representing semantic spaces of languages as a set of points.

    In efficient communication analyses, literal meanings are given a unified analysis as the objects that are picked out by words. Note that a word or linguistic form will often refer to more than one literal meaning. 

    These literal meanings are modeled in maximal generality: a Meaning_Point object does not require or prohibit any additional data storage beyond a __name which is used to pick it out from the Meaning_Space of a language.

    Typical usage example:

    point = Meaning_Point('foo')
    space = Meaning_Space({point})
"""

class Meaning_Space:
    """A container for meaning points.

    Attributes:
        points: a set containing meaning point names or indices as keys and Meaning_Points as values.
    """
    
    def __init__(self, points=None):
        self.__points = set()
        self.setpoints(points)

    def setpoints(self, points: set):
        self.__points = points
    def getpoints(self):
        return self.__points
    points=property(getpoints, setpoints)

    def __str__(self):
        raise NotImplementedError()

class Meaning_Point:
    """An object of reference.

    Examples of meaning points include 'weak+deontic' meaning for modals, or 
    a color-chip number for colors.

    Attributes:
        name: a string that uniquely identifies the meaning point.
    """
    def __init__(self, name=None):
        self.__name = str()
        self.__data = None
        self.setname(name)

    def setname(self, name):
        self.__name = name
    def getname(self):
        return self.__name
    name=property(getname, setname)

    def setdata(self, data):
        self.__data = data
    def getdata(self):
        return self.__data
    data=property(getdata, setdata)

    def __str__(self):
        raise NotImplementedError
