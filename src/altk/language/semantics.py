"""Classes for modeling the literal meanings of a language.

    Meanings are modeled as things which map linguistic forms to objects of reference. The linguistic forms and objects of reference can be richly defined, but they are opaque to the meaning.

    In efficient communication analyses, simplicity and informativeness are typically properties of semantic aspects of a language. E.g., a meaning is simple if it is easy to represent, or to compress into some code; a meaning is informative if it is easy for a listener to recover a speaker's intended literal meaning.

    Typical usage example:

        >>> from altk.language.syntax import Form
        >>> from altk.language.language import Expression, Language
        >>> form = Form('blue')
        >>> meaning = Color_Meaning() # some default meaning
        >>> expression = Expression(form, meaning)
        >>> lang = Language([expression])

"""

from abc import abstractmethod


class Universe:

    """The universe is the set of possible referent objects for a meaning."""

    def __init__(self, objects):
        self._objects = set()
        self.set_objects(objects)

    def set_objects(self, objects):
        self._objects = objects
    def get_objects(self):
        return self._objects
    universe=property(get_objects, set_objects)

    def __str__(self):
        objects = ",\n".join([str(point) for point in self.get_objects()])
        return "Universe: {}".format(str(objects))

    def __eq__(self, __o: object) -> bool:
        """Returns true if the two universes are the same set."""
        return self.get_objects() == __o.get_objects()


class Meaning:

    """A meaning picks out objects of the universe.
    
    There are several easy ways of modeling this. 
    
    On one familiar model from (e.g. predicate logic and formal semantics) a semantic value can be set, called a property: the set of objects of the universe satisfying that property. A meaning can be associated with the relevant subset of the universe, or its characteristic function.
    
    On some efficient communication analysis models, we use the concept of meaning to be a more general mapping of forms to objects of reference.

    A literal meaning is always only one atomic object of the universe, though an expression may itself be underspecified: that is, the expression can be used to express different literal meanings. Sometimes these different literal meanings are not equally likely, in which it can be helpful to define a meaning as a distribution over objects in the universe.

    Typical usage example:

        from altk.language.semantics import Meaning, Universe
        universe = Universe(set(range(10))) # 10 objects with int labels
        precise_meaning = Meaning({1}) # picks out one object
        vague_meaning = Meaning({1,6}) # can pick out more than one object
    """

    def set_universe(self, universe: Universe):
        self._universe = universe
    def get_universe(self):
        return self._universe
    
    def get_objects(self):
        return self._objects
    def set_objects(self, objects):
        self._objects = objects
    
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        pass