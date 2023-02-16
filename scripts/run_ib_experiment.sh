#!/bin/sh

if test $# -lt 1
then
    echo "Usage: ./scripts/run_ib_experiment.sh path_to_config"
    exit 1
fi


CONFIG=$1

python3 src/create_folders.py $CONFIG

python3 src/build_meaning_space.py $CONFIG

python3 src/generate_expressions.py $CONFIG

python3 src/sample_languages.py $CONFIG

python3 src/add_natural_languages.py $CONFIG

python3 src/extract_prior.py $CONFIG

python3 src/estimate_pareto_frontier.py $CONFIG # this just samples

python3 src/compute_ib_curve.py $CONFIG # the actual pareto

python3 src/measure_ib_tradeoff.py $CONFIG

python3 src/analyze_ib.py $CONFIG
