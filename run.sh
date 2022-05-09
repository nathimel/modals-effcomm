#!/bin/sh

# source ~/miniforge3/etc/profile.d/conda.sh # Local
source ~/anaconda3/etc/profile.d/conda.sh # Patas
conda activate modals-effcomm

# ./scripts/run_full_experiment.sh configs/dev_4_4.yml
# ./scripts/run_full_experiment.sh configs/dev_1_4.yml
# ./scripts/run_full_experiment.sh configs/dev_3_3.yml
# ./scripts/run_full_experiment.sh configs/dev_2_5.yml
# ./scripts/run_full_experiment.sh configs/dev_2_8.yml
# ./scripts/run_full_experiment.sh configs/dev.yml
# ./scripts/run_full_experiment.sh configs/main_results.yml

./scripts/run_full_experiment.sh configs/indicator_literal.yml > outputs/indicator_literal/system_output.txt
./scripts/run_full_experiment.sh configs/indicator_pragmatic.yml > outputs/indicator_pragmatic/system_output.txt
./scripts/run_full_experiment.sh configs/half_credit_literal.yml > outputs/half_credit_literal/system_output.txt
./scripts/run_full_experiment.sh configs/half_credit_pragmatic.yml > outputs/half_credit_pragmatic/system_output.txt

conda deactivate
