"""A program to generate modal expressions for an efficient communication experiment.

Every possible modal meaning that can be expressed by a language is given exactly one expression. This expression is chosen based on a the shortest formula in a language of thought (LoT), which is estimated by a boolean algebra formula minimization heuristic.
"""

import sys
import os
from modals.modal_grammar_enumeration import get_all_expressions
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import ModalExpression
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

from experiment import Experiment

import hydra
from misc.file_util import set_seed
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    # Load parameters for expression generation
    # TODO: consider checking if expressions already exist instead of regenerating every time

    experiment = Experiment(config, load_files=["expressions"])

    if (
        experiment.expressions is not None
        and not config.experiment.overwrites.expressions
    ):
        print(f"Expressions already generated, skipping.")
        return

    if config.experiment.lot_estimation == "ultk":
        print("Evaluating lot expressions via ultk grammar...")
        # TODO: perform systematic comparison of complexities of expressions under both measures
        modal_expressions = get_all_expressions(
            experiment.grammar,
            experiment.universe,
        )

    elif config.experiment.lot_estimation == "homebuilt":
        # Generate lot expressions
        meanings = experiment.meanings
        mdl = experiment.mlot.minimum_lot_description
        print("Evaluating lot expressions via homebuilt heuristic...")
        # Measure expressions for complexity
        with Pool(cpu_count()) as p:
            lot_expressions = list(tqdm(p.imap(mdl, meanings), total=len(meanings)))

        # Check if negation shouldn't be there
        # N.B.: this is old stuff just for debugging
        negation = experiment.lot_negation
        if not negation:
            lot_expressions = [formula for formula in lot_expressions if "-" in formula]
            if len(lot_expressions) != 0:
                raise ValueError(
                    f"Negation shouldn't be in lot but found the following formulae with negation: {lot_expressions}"
                )

        # Save
        modal_expressions = [
            ModalExpression(
                form=f"dummy_form_{i}",
                meaning=meaning,
                lot_expression=lot_expressions[i],
            )
            for i, meaning in enumerate(meanings)
        ]
    else:
        raise ValueError(
            f"Incorrect config for lot_estimation; possible values are 'altk' or 'homebuilt'."
        )

    experiment.expressions = modal_expressions
    experiment.write_files(["expressions"])
    print("done.")


if __name__ == "__main__":
    main()
