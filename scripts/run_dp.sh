#!/bin/sh

python src/setup.py "$@"

python src/generate_expressions.py "$@"

python src/sample_languages.py "$@"

python src/estimate_pareto_frontier.py "$@"

python src/measure_tradeoff.py "$@"

python3 src/analyze.py "$@"