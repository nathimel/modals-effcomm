#!/bin/sh

source ~/miniforge3/etc/profile.d/conda.sh
conda activate modals-effcomm

# todo: move these to a setup config file
./scripts/main_results.sh configs/main_results/config.yml outputs/main_results/meaning_space.yml outputs/main_results/expressions.yml outputs/main_results/languages/artificial_languages.yml data/natural_languages outputs/main_results/languages/dominant_languages.yml outputs/main_results/dataframe.csv outputs/main_results/plot.png

conda deactivate
