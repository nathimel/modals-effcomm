"""Classes for defining the evolutionary algorithm for modals, including specific mutations on modal languages."""

import random

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
        return len(language) < lang_size

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Add a random new modal to the language."""
        new_expression = random.choice(expressions)
        while new_expression in language:
            new_expression = random.choice(expressions)
        language.add_expression(new_expression)
        return language


class Remove_Modal(Mutation):
    """Remove a random modal from the language."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only remove a modal if it does not remove the only modal in a language."""
        return len(language) > 1

    def mutate(self, language: ModalLanguage, expressions=None) -> ModalLanguage:
        """Removes a random modal from the list of expressions of a modal language.

        Dummy expressions argument to have the same function signature as super().mutate().
        """
        index = random.randint(0, len(language) - 1)
        language.pop(index)
        return language


class Add_Point(Add_Modal):
    """Add a new modal expressing exactly one point, and if possible a point that the language does not already cover. Designed to increase informativity."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        return super().precondition(language, **kwargs)

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression], **kwargs
    ) -> ModalLanguage:
        """Add a new expression to the language containing exactly one random meaning point, preferably one not already expressed by the language."""

        # add a random meaning point to an existing expression
        point = random.choice(list(language.universe.referents))
        if uncovered_points(language):
            point = random.choice(list(uncovered_points(language)))

        # Search for the correct expression
        new_meaning = [point]
        new_expression = None
        for e in expressions:
            points_ = e.meaning.referents
            if set(points_) == set(new_meaning):
                new_expression = e

        if new_expression is None:
            raise ValueError("new meaning not found in set of possible meanings")

        # Add it
        language.add_expression(new_expression)
        return language


class Remove_Point(Mutation):
    """Replace an ambiguous modal with a modal expressing one fewer meaning points. Designed to increase informativity."""

    def precondition(self, language: ModalLanguage, **kwargs) -> bool:
        """Only apply when the language has a modal that expresses more than one meaning point."""
        # Can express more than one pointe
        expressions = language.expressions
        for expression in expressions:
            points = expression.meaning.referents
            if len(points) > 1:
                return True
        return False

    def mutate(
        self, language: ModalLanguage, expressions: list[ModalExpression]
    ) -> ModalLanguage:
        """Choose a random modal from the langauge and replace it with a modal that is less ambiguous by a single point."""
        # randomly select an modal with more than one meaning
        vocab = list(language.expressions).copy()
        random.shuffle(vocab)

        expression_to_remove = None
        for expression in vocab:
            points = list(expression.meaning.referents)
            if len(points) > 1:
                expression_to_remove = expression
                break

        if expression_to_remove is None:
            return language

        # randomly remove a meaning point
        point = random.choice(points)
        points.remove(point)

        # Search for the correct expression
        for e in expressions:
            points_ = e.meaning.referents
            if set(points) == set(points_):
                new_expression = e
                break

        # Replace the ambiguous expression with the more precise one
        lang_expressions = list(language.expressions).copy()
        lang_expressions.remove(expression_to_remove)
        language.expressions = sorted(tuple(lang_expressions + [new_expression]))
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
    points = [point for e in language.expressions for point in e.meaning.referents]
    space = language.universe.referents
    return set(space) - set(points)
