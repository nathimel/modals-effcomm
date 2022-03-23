#!/bin/sh

# Example: ./scripts/main_results.sh configs/main_results/config.yml outputs/main_results/meaning_space.yml outputs/main_results/expressions.yml outputs/main_results/artificial_languages.yml

if test $# -lt 2
then
    echo "Usage: ./scripts/main_results/run.sh path_to_config path_to_save_meaning_space path_to_save_expressions path_to_save_artificial_languages"
    exit 1
fi


CONFIG=$1
MEANING_SPACE_SAVE_FILE=$2
EXPRESSIONS_SAVE_FILE=$3
ARTIFICIAL_LANGUAGES_SAVE_FILE=$4

python3 src/build_meaning_space.py $CONFIG $MEANING_SPACE_SAVE_FILE

python3 src/generate_expressions.py $CONFIG $MEANING_SPACE_SAVE_FILE $EXPRESSIONS_SAVE_FILE

python3 src/sample_languages.py $CONFIG $EXPRESSIONS_SAVE_FILE $ARTIFICIAL_LANGUAGES_SAVE_FILE

# python3 src/add_natural_languages.py $CONFIG

# python3 src/estimate_pareto_frontier.py $CONFIG

# python3 src/measure_languages.py $CONFIG

# python3 src/analysis.py $CONFIG
