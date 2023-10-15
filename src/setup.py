"""Minimal script to check that basic construction of the experiment works. Useful to run before any real steps."""

import hydra
from omegaconf import DictConfig

from misc.file_util import set_seed
from experiment import Experiment


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    exp = Experiment(config)

if __name__ == "__main__":
    main()
