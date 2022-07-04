"""Script for sampling languages."""

import sys
from altk.effcomm.sampling import generate_languages
from modals import modal_language
from modals.modal_language import ModalLanguage
from misc.file_util import *


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/sample_languages.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")


    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs["file_paths"]["expressions"]
    lang_save_fn = configs["file_paths"]["artificial_languages"]

    # Load parameters for languages
    lang_size = configs["lang_size"]
    sample_size = configs["sample_size"]
    set_seed(configs["random_seed"])

    # Turn the knob on universal property
    expressions = load_expressions(expression_save_fn)
    universal_property = getattr(modal_language, configs["universal_property"])

    print("Sampling random languages ...")
    result = generate_languages(
        language_class=ModalLanguage,
        expressions=expressions,
        lang_size=lang_size,
        sample_size=sample_size,
        criterion=universal_property,
    )
    any_languages = result["languages"]
    id_start = result["id_start"]

    # WARNING: this seems to be doubling the sample size, before you unique the pool afterwards.
    # sample only 100% universal property languages
    print("Sampling degree 1.0 universal languages ...")
    natural_expressions = [e for e in expressions if universal_property(e)]
    result = generate_languages(
        language_class=ModalLanguage,
        expressions=natural_expressions,
        lang_size=lang_size,
        sample_size=sample_size,
        criterion=universal_property,
        id_start=id_start,
    )
    universal_languages = result["languages"]

    # unique and save langs
    languages = list(set(any_languages + universal_languages))
    save_languages(lang_save_fn, languages, id_start, kind="sampled")
    print("done.")


if __name__ == "__main__":
    main()
