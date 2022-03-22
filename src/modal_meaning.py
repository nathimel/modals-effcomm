from altk.effcomm.meaning import Meaning_Point, Meaning_Space, Distribution_Meaning

class Modal_Meaning_Space(Meaning_Space):
    """Represents the set of possible modal (force, flavor) pairs.

    Attributes:
        points:

    Example usage:
        >>> points = {'weak+epistemic', 'weak+deontic'}
        >>> mps = {Modal_Meaning_Point(name=point) for point in points})
        >>> space = Modal_Meaning_Space(mps)
    """

    def __init__(self, points):
        super().__init__(points)
    
    def __str__(self):
        points = ",\n".join([str(point) for point in self.get_points()])
        space = "Modal_Meaning_Space: [\n{}\n]".format(points)
        return space

class Modal_Meaning_Point(Meaning_Point):

    """A meaning point is a (force,flavor) pair.

    Attributes:
        name:
    """

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

class Modal_Meaning(Distribution_Meaning):
    """"A modal meaning is a distribution over Modal_Meaning_Points it can be used to communicate.
    
    Attributes:
        distribution:

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
        super().__init__(distribution)

    def __str__(self):
        entries = ["{0}: {1}".format(k, v) for k,v in self.get_distribution().items()]
        s = "Meaning: [\n{}\n]".format("\n".join(entries))
        return s
