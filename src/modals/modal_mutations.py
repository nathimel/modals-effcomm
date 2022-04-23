"""Classes for defining the evolutionary algorithm for modals, including specific mutations on modal languages."""

from multiprocessing.sharedctypes import Value
import random
import numpy as np

from altk.effcomm.optimization import Mutation
from modals.modal_language import ModalExpression, ModalLanguage
from altk.effcomm.informativity import InformativityMeasure

##############################################################################
# Modals-specific evolutionary algorithm mutations
##############################################################################


class Add_Modal(Mutation):
    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only add a modal if the language size is not at maximum."""
        lang_size = kwargs["lang_size"]
        return language.size() < lang_size

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Add a new modal to the language. Currently the new modal must not exist in the language already, e.g. this function will not add a synonym."""
        new_expression = random.choice(expressions)
        # TODO: synonymy ?
        while language.has_expression(new_expression):
            new_expression = random.choice(expressions)
        language.add_expression(new_expression)
        return language


class Remove_Modal(Mutation):
    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only remove a modal if it does not remove the only modal in a language."""
        return language.size() > 1

    def mutate(self, language: ModalLanguage, expressions=None) -> ModalLanguage:
        """Removes a random modal from the list of expressions of a modal language.

        Dummy expressions argument to have the same function signature as super().mutate().
        """
        index = random.randint(0, language.size() - 1)
        language.pop(index)
        return language


class Add_Point(Mutation):
    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only apply when language is not perfectly informative and every point is not already expressible."""

        # Check informativity
        inf_measure = kwargs["inf_measure"]
        inf = inf_measure.language_informativity(language)
        if np.isclose(inf, 1.0):
            return False

        # Check for any points not expressed
        points = [
            point
            for e in language.get_expressions()
            for point in e.get_meaning().get_objects()
        ]
        space = language.get_meaning_space().get_objects()
        to_add = set(space) - set(points)
        if not to_add:
            return False

        return True

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression], **kwargs
    ) -> ModalLanguage:
        """Add a random meaning point not already expressed by the language to one of its expressions."""

        # get all meanings expressed
        points = [
            point
            for e in language.get_expressions()
            for point in e.get_meaning().get_objects()
        ]
        space = language.get_meaning_space().get_objects()
        to_add = list(set(space) - set(points))
        point = random.choice(to_add)

        # add meaning point to an existing expression
        index = random.randint(0, language.size() - 1)
        expression_points = list(
            language.get_expressions().copy()[index].get_meaning().get_objects()
        )

        new_meaning = set(expression_points + [point])

        # Search for the correct expression
        new_expression = None
        for e in expressions:
            points_ = e.get_meaning().get_objects()
            if set(points_) == new_meaning:
                new_expression = e

        if new_expression is None:
            raise ValueError("new meaning not found in set of possible meanings")

        # Replace modal with the new one with the additional point
        language.add_expression(new_expression)
        language.pop(index)
        return language


class Remove_Point(Mutation):
    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only apply when language is not perfectly informative, or when it can express more than one meaning point"""

        # Is not already perfectly informative
        inf_measure = kwargs["inf_measure"]
        inf = inf_measure.language_informativity(language)
        if np.isclose(inf, 1.0):
            return False

        # Can express more than one point
        expressions = language.get_expressions()
        meanings = 0
        for expression in expressions:
            points = expression.get_meaning().get_objects()
            if points:
                meanings += len(points)
        return meanings > 1

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Choose a random modal from the langauge and replace it with a modal that deletes one of the meaning points a language expresses.

        Should increase informativeness.
        """
        # randomly select a modal
        while True:
            index = random.randint(0, language.size() - 1)
            points = list(
                language.get_expressions().copy()[index].get_meaning().get_objects()
            )

            # randomly remove a bit
            point = random.choice(points)
            points.remove(point)

            # replace the modal
            if points:
                # Search for the correct expression
                for e in expressions:
                    points_ = e.get_meaning().get_objects()
                    if set(points) == set(points_):
                        new_expression = e
                # replace
                language.add_expression(new_expression)
                language.pop(index)
                break
        return language


class Interchange_Modal(Mutation):

    """Removes and then adds a random expresion.

    Requires creating Add_Modal and Remove_Modal mutations as instance attributes.
    """

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Always applies."""
        return True

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Removes and then adds a random expresion."""
        remove = Remove_Modal.mutate
        add = Add_Modal.mutate
        return remove(add(language, expressions), expressions)
