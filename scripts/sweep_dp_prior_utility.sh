#!/bin/sh

python src/estimate_pareto_frontier.py "$@"

python src/measure_tradeoff.py "$@"

python src/analyze.py "$@"
