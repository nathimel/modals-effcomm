import os
import yaml
from modal_meaning import Modal_Meaning_Space

# save paths
# I have a design decision to make. Either I fully specify the fullpath every time, or assume the existence of certain directory structure for the project.
# If the former, src code simplifies but experiment replication code complicates.
# If the latter, the structure of one experiment takes on a kind of (predictable) independence.

# path_to_save_meaning_space: 'output/main_results/meaning_space.yml'
# path_to_save_expressions: 'expresions.yml'
# path_to_save_artificial_languages: 'output/main_results/languages/artificial.yml'
# path_to_save_natural_languages: 'output/main_results/languages/natural.yml'
# path_to_save_frontier: 'output/main_results/languages/frontier.yml'
# dir_path_to_save_analysis: 'output/main_results/languages/analysis'

def load_modal_meaning_space(fn: str)->Modal_Meaning_Space:
    """Read and the Modal_Meaning_Space object for the experiment saved in a .yml file."""
    with open(fn, "r") as stream:
        mms = yaml.safe_load(stream)
    return mms