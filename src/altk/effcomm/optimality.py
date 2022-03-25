"""Classes and functions for measuring the Pareto optimality of a language with respect to a Pareto frontier."""

from abc import abstractmethod
from altk.language.language import Language

class Optimality_Measure:

    def __init__(self):
        pass

    def batch_optimality(self, langs: list[Language]) -> list[float]:
        """Measure the optimality of a list of languages."""
        return [self.language_optimality(lang) for lang in langs]

    @abstractmethod
    def language_optimality(self, language: Language) -> float:
        """Measure the optimality of a single language.
        """
        pass