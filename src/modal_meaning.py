from altk.effcomm.meaning import Meaning_Point, Meaning_Space

class Modal_Meaning_Space(Meaning_Space):

    def __init__(self, points=None):
        super().__init__(points)
    
    def __str__(self):
        points = ",\n".join([str(point) for point in self.getpoints()])
        space = "Modal_Meaning_Space: [\n{}]".format(points)
        return space

class Modal_Meaning_Point(Meaning_Point):

    def __init__(self, name=None):
        super().__init__(name=name)

    def __str__(self):
        return "Point: (name={0}, data={1})".format(
        str(self.getname()), str(self.getdata()))