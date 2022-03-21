#!/bin/sh

# Usage: ./scripts/main_results/run.sh path-to-config  
# Example: ./scripts/main_results/run.sh configs/main_results/config.yml 

$CONFIG = $1

python3 build_meaning_space.py $CONFIG

python3 generate_expressions.py $CONFIG

python3 sample_languages.py $CONFIG

python3 add_natural_languages.py $CONFIG

python3 estimate_pareto_frontier.py $CONFIG

python3 measure_languages.py $CONFIG

python3 analysis.py $CONFIG
