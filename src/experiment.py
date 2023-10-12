import os
import torch

import pandas as pd

from misc.file_util import get_original_fp
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language_of_thought import ModalLOT


def random_stochastic_matrix(shape: tuple[int], beta: float = 1e-2):
    """Generate a random stochastic matrix using energy-based initialization, where lower `beta` -> more uniform initialization."""
    energies = beta * torch.randn(*shape)
    return torch.softmax(energies, dim=-1)

class Experiment:
    """A simple data structure to contain initialized constructs for effcomm experiment, i.e. universe, prior, complexity and informativeness measures, etc."""

    def __init__(
        self,
        universe: ModalMeaningSpace,
        lot_negation: bool = True,
        ) -> None:
        
        self.universe = universe
        self.lot_negation = lot_negation
        self.mlot = ModalLOT(self.universe, self.lot_negation)
        self.meanings = [x for x in self.universe.generate_meanings()]

    
    @classmethod
    def from_hydra(cls, config, *args, **kwargs):
        """Automatically construct an effcomm experiment from a hydra config."""

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
        # breakpoint()
        universe = ModalMeaningSpace.from_dataframe(referents_df)

        # Check prior is valid distribution
        prior = torch.from_numpy(universe.prior_numpy()).float()
        if not torch.isclose(prior.sum(), torch.tensor([1.0])):
            raise Exception(f"Prior does not sum to 1.0. (sum={prior.sum()})")
        
        return cls(
            universe,
            config.experiment.effcomm.comp.lot_negation,
        )