import sys
from misc import file_util
from modals.modal_meaning import generate_meaning_distributions
from altk.effcomm.information import get_ib_curve


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/compute_ib_curve.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Computing IB curve ...")

    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)
    curve_fn = configs["file_paths"]["ib_curve"]
    space_fn = configs["file_paths"]["meaning_space"]
    prior_fn = configs["file_paths"]["prior"]

    space = file_util.load_space(space_fn)
    prior = space.prior_to_array(file_util.load_prior(prior_fn))
    meaning_dists = generate_meaning_distributions(space)

    curve_points = get_ib_curve(
        prior=prior,
        meaning_dists=meaning_dists,
        curve_type="comm_cost",
    )

    file_util.save_ib_curve(curve_fn, curve_points)


if __name__ == "__main__":
    main()
