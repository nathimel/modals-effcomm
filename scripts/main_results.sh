#!/bin/sh

# Example: ./scripts/main_results.sh configs/main_results/config.yml

if test $# -lt 1
then
    echo "Usage: ./scripts/main_results/run.sh path_to_config"
    exit 1
fi


CONFIG=$1

python3 src/build_meaning_space.py $CONFIG

python3 src/generate_expressions.py $CONFIG

python3 src/sample_languages.py $CONFIG

python3 src/add_natural_languages.py $CONFIG

python3 src/estimate_pareto_frontier.py $CONFIG

python3 src/analyze.py $CONFIG
