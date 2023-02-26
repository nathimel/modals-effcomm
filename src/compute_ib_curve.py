import sys
from misc import file_util
from measure_ib_tradeoff import DEFAULT_DECAY, DEFAULT_UTILITY
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
    utility = file_util.load_utility(DEFAULT_UTILITY)

    space = file_util.load_space(space_fn)
    prior = space.prior_to_array(file_util.load_prior(prior_fn))

    curve_points = get_ib_curve(
        prior=prior,
        space=space,
        decay=DEFAULT_DECAY,
        cost=lambda x, y: 1 - utility(x, y),
        curve_type="comm_cost",
    )

    file_util.save_ib_curve(curve_fn, curve_points)


if __name__ == "__main__":
    main()
