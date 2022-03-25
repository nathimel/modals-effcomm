import yaml
from modals.modal_meaning import Modal_Meaning_Space, Modal_Meaning
from modals.modal_language import Modal_Expression, Modal_Language

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
        yaml.safe_dump(space, outfile)

def load_space(fn: str)->Modal_Meaning_Space:
    """Read and the Modal_Meaning_Space object for the experiment saved in a .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    return Modal_Meaning_Space(d['forces'], d['flavors'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Expressions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_expressions(fn, expressions: list[Modal_Expression]):
    """Saves the set of all possible modal expressions to a .yml file.
    
    Requires expressions to be nonempty in order to save data about the modal meaning space.
    """
    if not expressions:
        raise ValueError("Cannot save an empty list of modal expressions.")

    space = expressions[0].get_meaning().get_meaning_space()
    expressions = [{
        'form': e.get_form(),
        'meaning': e.get_meaning().get_points(),
        'lot_exp': e.get_lot_expression(),
        }
         for e in expressions]
    struct = {
        'forces': space.forces, 
        'flavors': space.flavors, 
        'expressions': expressions
    }

    with open(fn, 'w') as outfile:
        yaml.safe_dump(struct, outfile)

def load_expressions(fn) -> list[Modal_Expression]:
    """Loads the set of modal expressions from the specified .yml file."""
    with open(fn, "r") as stream:
        d = yaml.safe_load(stream)
    (forces, flavors) = d['forces'], d['flavors']
    expressions = d['expressions']
    expressions = [
        Modal_Expression(
            x['form'], 
            Modal_Meaning(
                x['meaning'], 
                Modal_Meaning_Space(forces, flavors)),
            x['lot_exp']) 
        for x in expressions
    ]
    return expressions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Languages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_languages(fn, languages: list[Modal_Language]):
    """Saves a list of modal languages to a .yml file."""
    langs = [x.yaml_rep() for x in languages]
    with open(fn, "w") as outfile:
        yaml.safe_dump(langs, outfile)

def load_languages(fn) -> list[Modal_Language]:
    """Loads a list of modal languages from a .yml file."""
    with open(fn, "r") as stream:
        expressions = yaml.safe_load(stream)        
    langs = [
        Modal_Language(
            Modal_Expression(
                form=e['form'],
                meaning=e['meaning'],
                lot_expression=e['lot'],
            )
            for e in expressions
        ) for expressions in langs
    ]
    return langs