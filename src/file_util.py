import os
import yaml
from modal_meaning import Modal_Meaning_Space
from modal_language import Modal_Expression

# save paths
# I have a design decision to make. Either I fully specify the fullpath every time, or assume the existence of certain directory structure for the project.
# If the former, src code simplifies but experiment replication code complicates.
# If the latter, the structure of one experiment takes on a kind of (predictable) independence.

# path_to_save_meaning_space: 'output/main_results/meaning_space.yml'
# path_to_save_expressions: 'expresions.yml'
# path_to_save_artificial_languages: 'output/main_results/languages/artificial.yml'
# path_to_save_natural_languages: 'output/main_results/languages/natural.yml'
# path_to_save_frontier: 'output/main_results/languages/frontier.yml'
# dir_path_to_save_analysis: 'output/main_results/languages/analysis'


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

def save_space(fn, space: Modal_Meaning_Space):
    """Saves the modal meaning space to a .yml file."""
    space = {'forces': space.forces, 'flavors': space.flavors}
    with open(fn, 'w') as outfile:
        yaml.dump(space, outfile)

def load_space(fn: str)->Modal_Meaning_Space:
    """Read and the Modal_Meaning_Space object for the experiment saved in a .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    return Modal_Meaning_Space(d['forces'], d['flavors'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Expressions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_expressions(fn, expressions: list[Modal_Expression]):
    """Saves the set of all possible modal expressions to a .yml file."""
    expressions = [{
        'form': e.get_form(),
        'meaning': e.get_meaning().get_points(),
        'lot_exp': e.get_lot_expression(),
        }
         for e in expressions]
    with open(fn, 'w') as outfile:
        yaml.dump(expressions, outfile)

def load_expressions(fn):
    """Loads the set of modal expressions from the specified .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    expressions = [
        Modal_Expression(x['form'], x['meaning'], x['lot_exp']) for x in d
    ]
    return expressions