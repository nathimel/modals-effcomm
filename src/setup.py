"""Minimal script to check that basic construction of the experiment works. Useful to run before any real steps."""

import hydra
import plotnine as pn
import pandas as pd
from omegaconf import DictConfig

from misc.file_util import set_seed
from experiment import Experiment


def plot_pointwise_inf_weights(exp: Experiment) -> pn.ggplot:
    """Visualize the pointwise weights induced by the prior p(meaning) and the utility u(meaning, meaning')."""
    df = pd.DataFrame(
        [
            # Referent, Referent, Weight
            (str(ref), str(ref_), exp.prior[idx] * exp.utility(ref, ref_))
            for ref_ in exp.universe
            for idx, ref in enumerate(exp.universe)
        ],
        columns=["ref", "ref_", "weight"],
    )

    return (
        pn.ggplot(df)
        + pn.geom_tile(pn.aes(x="ref_", y="ref", fill="weight"))
        + pn.ylab("Speaker meaning")
        + pn.xlab("Listener meaning")
        + pn.theme(axis_text_x=pn.element_text(angle=45))
    )


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    exp = Experiment(config)
    plot_pointwise_inf_weights(exp).save(
        "pointwise_inf_weights.png", width=10, height=10, dpi=300
    )


if __name__ == "__main__":
    main()
