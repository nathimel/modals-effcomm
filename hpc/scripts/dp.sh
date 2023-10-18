#!/bin/sh

# load conda and activate environment
module load miniconda3/4.8.5
conda init bash
source /opt/apps/miniconda3/4.8.5/etc/profile.d/conda.sh
conda activate modals-effcomm

# run programs
echo
echo 'python src/setup.py "$@"'
python src/setup.py "$@"

echo
echo 'src/generate_expressions.py "$@"'
python src/generate_expressions.py "$@"

echo
echo 'python src/sample_languages.py "$@"'
python src/sample_languages.py "$@"

echo
echo 'src/estimate_pareto_frontier.py "$@"'
python src/estimate_pareto_frontier.py "$@"

echo
echo 'python src/measure_tradeoff.py "$@"'
python src/measure_tradeoff.py "$@"

echo
echo 'src/analyze.py "$@"'
python3 src/analyze.py "$@"