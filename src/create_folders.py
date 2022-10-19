"""Create all directories for an experiment specified in the main config file recursively if they don't exist already."""

import sys
from misc.file_util import load_configs, make_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/create_folers.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)

    for file_key in configs["file_paths"]:
        if file_key != "data" and file_key != "modality_corpus":
            if file_key == "analysis":
                for file_key_ in configs["file_paths"][file_key]:
                    make_path(configs["file_paths"][file_key][file_key_])
            else:
                make_path(configs["file_paths"][file_key])


if __name__ == "__main__":
    main()
