"""A program to build the modal meaning space for an efficient communication experiment.

    Load the configurations from the config.yml specified in command-line args, and automaticaly create modal force and flavor names if none specified. Save the modal meaning space to a .yml file for use in the rest of the experiment.

"""

import sys
from modals.modal_meaning import ModalMeaningSpace
from misc.file_util import load_configs, save_space


def build_default_force_names(num_forces: int):
    """Construct default names for the modal forces.

    Args:
        - num_forces: an integer representing the number of possible modal force distinctions in a language
    Returns:
        - force_names: a set of the default modal force names
    """
    force_names = set(["Q_%d" % (i + 1) for i in range(num_forces)])
    return force_names


def build_default_flavor_names(num_flavors: int):
    """Construct default names for the modal flavors.

    Args:
        - num_forces: an integer representing the number of possible modal flavor distinctions in a language
    Returns:
        - flavor_names: a set of the default modal flavor names
    """
    flavor_names = set(["f_%d" % (i + 1) for i in range(num_flavors)])
    return flavor_names


def get_force_flavor_names(
    num_forces: int, num_flavors: int, force_names=None, flavor_names=None
) -> set:
    """
    Loads the number and names of expressible modal forces and modal flavors (conversational backgrounds) from the config file. Constructs names for
    the meanings if all force and flavor names not fully specified.

    Args:
        - forces: an integer of the number of modal forces.
        - flavors: an integer of the number of modal flavors.
        - force_names: list of the names of the modal forces.
        - flavor_names: list of the names of the modal flavors.

    Returns:
        - force_names: list of (possibly auto-generated) names of the modal forces.
        - flavor_names: list of (possibly auto-generated) names of the modal flavors.
    """
    if num_forces < 1 or num_flavors < 1:
        raise ValueError("The analysis requires at least one force and flavor")

    # Construct default names for the meaning points
    if not force_names:
        force_names = build_default_force_names(num_forces)
    if not flavor_names:
        flavor_names = build_default_flavor_names(num_flavors)

    if num_forces != len(force_names):
        raise ValueError(
            f"The list of force names must be equal in size to the number of expressible modal forces, or else empty. num_forces={num_forces}, len(force_names)={len(force_names)}"
        )

    if num_flavors != len(flavor_names):
        raise ValueError(
            f"The list of flavor names must be equal in size to the number of expressible modal flavors, or else empty. num_flavors={num_flavors}, len(flavor_names)={len(flavor_names)}"
        )

    return (force_names, flavor_names)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/build_meaning_space.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Building modal meaning space ...", sep=" ")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    path_to_save_meaning_space = configs["file_paths"]["meaning_space"]

    forces, flavors = get_force_flavor_names(
        configs["num_forces"],
        configs["num_flavors"],
        configs["force_names"],
        configs["flavor_names"],
    )
    space = ModalMeaningSpace(forces, flavors)
    save_space(path_to_save_meaning_space, space)

    print("done.")


if __name__ == "__main__":
    main()
