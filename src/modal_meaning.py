from ssl import get_default_verify_paths
from altk.effcomm.meaning import Meaning_Point, Meaning_Space

class Modal_Meaning_Space(Meaning_Space):
    """A set representing the possible modal (force, flavor) pairs.

    Example usage:
        >>> points = {'weak+epistemic', 'weak+deontic'}
        >>> mps = {Modal_Meaning_Point(name=point) for point in points})
        >>> space = Modal_Meaning_Space(mps)
    """


    def __init__(self, points):
        super().__init__(points)
    
    def __str__(self):
        points = ",\n".join([str(point) for point in self.getpoints()])
        space = "Modal_Meaning_Space: [\n{}]".format(points)
        return space

class Modal_Meaning_Point(Meaning_Point):

    def __init__(self, name=None):
        super().__init__(name=name)


    def __str__(self):
        """For printing out a single meaning point.
        Example usage: 
            >>> p = Modal_Meaning_Point('m')
            >>> print(p)
            Point: (name='m', data=None)
        """
        return "Point: (name={0}, data={1})".format(
        str(self.get_name()), str(self.get_data()))

class Modal_Meaning(Modal_Meaning_Space):
    """"A modal meaning is a distribution over Modal_Meaning_Points it can be used to communicate.
    
    Example usage:
        >>> points = {'weak+epistemic', 'weak+deontic'}
        >>> mps = {Modal_Meaning_Point(name=point) for point in points})
        >>> space = Modal_Meaning_Space(mps)
        >>> dist = {point: 1/len(space) for point in space.get_points()}
        >>> meaning_example = Modal_Meaning(dist)
        >>> meaning_example
        Meaning: [
        Point: (name=weak+epistemic, data=None): 0.5
        Point: (name=weak+deontic, data=None): 0.5
        ]
    """

    def __init__(self, distribution):
        self.__distribution = dict()
        self.set_distribution(distribution)

    def set_distribution(self, distribution):
        self.__distribution = distribution
    def get_distribution(self):
        return self.__distribution
    distribution=property(get_distribution, set_distribution)

    def __str__(self):
        entries = ["{0}: {1}".format(k, v) for k,v in self.get_distribution().items()]
        s = "Meaning: [\n{}\n]".format("\n".join(entries))
        return s
