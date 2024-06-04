#!/bin/sh

python src/setup.py "$@"

python src/generate_expressions.py "$@"

python src/add_natural_languages.py "$@"

# python src/estimate_pareto.py "experiment.overwrites.languages={"natural":False, "artificial":True, "dominant":True}" "$@"

python src/new_explore_languages.py "experiment.overwrites.languages={"natural":False, "artificial":True, "dominant":True}" "$@"

# python src/measure_tradeoff.py "experiment.overwrites.languages={"natural":True, "artificial":True, "dominant":True}" "$@"

# python3 src/analyze.py "$@"