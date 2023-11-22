import itertools

from altk.language.grammar import Grammar, Rule
from altk.language.semantics import Referent, Universe

from modals.modal_meaning import ModalMeaning, ModalMeaningSpace
from modals.modal_language import ModalExpression


def get_all_expressions(
    modal_grammar: Grammar,
    modal_universe: ModalMeaningSpace,
    depth = 5,
    ) -> list[str]:
    """Use an ALTK grammar to find the shortest description length expressions denoting every possible meaning (subset of the universe), and return a corresponding list of `ModalExpression`s.
    """

    expressions_by_meaning = modal_grammar.get_unique_expressions(
        depth=depth,
        max_size=2 ** len(modal_universe),
        unique_key=lambda expr: expr.evaluate(modal_universe),
        compare_func=lambda e1, e2: len(e1) < len(e2),
    )

    modal_expressions = [
        ModalExpression(
            form=f"dummy_form_{i}",
            meaning=meaning,
            lot_expression=str(expressions_by_meaning[meaning]) # crucial, for saving, reading, etc.
        )
        for i, meaning in enumerate(expressions_by_meaning)
        if len(meaning.referents) # excludes bottom
    ]

    return modal_expressions