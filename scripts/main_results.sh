#!/bin/sh

# Example: ./scripts/main_results.sh configs/main_results/config.yml outputs/main_results/meaning_space.yml outputs/main_results/expressions.yml outputs/main_results/languages/artificial_languages.yml data/natural_languages outputs/main_results/languages/dominant_languages.yml outputs/main_results/dataframe.csv outputs/main_results/plot.png

if test $# -lt 8
then
    echo "Usage: ./scripts/main_results/run.sh path_to_config path_to_meaning_space path_to_expressions path_to_artificial_languages path_to_natural_languages path_to_save_dataframe path_to_save_plot"
    exit 1
fi


CONFIG=$1
MEANING_SPACE_SAVE_FILE=$2
EXPRESSIONS_SAVE_FILE=$3
ARTIFICIAL_LANGUAGES_SAVE_FILE=$4
NATURAL_LANGUAGES_SAVE_FILE=$5
DOMINANT_LANGUAGES_SAVE_FILE=$6
DATAFRAME_SAVE_FILE=$7
PLOT_SAVE_FILE=$8

python3 src/build_meaning_space.py $CONFIG $MEANING_SPACE_SAVE_FILE

python3 src/generate_expressions.py $CONFIG $MEANING_SPACE_SAVE_FILE $EXPRESSIONS_SAVE_FILE

python3 src/sample_languages.py $CONFIG $EXPRESSIONS_SAVE_FILE $ARTIFICIAL_LANGUAGES_SAVE_FILE

# python3 src/add_natural_languages.py $CONFIG

python3 src/estimate_pareto_frontier.py $CONFIG $EXPRESSIONS_SAVE_FILE $ARTIFICIAL_LANGUAGES_SAVE_FILE

python3 src/analyze.py $CONFIG $MEANING_SPACE_SAVE_FILE  $ARTIFICIAL_LANGUAGES_SAVE_FILE $NATURAL_LANGUAGES_SAVE_FILE $DOMINANT_LANGUAGES_SAVE_FILE $DATAFRAME_SAVE_FILE $PLOT_SAVE_FILE
