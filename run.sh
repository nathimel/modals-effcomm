#!/bin/sh

# source ~/miniforge3/etc/profile.d/conda.sh
source ~/anaconda3/etc/profile.d/conda.sh
conda activate modals-effcomm

./scripts/run_full_experiment.sh configs/dev_4_4.yml
# ./scripts/run_full_experiment.sh configs/dev_1_4.yml
# ./scripts/run_full_experiment.sh configs/dev_3_3.yml
# ./scripts/run_full_experiment.sh configs/dev_2_5.yml
# ./scripts/run_full_experiment.sh configs/dev.yml
# ./scripts/run_full_experiment.sh configs/main_results.yml

conda deactivate
