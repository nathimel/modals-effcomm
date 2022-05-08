"""Script for sampling languages."""

import sys
from altk.effcomm.sampling import generate_languages
from modals.modal_language import ModalExpression, ModalLanguage, is_iff
from misc.file_util import *
from modals.modal_meaning import ModalMeaning


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/sample_languages.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Sampling languages ...")

    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs["file_paths"]["expressions"]
    lang_save_fn = configs["file_paths"]["artificial_languages"]

    # Load parameters for languages
    lang_size = configs["lang_size"]
    sample_size = configs["sample_size"]
    set_seed(configs["random_seed"])

    # Turn the knob on iff
    expressions = load_expressions(expression_save_fn)
    languages = generate_languages(
        ModalLanguage,        
        expressions,
        lang_size,
        sample_size,
        is_iff,
        # verbose=True,
    )

    # unique and save langs
    languages = list(set(languages))
    save_languages(lang_save_fn, languages, kind="sampled")
    print("done.")


if __name__ == "__main__":
    main()
