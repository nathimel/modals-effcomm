#!/bin/sh

source ~/miniforge3/etc/profile.d/conda.sh
conda activate modals-effcomm

./scripts/main_results.sh configs/main_results/config.yml

conda deactivate
