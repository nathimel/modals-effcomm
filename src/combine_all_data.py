"""Script to compile all data from sweeps into one dataframe for easy analysis."""

import sys
import omegaconf

import pandas as pd

from pathlib import Path
from tqdm import tqdm


# We don't use the hydra.compose api, since we can't use sweeps with that anyways. Instead, we literally build a giant dataframe of all outputs in multirun.

def main():

    if len(sys.argv) != 2:
        print("Usage: python src/combine_all_data.py. PATH_TO_ALL_DATA \nThis script does not use hydra; do not pass overrides.")
        sys.exit(1)

    # Where to save the giant dataframe
    save_fn = sys.argv[1]

    # helper
    concat = lambda list_of_dfs: pd.concat(list_of_dfs, axis=0, ignore_index=True)

    config_fp = "conf/config.yaml"
    cfg = omegaconf.OmegaConf.load(config_fp)


    # Assume we're interested in multisweeps
    # root_dir = cfg.filepaths.hydra_sweep_root
    # Though for dev, use outputs
    root_dir = cfg.filepaths.hydra_run_root

    leaf_hydra_cfg_fn = ".hydra/config.yaml"
    overrides_fn = "overrides.yaml"

    # the data produced by analze.py
    data_fn = "analysis/all_data.csv"

    # Collect all the results of individual experiments
    experiment_results = []
    print(f"collecting data from {root_dir}.")
    cfg_fns = list(Path(root_dir).rglob(leaf_hydra_cfg_fn))
    for path in tqdm(cfg_fns, desc=f"collecting {len(cfg_fns)} experiments"):
        leaf_cfg = omegaconf.OmegaConf.load(path)
        run_dir = path.parent.parent.absolute()

        df = pd.read_csv(run_dir / data_fn)

        # Add metadata columns
        df["universe"] = leaf_cfg.experiment.universe
        df["prior"] = leaf_cfg.experiment.effcomm.inf.prior
        df["utility"] = leaf_cfg.experiment.effcomm.inf.utility
        df["agent_type"] = leaf_cfg.experiment.effcomm.inf.agent_type

        # In general there is a lot more metadata we can add, so change as necessary
        experiment_results.append(df)

    all_data = concat(experiment_results)

    # Save
    all_data.to_csv(save_fn, index=False)
    print(f"Saved a dataframe to {save_fn}")    


if __name__ == "__main__":
    main()
