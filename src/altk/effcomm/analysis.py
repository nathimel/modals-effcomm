"""Functions for analyzing the results of the simplicity/informativeness trade-off."""

from altk.language.language import Language
from altk.effcomm.complexity import ComplexityMeasure
from altk.effcomm.informativity import InformativityMeasure

class EffComm_Analyzer:

    def __init__(
        self,
        languages: list[Language], 
        comp_measure: ComplexityMeasure,
        inf_measure: InformativityMeasure,
        ):
        self.comp_measure = comp_measure
        self.inf_measure = inf_measure

        self.set_languages(languages)

    def measure_languages(self) -> None:
        """Measure the pareto optimality, with respect to a non-dominated front optimizing simplicity and informativeness, of a list of languages and store the results in the class instance as attributes.
        """
        raise NotImplementedError
        

    def set_languages(self, langs: list[Language]):
        self.__languages = langs
    def get_languages(self) -> list[Language]:
        return self.__languages
    languages=property(get_languages, set_languages)

    def set_dominating_languages(self, doms: list[Language]):
        self.__dominating_languages = doms
    def get_dominating_languages(self) -> list[Language]:
        return self.__dominating_languages
    dominating_languages=property(get_dominating_languages, set_dominating_languages)