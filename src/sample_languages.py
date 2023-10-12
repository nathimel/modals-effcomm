"""Script for sampling languages."""

import sys
from altk.language.sampling import generate_languages
from modals import modal_language
from modals.modal_language import ModalLanguage

import hydra
from misc.file_util import set_seed, save_languages, load_expressions, get_subdir_fn
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    expressions_fn = get_subdir_fn(config, config.filepaths.expressions_subdir, config.filepaths.expressions)
    lang_save_fn = get_subdir_fn(config, config.filepaths.language_subdir, config.filepaths.artificial_languages)

    # Load parameters for languages
    lang_size = config.experiment.sampling.maximum_lang_size
    sample_size = config.experiment.sampling.unbiased.sample_size

    # Turn the knob on universal property
    expressions = load_expressions(expressions_fn)
    universal_property = getattr(modal_language, config.experiment.sampling.unbiased.universal_property)

    print("Sampling random languages ...")
    result = generate_languages(
        language_class=ModalLanguage,
        expressions=expressions,
        lang_size=lang_size,
        sample_size=sample_size,
        criterion=universal_property,
    )
    languages = result["languages"]
    id_start = result["id_start"]

    languages = list(set(languages))
    save_languages(lang_save_fn, languages, id_start, kind="sampled")
    print("done.")


if __name__ == "__main__":
    main()
