#!/bin/sh

python src/setup.py "$@"

python src/generate_expressions.py "$@"

# python src/sample_languages.py "$@"

python src/add_dp_natural_languages.py "$@"

python src/explore_languages.py "$@"

# crucially this comes after explore, since we hackily overwrite
# the results of artificial.yml but not dominant.yml
python src/perturb_languages.py "$@"

python src/measure_tradeoff.py "$@"

python3 src/analyze.py "$@"