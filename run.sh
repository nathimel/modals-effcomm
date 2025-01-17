#!/bin/sh

# source ~/miniforge3/etc/profile.d/conda.sh # Local
source ~/anaconda3/etc/profile.d/conda.sh # Patas
conda activate modals-effcomm

# time ./scripts/run_full_experiment.sh configs/dev.yml
# time ./scripts/run_full_experiment.sh configs/salt.yml > outputs/salt/system_output.txt

time ./scripts/run_full_experiment.sh configs/indicator_literal.yml > outputs/indicator_literal/system_output.txt
time ./scripts/run_full_experiment.sh configs/indicator_pragmatic.yml > outputs/indicator_pragmatic/system_output.txt
time ./scripts/run_full_experiment.sh configs/half_credit_literal.yml > outputs/half_credit_literal/system_output.txt
time ./scripts/run_full_experiment.sh configs/half_credit_pragmatic.yml > outputs/half_credit_pragmatic/system_output.txt


# conda deactivate
