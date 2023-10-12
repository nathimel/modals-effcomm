import os
import hydra
import random
import time
import yaml
import numpy as np
import pandas as pd
from typing import Any, Callable
from modals.modal_meaning import ModalMeaningSpace, half_credit, indicator
from modals.modal_language import ModalExpression, ModalLanguage

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Pseudo random
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def set_seed(seed: int) -> None:
    """Sets various random seeds."""
    random.seed(seed)
    np.random.seed(seed)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hydra
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_original_fp(fn: str):
    return os.path.join(hydra.utils.get_original_cwd(), fn)

def get_expressions_fn(config: dict):
    expressions_dir = os.getcwd().replace(
        config.filepaths.leaf_subdir, config.filepaths.expressions_subdir
    )
    expressions_fn = os.path.join(expressions_dir, config.filepaths.expressions)
    return expressions_fn

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def make_path(fn: str) -> None:
    """Creates the path recursively if it does not exist."""
    dirname = os.path.dirname(fn)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        print(f"Created folder {dirname}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def load_configs(fn: str) -> dict:
    """Load the configs .yml file as a dict."""
    with open(fn, "r") as stream:
        configs = yaml.safe_load(stream)
    return configs


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Measures
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def load_utility(name: str) -> Callable:
    """Loads the utility function for the experiment."""
    if name == "indicator":
        return indicator
    elif name == "half_credit":
        return half_credit
    raise ValueError(f"No utility function named {name}.")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Modal Meaning Space
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_space(fn, space: ModalMeaningSpace):
    """Saves the modal meaning space to a .yml file."""
    space = {"forces": space.forces, "flavors": space.flavors}
    with open(fn, "w") as outfile:
        yaml.safe_dump(space, outfile)


def load_space(fn: str) -> ModalMeaningSpace:
    """Read and the ModalMeaningSpace object for the experiment saved in a .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    return ModalMeaningSpace(d["forces"], d["flavors"])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prior
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_prior(fn: str, prior: dict[str, float]) -> None:
    """Save an estimated prior over modal meaning points to a YAML file.

    Args:
        fn: the file to save the probability distribution dict to.

        prior: a dict representing the distribution over meaning points with
            string keys = meaning point names,
            float values = weights e.g. frequencies or probabilities.
    """
    with open(fn, "w") as outfile:
        yaml.safe_dump(prior, outfile)


def load_prior(fn: str) -> dict[str, float]:
    """Load a prior communicative need probability distribution over modal meaning points from a saved YAML file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    d = {
        tuple(key.split("+")): value for key, value in d.items()
    }  # convert from strings to tuples
    return d

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Expressions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_expressions(fn, expressions: list[ModalExpression]):
    """Saves the set of all possible modal expressions to a .yml file.

    Requires expressions to be nonempty in order to save data about the modal meaning space.
    """
    if not expressions:
        raise ValueError("Cannot save an empty list of modal expressions.")

    space = expressions[0].meaning.universe
    expressions = [
        {
            "form": e.form,
            # N.B.: force+flavor string is most readable in YML file
            "meaning": [point.name for point in e.meaning.referents],
            "lot": e.lot_expression,
        }
        for e in expressions
    ]
    data = {
        "forces": space.forces,
        "flavors": space.flavors,
        "expressions": expressions,
    }

    with open(fn, "w") as outfile:
        yaml.safe_dump(data, outfile)


def load_expressions(fn) -> list[ModalExpression]:
    """Loads the set of modal expressions from the specified .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    space = ModalMeaningSpace(d["forces"], d["flavors"])
    expressions = d["expressions"]
    return [ModalExpression.from_yaml_rep(x, space) for x in expressions]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Languages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_languages(
    fn, languages: list[ModalLanguage], id_start: int, kind="", verbose=True
):
    """Saves a list of modal languages to a .yml file.

    Args:
        fn: the str representing the YAML file to dump (overwrite) languages to.

        languages: the list of languages to save.

        id_start: a number representing the total number of languages generated so far in an experiment. When saving natural languages, can be None.

        kind: a string for printing the kind of pool of languages, e.g. 'sampled'

    """
    start = time.time()
    space = languages[0].expressions[0].meaning.universe

    # Do not use a dict, which will lose data from the yaml representation
    langs = list(lang.yaml_rep() for lang in languages)

    data = {
        "forces": space.forces,
        "flavors": space.flavors,
        "id_start": id_start,
        "languages": langs,
    }

    with open(fn, "w") as outfile:
        yaml.safe_dump(data, outfile)

    if kind:
        kind = f" {kind} "
    else:
        kind == " "

    duration = ""
    if verbose:
        duration = time.time() - start
        duration = f"in {duration:.2f} seconds"
    print(f"Saved {len(langs)}{kind}languages {duration}")


def load_languages(fn: str, verbose=True) -> dict[str, Any]:
    """Loads modal languages from a .yml file.

    Args:
        fn: the str of the filename to load languages from.

    Returns:
        a dict of the languages and the id_start, e.g.
        {
            "languages": (a list),
            "id_start": (an int or None),
        }
    """
    start = time.time()

    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    space = ModalMeaningSpace(d["forces"], d["flavors"])
    id_start = d["id_start"]

    languages = d["languages"]
    result = {
        "languages": [
            ModalLanguage.from_yaml_rep(name, data, space)
            for language in languages  # a list of dicts
            for name, data in language.items()  # a dict with one entry
        ],
        "id_start": id_start,
    }
    duration = ""
    if verbose:
        duration = time.time() - start
        duration = f"in {duration:.2f} seconds"
        print(f"Loaded {len(result['languages'])} languages {duration}")
    return result


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
