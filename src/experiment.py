import os

import numpy as np
import pandas as pd

from altk.effcomm.informativity import informativity
from altk.language.grammar import Grammar, Rule

from typing import Any
from misc.file_util import get_original_fp, load_expressions, load_languages, save_expressions, save_languages, get_subdir_fn_abbrev
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_utility_measures import half_credit, indicator, utility_func_from_csv
from modals.modal_language_of_thought import ModalLOT
from modals.modal_measures import language_complexity
from omegaconf import DictConfig

from scipy.special import softmax

def random_stochastic_matrix(shape: tuple[int], beta: float = 1e-2):
    """Generate a random stochastic matrix using energy-based initialization, where lower `beta` -> more uniform initialization."""
    energies = beta * np.random.randn(*shape)
    return softmax(energies, axis=-1)

class Experiment:
    """A simple data structure to contain initialized constructs for effcomm experiment, i.e. universe, prior, complexity and informativeness measures, etc."""

    def __init__(
        self,
        config: DictConfig,
        load_files: list[str] = [],
        ) -> None:
        """Construct an experiment object, which can contain all the necessary data for running the computational experiment measuring efficiency of modal languages.

        Args:
            config: a Hydra config

            load_files: the list of files to load when upon construction. By default is empty for efficiency, but possible values are all keys of `self.paths`, i.e. `["expressions", "artificial_languages", "natural_languages", "dominant_languages"]`
        """

        ######################################################################
        # Construct prior and universe from config file
        ######################################################################

        # Load prior and universe
        universe = None
        prior = None

        # Initialize Universe, default is a list of integers
        if isinstance(config.experiment.universe, str):
            fn = get_original_fp(config.filepaths.universe_fn)
            referents_df = pd.read_csv(fn)
        else:
            raise ValueError(
                f"The value of config.experiment.universe must be the name of a file located at data/universe (str). Received type: {type(universe)}."
            )
        # Set Prior
        prior = config.experiment.effcomm.inf.prior
        if isinstance(prior, str):
            fn = get_original_fp(config.filepaths.prior_fn)
            prior_df = pd.read_csv(fn)
        else: # is an int or float
            prior_df = referents_df.copy()[["name"]]
            prior_df["probability"] = random_stochastic_matrix(
                (len(referents_df),), beta=prior
            ).tolist()
        
        # Construct Universe
        universe = ModalMeaningSpace.from_dataframe(referents_df)

        # Check prior is valid distribution
        prior = universe.prior_numpy()
        if not np.isclose(prior.sum(), 1.0):
            raise Exception(f"Prior does not sum to 1.0. (sum={prior.sum()})")

        # Construct the utility function for the experiment        
        utility = None
        name = config.experiment.effcomm.inf.utility
        fn = get_original_fp(config.filepaths.utility_fn)
        if name == "indicator":
            utility = indicator
        elif name == "half_credit":
            utility = half_credit
        elif os.path.exists(fn):
            utility = utility_func_from_csv(fn)
        else:
            raise ValueError(f"Invalid utility function name. You must pass either 'indicator' or 'half_credit' or the name of a file located at the data/utility folder.")
        
        ######################################################################
        # Initialize experiment parameters
        ######################################################################

        modal_grammar = Grammar(bool)
        # basic propositional logic
        modal_grammar.add_rule(Rule("and", bool, (bool, bool), lambda p1, p2: p1 and p2))
        modal_grammar.add_rule(Rule("or", bool, (bool, bool), lambda p1, p2: p1 or p2))
        modal_grammar.add_rule(Rule("not", bool, (bool,), lambda p1: not p1))
        # primitive features for forces

        # TODO: why did looping over `forces` and `flavors` not work here?
        # I think this has to do with call-by-name vs call-by-value and lambdas and stuff...
        modal_grammar.add_rule(
            Rule("strong", bool, None, lambda point: point.force == "strong")
        )
        modal_grammar.add_rule(Rule("weak", bool, None, lambda point: point.force == "weak"))
        # primitive features for flavors
        modal_grammar.add_rule(
            Rule("epistemic", bool, None, lambda point: point.flavor == "epistemic")
        )
        modal_grammar.add_rule(
            Rule("deontic", bool, None, lambda point: point.flavor == "deontic")
        )
        modal_grammar.add_rule(
            Rule("circumstantial", bool, None, lambda point: point.flavor == "circumstantial")
        )

        self.config = config
        self.universe = universe
        self.prior = universe._prior
        self.lot_negation = config.experiment.effcomm.comp.lot_negation
        self.mlot = ModalLOT(self.universe, self.lot_negation)
        self.meanings = [x for x in self.universe.generate_meanings()]
        self.grammar = modal_grammar

        # Measures of Complexity and Informativeness
        self.complexity_measure = lambda lang: language_complexity(lang, self.mlot, self.grammar, config)
        self.informativity_measure = lambda lang: informativity(
            language=lang,
            prior=prior,
            utility=utility,
            agent_type=config.experiment.effcomm.inf.agent_type,
        )

        # dict containing absolute paths to language data files
        self.paths = {
            "expressions": None,
            "artificial_languages": None,
            "natural_languages": None,
            "dominant_languages": None,
        }

        # list of ModalExpressions
        self.expressions = None

        # Each a dict of form {"languages": ..., "id_start": ..}
        self.artificial_languages = None
        self.natural_languages = None
        self.dominant_languages = None

        self.load_files(load_files)

    def ensure_paths(self, keys: str) -> None:
        if not all(self.paths[key] is not None for key in keys):
            self.set_filepaths(keys)

    def path_exists(self, path: str, absolute=False) -> bool: 
        """Check whether the absolute path corresponding to the file key exists."""
        path = path if absolute else self.paths[path]
        return os.path.exists(path)

    def set_filepaths(self, keys: list[str]) -> None:
        """Infer the absolute paths of language data filenames relative to hydra interpolations."""
        for key in keys:
            if key not in self.paths:
                raise KeyError(f"The file {key} cannot be loaded because it is not one of {self.paths.keys()}.")

            subdir = "generate_subdir" if key == "expressions" else "languages_subdir"
            self.paths[key] = get_subdir_fn_abbrev(self.config, subdir, key)


    def load_files(self, files: list[str]) -> None:
        """Load language data from filenames."""
        self.ensure_paths(files)

        for key in files:
            if key not in self.paths:
                raise KeyError(f"The file {key} cannot be loaded because it is not one of {self.paths.keys()}.")

            result = None
            loader = load_expressions if key == "expressions" else load_languages
            if self.path_exists(key):
                print(f"Loading {key}...")
                result = loader(self.paths[key])
                print("done.")
            else:
                print(f"Cannot load file {self.paths[key]} because it does not exist; setting Experiment.{key}=None.")
            setattr(self, key, result)

    def write_files(self, files: list[str], kinds = []) -> None:
        """Write the language data contained in the Experiment to the corresponding files."""

        self.ensure_paths(files)

        for i, key in enumerate(files):

            if key not in self.paths:
                raise KeyError(f"The file {key} cannot be written to because it is not one of {self.paths.keys()}.")
            
            fullpath = self.paths[key]
            data = getattr(self, key)
            if data is None:
                print(f"{key} was None; skipping.")

            if key == "expressions":
                saver = save_expressions
                overwrite = self.config.experiment.overwrite_expressions
                save_args = [fullpath, data]
                save_kwargs = dict()
            else:
                saver = save_languages
                overwrite = self.config.experiment.overwrite_languages
                save_args = [fullpath] + list(data.values()) # langs, id_start
                save_kwargs = {"kind":kinds[i]}
            
            if not self.path_exists(key) or overwrite:
                saver(*save_args, **save_kwargs)
            else:
                print(f"File {fullpath} already exists, not overwriting.")

