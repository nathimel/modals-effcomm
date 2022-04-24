from collections import Counter
from copy import copy, deepcopy
from itertools import product
from altk.language.language import Expression, Language
from modals.modal_meaning import ModalMeaning, ModalMeaningSpace

##############################################################################
# Expression
##############################################################################
class ModalExpression(Expression):

    """A container for modal forms, meanings and other data.

    It is useful to additionally store the modal's shortest LoT description, as well as the complexity associated with this description. For semantic universals formulated in at the level of individual modal lexical items, e.g. the Independence of Force and Flavors, satisfaction of such universals is also stored.

    Example usage:

        e = Modal_Expression('might', {'weak+epistemic'}, '(* (weak ) (epistemic ))')
    """

    def __init__(self, form, meaning, lot_expression):
        super().__init__(form, meaning)
        self.set_lot_expression(lot_expression)

    def set_lot_expression(self, e):
        self._lot_expression = e

    def get_lot_expression(self):
        return self._lot_expression

    def __hash__(self) -> int:
        return (
            hash(self.get_form())
            + hash(self.get_meaning())
            + hash(self.get_lot_expression())
        )

    def __eq__(self, __o: object) -> bool:
        return (
            self.get_form() == __o.get_form()
            and self.get_meaning() == __o.get_meaning()
            and self.get_lot_expression() == __o.get_lot_expression()
        )

    def __str__(self) -> str:
        return f"Modal_Expression: [\nform={self.get_form()}\nmeaning={self.get_meaning()}\nlot_expression={self.get_lot_expression()}]"

    def yaml_rep(self) -> dict:
        """Convert to a dictionary representation of the expression for compact saving to .yml files."""
        return {
            "form": self.get_form(),
            "meaning": list(self.get_meaning().get_points()),
            "lot": self.get_lot_expression(),
        }

    @classmethod
    def from_yaml_rep(cls, rep: dict, space: ModalMeaningSpace):
        """Takes a yaml representation and returns the corresponding Modal Expression.

        Args:
            - rep: a dictionary of the form {'form': str, 'meaning': list, 'lot': str}
        """
        form = rep["form"]
        meaning = rep["meaning"]
        lot = rep["lot"]

        meaning = ModalMeaning(meaning, space)
        return cls(form, meaning, lot)


##############################################################################
# Language
##############################################################################


class ModalLanguage(Language):

    """A container for modal expressions, and other efficient communication data.

    Example usage:

        language = Modal_Language(expressions)
        c = language.get_complexity()
    """

    def __init__(self, expressions: list[ModalExpression], name=None):
        super().__init__(expressions)
        self.set_name(name)

        # initialize all other attributes to None
        self.set_complexity(None)
        self.set_informativity(None)
        self.set_optimality(None)
        self.set_naturalness(None)

    def rename_synonyms(
        self, expressions: list[ModalExpression]
    ) -> list[ModalExpression]:
        """Give any expressions with exactly the same meanings different forms.

        This is necessary at least because a speaker and listener need to be able to distinguish them.
        """
        synonyms = {
            item: count for item, count in Counter(expressions).items() if count > 1
        }

        # create a stack of names for each synonym
        synonyms = {
            item: [f"{item.get_form()}_{idx}" for idx in range(synonyms[item])]
            for item in synonyms
        }

        expressions_ = deepcopy(expressions)
        for expression in expressions_:
            if expression in synonyms:
                new_form = synonyms[expression].pop()
                expression.set_form(new_form)

        return expressions_

    def set_expressions(self, expressions: list[Expression]):
        if not expressions:
            raise ValueError("list of Expressions must not be empty.")
        self._expressions = self.rename_synonyms(expressions)

    def __str__(self) -> str:
        expressions_str = "\n".join([str(e) for e in self.get_expressions()])
        return f"Modal_Language: [\n{expressions_str}\n]"

    def __hash__(self) -> int:
        return hash(tuple([self.get_name()] + self.get_expressions()))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def get_meaning_space(self) -> ModalMeaningSpace:
        return self.get_universe()

    def set_complexity(self, complexity: float):
        self._complexity = complexity

    def get_complexity(self) -> float:
        return self._complexity

    def set_informativity(self, informativity: float):
        self._informativity = informativity

    def get_informativity(self) -> float:
        return self._informativity

    def set_optimality(self, optimality: float):
        self._optimality = optimality

    def get_optimality(self) -> float:
        return self._optimality

    def yaml_rep(self) -> tuple:
        """Get a data structure for safe compact saving in a .yml file.

        A tuple of the language name, and nested dict of list of the expressions, and trade-off data for compact saving in a .yml file.
        """
        data = (
            self.get_name(),
            {
                "expressions": [e.yaml_rep() for e in self.get_expressions()],
                "measurements": {
                    "complexity": self.get_complexity(),
                    "informativity": self.get_informativity(),
                    "optimality": self.get_optimality(),
                    "iff": self.get_naturalness(),
                },
            },
        )
        return data

    @classmethod
    def from_yaml_rep(cls, name: str, data: dict, space: ModalMeaningSpace):
        """Takes a yaml representation and returns the corresponding Modal Language.

        Args:
            - name: the name of the language

            - data: a dictionary of the expressions and trade-off measurements

            - space: the modal meaning space being used by the language.
        """
        expressions = data["expressions"]
        measurements = data["measurements"]

        complexity = measurements["complexity"]
        informativity = measurements["informativity"]
        optimality = measurements["optimality"]
        iff = measurements["iff"]

        expressions = [ModalExpression.from_yaml_rep(x, space) for x in expressions]
        lang = cls(expressions, name)
        lang.set_complexity(complexity)
        lang.set_informativity(informativity)
        lang.set_optimality(optimality)
        lang.set_naturalness(iff)
        return lang

    def get_naturalness(self) -> float:
        """Degree of quasi-naturalness, as measured by the SAV or IFF universals."""
        return self._naturalness

    def set_naturalness(self, naturalness: float):
        self._naturalness = naturalness

    """Natural languages have meaningful names."""

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    name = property(get_name, set_name)

    def is_natural(self) -> bool:
        """Whether a Modal Language represents a natural language constructed from typological data."""
        return not "dummy_lang" in self.get_name()


##############################################################################
# Functions
##############################################################################


def is_iff(e: ModalExpression) -> bool:
    """Whether an expression satisfies the Independence of Forces and Flavors Universal.

    The set of forces X that a modal lexical item m can express and the set of flavors be Y that m can express, then the full set of meaning points that m expresses is the Cartesian product of X and Y.
    """
    points = e.get_meaning().get_points()
    forces = set()
    flavors = set()
    for point in points:
        force, flavor = point.split("+")
        forces.add(force)
        flavors.add(flavor)

    for (force, flavor) in product(forces, flavors):
        point = f"{force}+{flavor}"
        if point not in points:
            return False
    return True


def degree_iff(language: ModalLanguage) -> float:
    """The fraction of a modal language satisfying the IFF semantic univeral."""
    iff_items = sum([is_iff(item) for item in language.get_expressions()])
    return iff_items / language.size()
