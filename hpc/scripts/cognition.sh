#!/bin/sh


# load conda and activate environment
module load miniconda3/4.8.5
conda init bash
source /opt/apps/miniconda3/4.8.5/etc/profile.d/conda.sh
conda activate modals-effcomm


echo 'python src/setup.py "$@"'
python src/setup.py "$@"

echo 'python src/add_natural_languages.py "$@"'
python src/generate_expressions.py "$@"

echo 'python src/add_natural_languages.py "$@"'
python src/add_natural_languages.py "$@"

# python src/estimate_pareto.py "experiment.overwrites.languages={"natural":False, "artificial":True, "dominant":True}" "$@"

echo 'python src/new_explore_languages.py "experiment.overwrites.languages={"natural":False, "artificial":True, "dominant":True}" "$@"'
python src/new_explore_languages.py "experiment.overwrites.languages={"natural":False, "artificial":True, "dominant":True}" "$@"

echo 'python src/measure_tradeoff.py "experiment.overwrites.languages={"natural":True, "artificial":True, "dominant":True}" "$@"'
python src/measure_tradeoff.py "experiment.overwrites.languages={"natural":True, "artificial":True, "dominant":True}" "$@"

echo 'python3 src/analyze.py "$@"'
python3 src/analyze.py "$@"
