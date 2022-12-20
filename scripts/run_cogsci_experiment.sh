#!/bin/sh

CONFIG=$1

python3 src/create_folders.py $CONFIG

python3 src/build_meaning_space.py $CONFIG

python3 src/generate_expressions.py $CONFIG

python3 src/sample_languages.py $CONFIG

# eventually add nat langs

python3 src/set_prior.py $CONFIG # overwrites prior

python3 src/estimate_pareto_frontier.py $CONFIG

python3 src/measure_tradeoff.py $CONFIG

# notebook for analysis
