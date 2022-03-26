import numpy as np
from altk.language.language import Expression, Language
from modals.modal_meaning import Modal_Meaning, Modal_Meaning_Space

##############################################################################
# Expression
##############################################################################
class Modal_Expression(Expression):

    """A container for modal forms, meanings and other data.
    
    It is useful to additionally store the modal's shortest LoT description, as well as the complexity associated with this description. For semantic universals formulated in at the level of individual modal lexical items, e.g. the Independence of Force and Flavors, satisfaction of such universals is also stored.

    Example usage:
            
        e = Modal_Expression('might', {'weak+epistemic'}, '(* (weak ) (epistemic ))')
    """

    def __init__(self, form, meaning, lot_expression):
        super().__init__(form, meaning)
        self.set_lot_expression(lot_expression)

    def set_lot_expression(self, e):
        self.__lot_expression = e
    def get_lot_expression(self):
        return self.__lot_expression

    def __hash__(self) -> int:
        return (
            hash(self.get_form())
            + hash(self.get_meaning())
            + hash(self.get_lot_expression())
            )
    def __eq__(self, __o: object) -> bool:
        return (self.get_form() == __o.get_form()
            and self.get_meaning() == __o.get_meaning()
            and self.get_lot_expression() == __o.get_lot_expression())

    def __str__(self) -> str:
        return "Modal_Expression: [\nform={0}\nmeaning={1}\nlot_expression={2}]".format(self.get_form(), self.get_meaning(), self.get_lot_expression())
        # return str(self.get_meaning().to_array())

    def yaml_rep(self) -> dict:
        """Convert to a dictionary representation of the expression for compact saving to .yml files."""
        return {
            'form':self.get_form(),
            'meaning':list(self.get_meaning().get_points()),
            'lot':self.get_lot_expression(),
        }

    @classmethod
    def from_yaml_rep(cls, rep: dict, space: Modal_Meaning_Space):
        """Takes a yaml representation and returns the corresponding Modal Expression.

        Args: 
            - rep: a dictionary of the form {'form': str, 'meaning': list, 'lot': str}
        """
        form = rep['form']
        meaning = rep['meaning']
        lot = rep['lot']

        meaning = Modal_Meaning(meaning, space)
        return cls(form, meaning, lot)

##############################################################################
# Language
##############################################################################

class Modal_Language(Language):

    """A container for modal expressions, and other efficient communication data.

    Example usage:

        language = Modal_Language(expressions)
        c = language.get_complexity()
    """

    def __init__(self, expressions: list[Modal_Expression], name=None):
        super().__init__(expressions)
        self.set_name(name)

    def __str__(self) -> str:
        return "Modal_Language: [\n{}\n]".format("\n".join([str(e) for e in self.expressions]))

    def __hash__(self) -> int:
        return hash(tuple(self.get_expressions()))

    def __eq__(self, __o: object) -> bool:
        return self.get_expressions() == __o.get_expressions()

    def get_meaning_space(self) -> Modal_Meaning_Space:
        return self.get_universe()

    def set_complexity(self, complexity: float):
        self.__complexity = complexity
    def get_complexity(self) -> float:
        return self.__complexity
    complexity=property(get_complexity, set_complexity)

    def set_informativity(self, informativity: float):
        self.__informativity = informativity
    def get_informativity(self) -> float:
        return self.__informativity
    informativity=property(get_informativity, set_informativity)

    def set_optimality(self, optimality: float):
        self.__optimality = optimality
    def get_optimality(self) -> float:
        return self.__optimality

    def set_iff(self, iff: float):
        self.__iff = iff
    def get_iff(self):
        return self.__iff

    def yaml_rep(self) -> tuple:
        """A pair of the language name and list of the expressions for compact saving in a .yml file."""
        return (
            self.get_name(), [
                e.yaml_rep() for e in self.expressions
                ]
        )
    @classmethod
    def from_yaml_rep(cls, rep: dict, space: Modal_Meaning_Space):
        """Takes a yaml representation and returns the corresponding Modal Language.

        Args: 
            - rep: a dictionary of the form {'language_name': data}
        """
        name, expressions = rep
        expressions = [
            Modal_Expression.from_yaml_rep(x, space) for x in expressions
        ]
        return cls(expressions, name)

    """Natural languages have meaningful names."""
    def set_name(self, name):
        self.__name = name
    def get_name(self):
        return self.__name
    name=property(get_name, set_name)

    def is_natural(self) -> bool:
        """Whether a Modal Language represents a natural language constructed from typological data."""
        return not 'dummy_lang' in self.get_name()

##############################################################################
# Functions
##############################################################################

def is_iff(e: Modal_Expression) -> bool:
    """The Independence of Forces and Flavors Universal states that XXX.

    Formally, 
        XXX.
    """
    return int(np.random.uniform(0,2)) # dummy

def degree_iff(language: Modal_Language) -> float:
    """The fraction of a modal language satisfying the IFF semantic univeral.
    """
    iff_items = sum([is_iff(item) for item in language.get_expressions()])
    return iff_items / language.size()
