#!/bin/sh

source ~/miniforge3/etc/profile.d/conda.sh
# source ~/anaconda3/etc/profile.d/conda.sh
conda activate modals-effcomm

./scripts/run_full_experiment.sh configs/dev.yml
# ./scripts/run_full_experiment.sh configs/main_results.yml

conda deactivate
