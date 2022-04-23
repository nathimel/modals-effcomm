import os
import yaml
import random
import numpy as np
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_language import ModalExpression, ModalLanguage

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Psuedo random
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def set_seed(seed: int) -> None:
    """Sets various random seeds. """
    random.seed(seed)
    np.random.seed(seed)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def make_path(fn: str) -> None:
    """Creates the path recursively if it does not exist.
    """
    dirname = os.path.dirname(fn)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_configs(fn: str)->dict:
    """Load the configs .yml file as a dict."""
    with open(fn, "r") as stream:
        configs = yaml.safe_load(stream)
    return configs

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Modal Meaning Space
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_space(fn, space: ModalMeaningSpace):
    """Saves the modal meaning space to a .yml file."""
    space = {'forces': space.forces, 'flavors': space.flavors}
    with open(fn, 'w') as outfile:
        yaml.safe_dump(space, outfile)

def load_space(fn: str)->ModalMeaningSpace:
    """Read and the ModalMeaningSpace object for the experiment saved in a .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    return ModalMeaningSpace(d['forces'], d['flavors'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Expressions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_expressions(fn, expressions: list[ModalExpression]):
    """Saves the set of all possible modal expressions to a .yml file.
    
    Requires expressions to be nonempty in order to save data about the modal meaning space.
    """
    if not expressions:
        raise ValueError("Cannot save an empty list of modal expressions.")

    space = expressions[0].get_meaning().get_meaning_space()
    expressions = [{
        'form': e.get_form(),
        'meaning': e.get_meaning().get_points(),
        'lot': e.get_lot_expression(),
        }
         for e in expressions]
    data = {
        'forces': space.forces, 
        'flavors': space.flavors, 
        'expressions': expressions
    }

    with open(fn, 'w') as outfile:
        yaml.safe_dump(data, outfile)

def load_expressions(fn) -> list[ModalExpression]:
    """Loads the set of modal expressions from the specified .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    space = ModalMeaningSpace(d['forces'], d['flavors'])
    expressions = d['expressions']
    return [
        ModalExpression.from_yaml_rep(x, space) for x in expressions
        ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Languages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_languages(fn, languages: list[ModalLanguage]):
    """Saves a list of modal languages to a .yml file."""
    space = languages[0].get_expressions()[0].get_meaning().get_meaning_space()

    # Do not use a dict, which will lose data from the yaml representation
    langs = list(lang.yaml_rep() for lang in languages)

    data = {
        'forces': space.forces, 
        'flavors': space.flavors, 
        'languages': langs,
    }

    with open(fn, 'w') as outfile:
        yaml.safe_dump(data, outfile)

    print("Saved {} languages".format(len(langs)))

def load_languages(fn) -> list[ModalLanguage]:
    """Loads a list of modal languages from a .yml file."""

    # TODO: use tqdm 

    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)

    space = ModalMeaningSpace(d['forces'], d['flavors'])
    languages = d['languages']
    return [
        ModalLanguage.from_yaml_rep(
            name, data, space) 
            for name, data in languages
        ]
