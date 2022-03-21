#!/bin/sh

# Usage: ./scripts/main_results/run.sh path-to-config  
# Example: ./scripts/main_results/run.sh configs/main_results/config.yml 

if test $# -lt 1
then
    echo "Usage: ./scripts/main_results/run.sh path-to-config"
    exit 1
fi


CONFIG=$1

python3 src/build_meaning_space.py $CONFIG #not obvious this is necessary

python3 src/generate_expressions.py $CONFIG

python3 src/sample_languages.py $CONFIG

python3 src/add_natural_languages.py $CONFIG

python3 src/estimate_pareto_frontier.py $CONFIG

python3 src/measure_languages.py $CONFIG

python3 src/analysis.py $CONFIG
