"""A class for constructing an efficient communication analysis from a pool of languages."""

import numpy as np
import plotnine as pn
import pandas as pd

from altk.language.language import Language
from altk.effcomm.complexity import ComplexityMeasure
from altk.effcomm.informativity import InformativityMeasure
from pygmo import non_dominated_front_2d
from typing import Callable

from scipy import interpolate
from scipy.spatial.distance import cdist


class Tradeoff:
    """Class for building a final efficient communication analysis of languages.

    A set of languages, measures of informativity and simplicity (complexity) fully define the efficient communication results, which is the relative (near) Pareto optimality of each language. Sometimes we want to measure degrees of natualness, or a categorical analogue of naturalness, as e.g. satisfaction with a semantic universal. 
    
    This class contains functions for measuring the languages and formatting results as a dataframe or a plot.
    """
    def __init__(
        self,
        languages: list[Language],
        comp_measure: ComplexityMeasure,
        inf_measure: InformativityMeasure,
        degree_naturalness: Callable,
    ):
        self.comp_measure = comp_measure
        self.inf_measure = inf_measure
        self.degree_naturalness = degree_naturalness

        self.set_languages(languages)

    def measure_languages(self) -> list[Language]:
        """Measure a list of languages and return a pair of (all languages, dominant_languages).

        Measure the pareto optimality, with respect to a non-dominated front optimizing simplicity and informativeness, of a list of languages. This involves setting all the necessary data for the full efficient communication analysis.
        """
        langs = self.get_languages()
        # measure simplicity, informativity, and semantic universals
        for lang in langs:
            lang.set_complexity(self.comp_measure.language_complexity(lang))
            lang.set_informativity(self.inf_measure.language_informativity(lang))
            lang.set_naturalness(self.degree_naturalness(lang))

        # measure relative pareto optimality
        dominating_indices = non_dominated_front_2d(
            list(
                zip(
                    [1 - lang.get_informativity() for lang in langs],
                    [lang.get_complexity() for lang in langs],
                )
            )
        )

        dominating_languages = [langs[i] for i in dominating_indices]
        self.set_languages(langs)
        self.set_dominating_languages(dominating_languages)
        self.measure_closeness(self.interpolate_data())
        return (self.get_languages(), self.get_dominating_languages())

    def measure_closeness(self, pareto_points: list):
        """Measure the Pareto optimality of each language by measuring its Euclidean closeness to the frontier."""
        langs = self.get_languages()
        comm_cost = []
        comp = []
        for lang in langs:
            comm_cost.append(1 - lang.get_informativity())
            comp.append(lang.get_complexity())
        points = np.array(list(zip(comm_cost, comp)))

        # Measure closeness of each language to any frontier point
        distances = cdist(points, pareto_points)
        min_distances = np.min(distances, axis=1)

        for i, lang in enumerate(langs):
            # warning: yaml that saves lang must use float, not numpy.float64 !
            lang.set_optimality(1 - float(min_distances[i]))
        self.set_languages(langs)

    def interpolate_data(self) -> np.ndarray:
        """Interpoloate the points yielded by the pareto optimal languages into a continuous (though not necessarily smooth) curve."""
        dom_cc = []
        dom_comp = []
        for lang in self.get_dominating_languages():
            dom_cc.append(1 - lang.get_informativity())
            dom_comp.append(lang.get_complexity())

        values = list(set(zip(dom_cc, dom_comp)))
        pareto_x, pareto_y = list(zip(*values))

        interpolated = interpolate.interp1d(
            pareto_x, pareto_y, fill_value="extrapolate"
        )
        pareto_costs = np.linspace(0, 1.0, num=5000)
        pareto_complexities = interpolated(pareto_costs)
        pareto_points = np.array(list(zip(pareto_costs, pareto_complexities)))
        return pareto_points

    def get_dataframe(self, languages: list[Language]) -> pd.DataFrame:
        """Get a pandas DataFrame for a list of languages containing efficient communication data.

        Args:
            - languages: the list of languages for which to get efficient communication dataframe.

        Returns:
            - data: a pandas DataFrame with rows as individual languages, with the columns specifying their
                - communicative cost
                - cognitive complexity
                - satisfaction of the iff universal
                - Language type (natural or artificial)
        """
        data = []
        for lang in languages:
            point = (1 - lang.get_informativity(),
                    lang.get_complexity(),
                    lang.get_naturalness(),
                    "natural" if lang.is_natural() else "artificial")
            data.append(point)

        data = pd.DataFrame(
            data=data,
            columns=[
                "comm_cost",
                "complexity",
                "naturalness",
                "Language",
            ],
        )

        # Pandas confused by mixed types int and string, so convert back.
        data[["comm_cost", "complexity", "naturalness"]] = data[
            ["comm_cost", "complexity", "naturalness"]
        ].apply(pd.to_numeric)

        return data

    def get_tradeoff_plot(self) -> pn.ggplot:
        """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

        Returns:
            - plot: a plotnine 2D plot of the trade-off.
        """
        data = self.get_dataframe(self.get_languages())
        pareto_df = self.get_dataframe(self.get_dominating_languages())
        plot = (
            pn.ggplot(data=data, mapping=pn.aes(x="comm_cost", y="complexity"))
            + pn.scale_x_continuous(limits=[0, 1])
            + pn.geom_jitter(
                stroke=0,
                alpha=1,
                width=0.00,
                height=0.00,
                # mapping=pn.aes(size="Language", shape="Language", fill="Language"),
                mapping=pn.aes(size="Language", shape="Language", color="naturalness"),
            )
            + pn.geom_line(size=1, data=pareto_df)
            + pn.xlab("Communicative cost of languages")
            + pn.ylab("Complexity of languages")
            + pn.scale_color_cmap("cividis")
        )
        return plot

    def set_languages(self, langs: list[Language]):
        self._languages = langs

    def get_languages(self) -> list[Language]:
        return self._languages

    def set_dominating_languages(self, doms: list[Language]):
        self._dominating_languages = doms

    def get_dominating_languages(self) -> list[Language]:
        return self._dominating_languages
