#!/bin/sh

python src/generate_expressions.py

python src/sample_languages.py

python src/add_natural_languages.py

python src/extract_prior.py

python src/estimate_pareto_frontier.py

python src/measure_tradeoff.py

python3 src/analyze.py