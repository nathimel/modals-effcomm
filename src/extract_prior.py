"""Script for estimating probability distribution over modal meaning points from a dataset."""
import sys
from misc import file_util


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Estimating prior...")

    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)
    prior_fn = configs["file_paths"]["prior"]

    space = file_util.load_space(configs["file_paths"]["meaning_space"])

    # Dummy is uniform now, will test others later
    prior = {point.name: 1 / len(space) for point in space.referents}

    file_util.save_prior(prior_fn, prior)

    print("done.")


if __name__ == "__main__":
    main()
