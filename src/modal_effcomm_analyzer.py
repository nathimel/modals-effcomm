"""Classes and functinos to analyze the simplicity/informativeness trade-off for modals."""

import sys
import pygmo
import numpy as np
import plotnine as pn
import pandas as pd

from scipy import interpolate
from scipy.spatial.distance import cdist
from altk.effcomm.analysis import EffComm_Analyzer
from modals.modal_language import Modal_Language, degree_iff
from modals.modal_measures import Modal_Complexity_Measure, Modal_Informativity_Measure

class Modal_EffComm_Analyzer(EffComm_Analyzer):

    def __init__(
        self,
        languages: list[Modal_Language], 
        comp_measure: Modal_Complexity_Measure, 
        inf_measure: Modal_Informativity_Measure
    ):
        super().__init__(languages, comp_measure, inf_measure)


    def measure_languages(self) -> None:
        """

        Returns: 
            tuple[list[Language]]: a pair of the dominating_languages and all_languages.
        """
        langs = self.get_languages()
        # measure simplicity, informativity, and semantic universals
        for lang in langs:
            lang.set_complexity(
                self.comp_measure.language_complexity(lang)
                )
            lang.set_informativity(
                self.inf_measure.language_informativity(lang)
                )
            lang.set_iff(degree_iff(lang))

        # measure relative pareto optimality
        dominating_indices = pygmo.non_dominated_front_2d(
            list(zip(
                [1 - lang.get_informativity() for lang in langs],
                [lang.get_complexity() for lang in langs]
                )
            ))

        dominating_languages = [langs[i] for i in dominating_indices]
        self.set_languages(langs)
        self.set_dominating_languages(dominating_languages)
        self.measure_closeness(self.interpolate_data())        

    def get_results(self) -> tuple:
        """Get the main plot, dataframe, report of semantic univeral correlation with optimality.
        """
        return [self.get_df(self.get_languages()), self.get_plot()]

    def get_plot(self) -> pn.ggplot:
        """Create the main plotnine plot for the communicative cost, complexity trade-off for the experiment.

        Returns: 
            - plot: a plotnine 2D plot of the trade-off.
        """
        data = self.get_df(self.get_languages())
        pareto_df = self.get_df(self.get_dominating_languages())
        plot = (
            pn.ggplot(data=data, mapping=pn.aes(x="comm_cost", y="complexity"))
            + pn.scale_x_continuous(limits=[0, 1])
            + pn.geom_jitter(
                stroke=0,
                alpha=1,
                width=0.00,
                height=0.00,
                # mapping=pn.aes(size="Language", shape="Language", fill="Language"),
                mapping=pn.aes(size="Language", shape="Language", color="iff"),
            )
            + pn.geom_line(size=1, data=pareto_df)
            + pn.xlab("Communicative cost of languages")
            + pn.ylab("Complexity of languages")
            + pn.scale_color_cmap("cividis"))
        return plot

    def get_df(self, languages) -> pd.DataFrame:
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
        data = np.array([
                (1 - lang.get_informativity(),
                lang.get_complexity(),
                lang.get_iff(),
                'natural' if lang.is_natural() else 'artificial'
                ) for lang in languages
            ])
        data = pd.DataFrame(
            data=data, 
            columns=[
            'comm_cost', 
            'complexity',
            'iff',
            'Language',
            ])

        # Pandas confused by mixed types int and string, so convert back.
        data[['comm_cost', 'complexity', 'iff']] = data[['comm_cost', 'complexity', 'iff']].apply(pd.to_numeric)

        return data

    def measure_closeness(self, pareto_points: list):
        """Measure the Pareto optimality of each language by measuring its Euclidean closeness to the frontier.
        """
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
            lang.set_optimality(min_distances[i])
        self.set_languages(langs)

    def interpolate_data(self) -> np.ndarray:
        """Interpoloate the points yielded by the pareto optimal languages into a continuous (though not necessarily smooth) curve.
        """
        dom_cc = []
        dom_comp = []
        for lang in self.get_dominating_languages():
            dom_cc.append(1 - lang.get_informativity())
            dom_comp.append(lang.get_complexity())

        values = list(set(zip(dom_cc, dom_comp)))
        pareto_x, pareto_y = list(zip(*values))

        interpolated = interpolate.interp1d(pareto_x, pareto_y, fill_value="extrapolate")
        pareto_costs = np.linspace(0, 1.0, num=5000)
        pareto_complexities = interpolated(pareto_costs)
        pareto_points = np.array(list(zip(pareto_costs, pareto_complexities)))
        return pareto_points
