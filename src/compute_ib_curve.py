
import ib_measures
import sys
import numpy as np
from ib_measures import DEFAULT_DECAY, DEFAULT_UTILITY
from misc import file_util
from modals.modal_meaning import ModalMeaningSpace
from embo import InformationBottleneck

def get_curve(
    prior: np.ndarray,
    space: ModalMeaningSpace,
    decay: float,
    utility: str,
) -> np.ndarray:
    """Compute the IB curve bound (I[M:W] vs. I[W:U]) for a given semantic space. We use the embo package, which does not allow one to specify the number of betas, which means some interpolation might be necessary later.

    Args:
        prior: array of shape `|meanings|`

        space: the ModalMeaningSpace on which meanings are defined

        decay: parameter for meaning distribution p(u|m) generation

        utility: parameter for meaning distribution p(u|m) generation

    Returns:
        an array of shape `(num_points, 2)` representing the list of (comm_cost, complexity) points on the information plane.
    """
    conditional_pum = ib_measures.generate_meaning_distributions(space, decay, utility)
    joint_pmu = ib_measures.joint(conditional_pum, prior) # P(u) = P(m)
    I_mu = ib_measures.MI(joint_pmu)

    # I[M:W], I[W:U], H[W], beta
    I_mw, I_wu, _, _ = InformationBottleneck(pxy=joint_pmu).get_bottleneck()

    points = np.array(list(zip(I_mu - I_wu, I_mw))) # expected kl divergence, complexity
    # points = np.array(list(zip(I_wu, I_mw))) # informativity, complexity

    return points

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
    lang_size = configs["lang_size"]
    space = file_util.load_space(space_fn)
    prior = space.prior_to_array(file_util.load_prior(prior_fn))

    curve_points = get_curve(
        prior=prior,
        space=space,
        decay=DEFAULT_DECAY,
        utility=DEFAULT_UTILITY,
    )

    file_util.save_ib_curve(curve_fn, curve_points)

if __name__ == "__main__":
    main()