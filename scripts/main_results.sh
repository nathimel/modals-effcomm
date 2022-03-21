#!/bin/sh

# Usage: ./scripts/main_results/run.sh path-to-config  path-to-save-meaning_space path-to-save-expressions path-to-save-artificial-languages path-to-save-natural-languages path-to-save-frontier dir-path-to-save-analysis

# Example: ./scripts/main_results/run.sh configs/main_results/config.yml output/main_results/meaning_space.yml output/main_results/expressions.hml output/main_results/languages/artificial.json output/main_results/languages/natural.json output/main_results/languages/frontier.json output/main_results/analysis

$CONFIG = $1
$MEANING_SPACE_SAVE_FILE = $2
$EXPRESSIONS_SAVE_FILE = $3

python3 build_meaning_space.py 

python3 generate_expressions.py

python3 sample_languages.py

python3 add_natural_languages.py

python3 estimate_pareto_frontier.py

python3 measure_languages.py

python3 analysis.py
