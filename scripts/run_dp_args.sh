#!/bin/sh

# ./scripts/run_dp.sh experiment=dp experiment.overwrite_expressions=True experiment.overwrite_languages=True

python src/setup.py experiment=dp 

python src/generate_expressions.py experiment=dp experiment.overwrites.expressions=True

python src/add_dp_natural_languages.py experiment=dp experiment.overwrites.languages.natural=True

# DO want to save these artificial langs
python src/perturb_languages.py experiment=dp experiment.overwrites.languages.artificial=True

# Do not overwrite the artificial langs from above, only the dominant
# python src/explore_languages.py  experiment=dp experiment.overwrites.languages.dominant=True
python src/estimate_pareto.py  experiment=dp experiment.overwrites.languages.dominant=True

# Overwrite all languages with the new data
python src/measure_tradeoff.py  experiment=dp "experiment.overwrites.languages={"natural":True, "artificial":True, "dominant":True}"

python src/analyze.py experiment=dp
