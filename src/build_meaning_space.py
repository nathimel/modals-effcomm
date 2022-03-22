"""A program to build the modal meaning space for an efficient communication experiment."""

import sys
import yaml
from modal_meaning import Modal_Meaning_Point, Modal_Meaning_Space
from file_util import load_configs

def build_default_force_names(num_forces: int):
    """Construct default names for the modal forces.

    Args: 
        num_forces: an integer representing the number of possible modal force distinctions in a language
    Returns:
        force_names: a set of the default modal force names
    """
    force_names = set(["Q_%d" % (i + 1) for i in range(num_forces)])
    return force_names

def build_default_flavor_names(num_flavors: int):
    """Construct default names for the modal flavors.

    Args: 
        num_forces: an integer representing the number of possible modal flavor distinctions in a language
    Returns:
        flavor_names: a set of the default modal flavor names
    """
    flavor_names = set(["f_%d" % (i + 1) for i in range(num_flavors)])
    return flavor_names


def fill_meaning_point_names(num_forces: int, num_flavors: int, force_names=None, flavor_names=None)->set:
    """
    Loads the number and names of expressible modal forces and modal flavors (conversational backgrounds) from the config file. Constructs names for
    the meanings if all force and flavor names not fully specified.

    Args:
        forces: an integer of the number of modal forces.
        flavors: an integer of the number of modal flavors.
        force_names: list of the names of the modal forces.
        flavor_names: list of the names of the modal flavors.

    Returns: 
        point_names: a set of the meaning point names for the meaning space.
    """
    if num_forces < 1 or num_flavors < 1:
        raise ValueError("The analysis requires at least one force and flavor")

    # Construct default names for the meaning points
    if not force_names:
        force_names = build_default_force_names(num_forces)
    if not flavor_names:
        flavor_names = build_default_flavor_names(num_flavors)        

    if num_forces != len(force_names):
        raise ValueError("The list of force names must be equal in size to the number of expressible modal forces, or else empty.")
    if num_flavors != len(flavor_names):
        raise ValueError("The list of flavor names must be equal in size to the number of expressible modal flavors, or else empty.")

    point_names = set()
    # the set of modal meanings is the Cartesian product of forces, flavors
    for force in force_names:
        for flavor in flavor_names:
            name = "{0}+{1}".format(force, flavor)
            point_names.add(name)

    return point_names

def save_space(fn, space: Modal_Meaning_Space):
    """Saves the modal meaning space to a .yml file."""
    with open(fn, 'w') as outfile:
        yaml.dump(space, outfile)

def main():
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/build_meaning_space.py path_to_config_file path_to_save_meaning_space")
        sys.exit(1)

    config_fn = sys.argv[1]
    path_to_save_meaning_space = sys.argv[2]
    configs = load_configs(config_fn)
    
    point_names = fill_meaning_point_names(
        configs['num_forces'], 
        configs['num_flavors'], 
        configs['force_names'], 
        configs['flavor_names']
    )
    space = Modal_Meaning_Space(point_names)
    save_space(path_to_save_meaning_space, space)

if __name__ == "__main__":
    main()
