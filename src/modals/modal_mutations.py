"""Classes for defining the evolutionary algorithm for modals, including specific mutations on modal languages."""

import random
import numpy as np

from altk.effcomm.optimization import Mutation
from modals.modal_language import ModalExpression, ModalLanguage
from modals.modal_meaning import ModalMeaning

##############################################################################
# Modals-specific evolutionary algorithm mutations
##############################################################################


class Add_Modal(Mutation):
    """Add a random modal to the language."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only add a modal if the language size is not at maximum."""
        lang_size = kwargs["lang_size"]
        return language.size() < lang_size

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Add a random new modal to the language."""
        new_expression = random.choice(expressions)
        while language.has_expression(new_expression):
            new_expression = random.choice(expressions)
        language.add_expression(new_expression)
        return language


class Remove_Modal(Mutation):
    """Remove a random modal from the language."""

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
    """Add a new modal expressing exactly one point the language does not already cover. Designed to increase informativity."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only apply when language is not perfectly informative and every point is not already expressible."""

        # Check informativity
        inf_measure = kwargs["inf_measure"]
        inf = inf_measure.language_informativity(language)
        if np.isclose(inf, 1.0):
            return False

        # Check if any inexpressible meanings
        to_add = uncovered_points(language)
        return bool(to_add)

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression], **kwargs
    ) -> ModalLanguage:
        """Add a new expression to the language containing exactly one random meaning point not already expressed by the language."""

        # add a random meaning point to an existing expression
        point = random.choice(list(uncovered_points(language)))

        # Search for the correct expression
        new_meaning = [point]
        new_expression = None
        for e in expressions:
            points_ = e.meaning.objects
            if set(points_) == set(new_meaning):
                new_expression = e

        if new_expression is None:
            raise ValueError("new meaning not found in set of possible meanings")

        if new_expression in language.expressions:
            raise ValueError(
                "AddPoint should not add synonyms but new expression to add alredy in vocabulary."
            )

        # Add it
        language.add_expression(new_expression)
        return language


class Remove_Point(Mutation):
    """Replace an ambiguous modal with a modal expressing one fewer meaning points. Designed to increase informativity."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only apply when language is not perfectly informative, or when it has a modal that expresses more than one meaning point."""

        # Is not already perfectly informative
        inf_measure = kwargs["inf_measure"]
        inf = inf_measure.language_informativity(language)
        if np.isclose(inf, 1.0):
            return False

        # Can express more than one point
        expressions = language.expressions
        for expression in expressions:
            points = expression.meaning.objects
            if len(points) > 1:
                return True
        return False

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Choose a random modal from the langauge and replace it with a modal that deletes one of the meaning points a language expresses."""
        # randomly select an modal with more than one meaning
        vocab = language.expressions.copy()
        random.shuffle(vocab)

        for index, expression in enumerate(vocab):
            points = list(expression.meaning.objects)
            if len(points) > 1:
                break

        # randomly remove a meaning point
        point = random.choice(points)
        points.remove(point)

        # Search for the correct expression
        for e in expressions:
            points_ = e.meaning.objects
            if set(points) == set(points_):
                new_expression = e
                break

        language.add_expression(new_expression)
        language.pop(index)
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
        add = Add_Modal()
        remove = Remove_Modal()
        return remove.mutate(add.mutate(language, expressions), expressions)


def uncovered_points(language: ModalLanguage) -> set[ModalMeaning]:
    """Helper function for AddPoint to get the list of meanings not expressible in a language."""
    # Check for any points not expressed
    points = [
        point
        for e in language.expressions
        for point in e.meaning.objects
    ]
    space = language.universe.objects
    return set(space) - set(points)
