"""Create all directories for an experiment specified in the main config file recursively if they don't exist already."""

import sys
from misc.file_util import load_configs, make_path

def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/create_folers.py path_to_config_file")
        raise TypeError()  # TODO: create an actual error class for the package

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

    for file_key in configs['file_paths']:
        if file_key != "data":
            make_path(configs['file_paths'][file_key])


if __name__ == "__main__":
    main()