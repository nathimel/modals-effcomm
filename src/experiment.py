import os
import torch

import pandas as pd

from typing import Any
from misc.file_util import get_original_fp, load_expressions, load_languages, get_subdir_fn, save_expressions, save_languages, get_subdir_fn_abbrev
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language_of_thought import ModalLOT
from omegaconf import DictConfig

def random_stochastic_matrix(shape: tuple[int], beta: float = 1e-2):
    """Generate a random stochastic matrix using energy-based initialization, where lower `beta` -> more uniform initialization."""
    energies = beta * torch.randn(*shape)
    return torch.softmax(energies, dim=-1)

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

            load_files: the list of files to load when upon construction. By default is empty for efficiency, but possible values are all keys of `self.filenames`, i.e. `["expressions", "artificial_languages", "natural_languages", "dominant_languages"]`
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
                f"The value of config.game.universe must be the number of natural number states (int) or the name of a file located at data/universe (str). Received type: {type(universe)}."
            )
        # Set Prior
        prior = config.experiment.effcomm.inf.prior
        if isinstance(prior, str):
            fn = get_original_fp(config.filepaths.prior_fn)
            prior_df = pd.read_csv(fn)
        else:
            prior_df = referents_df.copy()[["name"]]
            prior_df["probability"] = random_stochastic_matrix(
                (len(referents_df),), beta=10**prior
            ).tolist()
        
        # Construct Universe
        universe = ModalMeaningSpace.from_dataframe(referents_df)

        # Check prior is valid distribution
        prior = torch.from_numpy(universe.prior_numpy()).float()
        if not torch.isclose(prior.sum(), torch.tensor([1.0])):
            raise Exception(f"Prior does not sum to 1.0. (sum={prior.sum()})")

        ######################################################################
        # Initialize experiment parameters
        ######################################################################

        self.config = config
        self.universe = universe
        self.lot_negation = config.experiment.effcomm.comp.lot_negation
        self.mlot = ModalLOT(self.universe, self.lot_negation)
        self.meanings = [x for x in self.universe.generate_meanings()]

        self.filenames = {
            "expressions": None,
            "artificial_languages": None,
            "natural_languages": None,
            "dominant_languages": None,
        }
        self.expressions = None
        self.artificial_languages = None
        self.natural_languages = None
        self.dominant_languages = None

        self.load_files(load_files)


    def load_files(self, files: list[str]) -> None:

        for key in files:

            if key not in self.filenames:
                raise KeyError(f"The file {key} cannot be loaded because it is not one of {self.filenames.keys()}.")

            filename = getattr(self.config.filepaths, key)
            result = None
            # Load expressions from file
            if key == "expressions":
                fullpath = get_subdir_fn_abbrev(self.config, "expressions_subdir", key)
                if os.path.exists(fullpath):
                    result = load_expressions(fullpath)
                else:
                    print(f"Filepath {fullpath} does not exist yet.")
            # Load language from file
            else:
                fullpath = get_subdir_fn_abbrev(self.config, "languages_subdir", key)
                if os.path.exists(fullpath):
                    result = load_languages(fullpath)
                else:
                    print(f"Filepath {fullpath} does not exist yet.")
            setattr(self, key, result)

    def write_files(self, files: list[str], *args, **kwargs) -> None:

        for key in files:

            if key not in self.filenames:
                raise KeyError(f"The file {key} cannot be written to because it is not one of {self.filenames.keys()}.")

            # Load expressions from file
            if key == "expressions":
                fullpath = get_subdir_fn_abbrev(self.config, "expressions_subdir", key)
                data = getattr(self, key)
                if data is not None and self.config.experiment.overwrite_expressions:
                    save_expressions(fullpath, data)
                else:
                    print(f"File {fullpath} already exists.")

            # Load language from file
            else:
                fullpath = get_subdir_fn_abbrev(self.config, "languages_subdir", key)
                data = getattr(self, key)
                if data is not None and self.config.experiment.overwrite_languages:
                    save_languages(fullpath, data, *args, **kwargs)
                else:
                    print(f"File {fullpath} already exists.")
