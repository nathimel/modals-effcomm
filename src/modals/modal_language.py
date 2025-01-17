import numpy as np

from collections import Counter
from copy import deepcopy
from itertools import product

from altk.language.language import Expression, Language
from modals.modal_meaning import ModalMeaning, ModalMeaningSpace
from modals.modal_meaning import ModalMeaningPoint

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
        self.lot_expression = lot_expression

    def __hash__(self) -> int:
        return hash(
            tuple([hash(self.form), hash(self.meaning), hash(self.lot_expression)])
        )

    def __lt__(self, __o: object) -> bool:
        return self.form < __o.form

    def __eq__(self, __o: object) -> bool:
        return (
            self.form == __o.form
            and self.meaning == __o.meaning
            and self.lot_expression == __o.lot_expression
        )

    def __str__(self) -> str:
        return f"Modal_Expression: [\nform={self.form}\nmeaning={self.meaning}\nlot_expression={self.lot_expression}]"

    def yaml_rep(self) -> dict:
        """Convert to a dictionary representation of the expression for compact saving to .yml files."""
        return {
            "form": self.form,
            # N.B.: force+flavor string is most readable in YML file
            "meaning": [point.name for point in self.meaning.referents],
            "lot": self.lot_expression,
        }

    @classmethod
    def from_yaml_rep(cls, rep: dict, space: ModalMeaningSpace):
        """Takes a yaml representation and returns the corresponding Modal Expression.

        Args:
            - rep: a dictionary of the form {'form': str, 'meaning': list[str], 'lot': str}
        """
        form = rep["form"]
        points = [ModalMeaningPoint.from_yaml_rep(name=name) for name in rep["meaning"]]
        # points = [ModalMeaningPoint(name=name) for name in rep["meaning"]]
        lot = rep["lot"]

        meaning = ModalMeaning(points, space)
        return cls(form, meaning, lot)


##############################################################################
# Language
##############################################################################


class ModalLanguage(Language):

    """A container for modal expressions, and other efficient communication data.

    Example usage:

        language = Modal_Language(expressions)
        c = language.complexity
    """

    def __init__(
        self,
        expressions: list[ModalExpression],
        name: str = None,
        data=None,
        natural=False,
    ):
        super().__init__(expressions)
        # Initialize / load all data
        self.data = (
            {
                "complexity": None,
                "simplicity": None,
                "comm_cost": None,
                "informativity": None,
                "optimality": None,
                "iff": None,
                "sav": None,
                "dlsav": None,
                "name": name,
                "Language": None,
                "family": "artificial",
            }
            if data is None
            else data
        )

        # Preserve language type when loading from yaml
        if (
            (data is not None)
            and ("Language" in data)
            and (data["Language"] == "natural")
        ):
            self.natural = True
        else:
            self.natural = False

        # TODO: do the same as above for `name`

    """Whether a Modal Language represents a natural language constructed from typological data."""

    @property
    def natural(self) -> bool:
        return self._natural

    @natural.setter
    def natural(self, val) -> None:
        if not isinstance(val, bool):
            raise ValueError(
                f"the attribute `natural` must be set to a bool, received type {type(val)}."
            )
        self._natural = val
        # make sure data is consistent
        self.data["Language"] = "natural" if self._natural else "artificial"

    def rename_synonyms(
        self, expressions: list[ModalExpression]
    ) -> list[ModalExpression]:
        """Give any expressions with exactly the same meanings (e.g., synonyms) different forms.

        This is necessary at least because a speaker and listener need to be able to distinguish them.
        """
        synonyms = {
            item: count for item, count in Counter(expressions).items() if count > 1
        }

        # create a stack of names for each synonym
        synonyms = {
            item: [f"{item.form}_{idx}" for idx in range(synonyms[item])]
            for item in synonyms
        }

        expressions_ = deepcopy(expressions)
        for expression in expressions_:
            if expression in synonyms:
                new_form = synonyms[expression].pop()
                expression.form = new_form

        return expressions_

    @property
    def expressions(self) -> list[ModalExpression]:
        return super().expressions

    @expressions.setter
    def expressions(self, val) -> None:
        if not val:
            raise ValueError("list of ModalExpressions must not be empty.")
        self._expressions = self.rename_synonyms(val)

    def __str__(self) -> str:
        expressions_str = "\n".join([str(e) for e in self.expressions])
        return f"Modal_Language: {self.data['name']}\n[\n{expressions_str}\n]"

    def __hash__(self) -> int:
        """Return a unique hash for a ModalLanguage. Two languages are unique if they differ in their vocabulary only by the forms of each expression.

        Because we've specified that expressions are hashed as a function of their meaning, lot formula, AND their form. This was necessary for differentiating synonymous expressions on the informativity calculation side, where we map expressions to indices and vice versa. However, we need to make sure that all natural languages are distinct, even if they have exactly the same modal meanings, differing only in form.

        To this end, we treat two languages equal if:

            (1) If they are artificial, then they differ only in forms.
            (2) If they are natural, they must have exactly the same forms.

        For the artificial langs, we hash a tuple of the sorted list of LoT strings in a language.
        """

        if self.natural:
            expressions_hash = hash(tuple(sorted([hash(e) for e in self.expressions])))
        else:
            # hash a tuple of the sorted list of LoT strings in a language
            expressions_hash = hash(
                tuple(sorted([e.lot_expression for e in self.expressions]))
            )
        return expressions_hash

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def yaml_rep(self) -> dict[str, dict]:
        """Get a data structure for safe compact saving in a .yml file.

        A dict of the language name and its data. This data is itself a dict of a list of the expressions, and other data.
        """
        data = {
            self.data["name"]: {
                "expressions": [e.yaml_rep() for e in self.expressions],
                "data": self.data,
                "length": self.__len__(),  # just for easy inspection
            },
        }
        return data

    @classmethod
    def from_yaml_rep(cls, name: str, lang_dict: dict, space: ModalMeaningSpace):
        """Takes a yaml representation and returns the corresponding Modal Language.

        Args:
            - name: the name of the language

            - lang_dict: a dictionary of the expressions and trade-off data

            - space: the modal meaning space being used by the language.
        """
        expressions = lang_dict["expressions"]
        data = lang_dict["data"]

        expressions = [ModalExpression.from_yaml_rep(x, space) for x in expressions]
        lang = cls(expressions, name=name, data=data)

        return lang

    @classmethod
    def default_language_from_space(cls, space: ModalMeaningSpace):
        """Construct a default, perfectly informative ModalLanguage from a ModalMeaningSpace."""
        expressions = [
            ModalExpression(
                form=f"default_expression_{referent}",
                meaning=ModalMeaning(
                    points=[
                        ModalMeaningPoint(force=referent.force, flavor=referent.flavor)
                    ],
                    meaning_space=space,
                ),
                lot_expression=None,  # cannot be measured for complexity
            )
            for referent in space.referents
        ]
        return cls(expressions, name="DEFAULT_LANGUAGE")


##############################################################################
# Functions
##############################################################################


def iff(e: ModalExpression) -> bool:
    """Whether an expression satisfies the Independence of Forces and Flavors Universal.

    The set of forces X that a modal lexical item m can express and the set of flavors be Y that m can express, then the full set of meaning points that m expresses is the Cartesian product of X and Y.
    """
    points = e.meaning.referents
    forces = set()
    flavors = set()
    for point in points:
        # force, flavor = point.name.split("+")
        force, flavor = point.data
        forces.add(force)
        flavors.add(flavor)

    for (force, flavor) in product(forces, flavors):
        # name = f"{force}+{flavor}"
        pair = (force, flavor)
        # if name not in [point.name for point in points]:
        if pair not in [point.data for point in points]:
            return False
    return True


def sav(e: ModalExpression) -> bool:
    """Single Axis of Variability universal: a modal expression may exhibit
    ambiguity across forces, or flavors, but not both."""
    points = e.meaning.referents
    forces = set()
    flavors = set()
    for point in points:
        # force, flavor = point.name.split("+")
        force, flavor = point.data
        forces.add(force)
        flavors.add(flavor)

    if len(forces) > 1 and len(flavors) > 1:
        return False
    return True


def dlsav(language: ModalLanguage) -> bool:
    """Domain-Level Single Axis of Variability universal: modals may be ambiguous across force or flavor, within a single modal domain (root vs epistemic).

    There is one main case to check for, after checking that the SAV universal holds of all expressions.

    Note: Epistemic modals never cause a violation.
     - if modal is within the epistemic domain and satisfies sav, dlsav will not be violated (because there is only one flavor in this 'domain', and modals are allowed to span domains, e.g. English 'must'.)

    Case to check for: there aren't both kinds of ambiguity within the root domain.
    - if the modal is in the root domain, and is ambiguous along axis a, no other root modals may be ambiguous across axis b where a != b.
    """
    row_ambigs = False
    col_ambigs = False
    for expression in language.expressions:
        # preliminary: dlsav is a refinement
        if not sav(expression):
            return False

        # get meanings
        argw = np.argwhere(expression.meaning.to_array())
        # has more than a single meaning
        if argw.size != 0 and len(argw) != 1:
            # any meanings not the epistemic column
            if np.any(argw[:, 1]):
                # check all values same along first axis
                if np.all(argw[:, 0] == argw[0, 0]):
                    row_ambigs = True
                # check all values same along second axis
                if np.all(argw[:, 1] == argw[0, 1]):
                    col_ambigs = True

    # if not both kinds of ambiguity / case 2 is true of entire language
    if not (row_ambigs and col_ambigs):
        return True
    return False
