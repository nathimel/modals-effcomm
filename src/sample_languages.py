"""Script for sampling languages."""

import os
import hydra

from altk.language.sampling import generate_languages
from modals import modal_language
from modals.modal_language import ModalLanguage
from experiment import Experiment

from misc.file_util import set_seed
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    experiment = Experiment(
        config, 
    )
    lang_fn = "artificial_languages"
    experiment.set_filepaths([lang_fn])
    if not config.experiment.overwrite_languages and experiment.path_exists(lang_fn):
        print("Language file found and will not be overwritten; skipping sampling of languages.")
        return

    experiment.load_files(["expressions", lang_fn])

    # Load parameters for languages
    lang_size = config.experiment.sampling.maximum_lang_size
    sample_size = config.experiment.sampling.unbiased.sample_size

    # Turn the knob on lexeme-level property
    expressions = experiment.expressions
    lexeme_property = getattr(modal_language, config.experiment.sampling.unbiased.lexeme_property)

    print("Sampling random languages ...")
    result = generate_languages(
        language_class=ModalLanguage,
        expressions=expressions,
        lang_size=lang_size,
        sample_size=sample_size,
        criterion=lexeme_property,
    )
    languages = result["languages"]
    id_start = result["id_start"]

    languages = list(set(languages))
    experiment.artificial_languages = {"languages": languages, "id_start": id_start}
    experiment.write_files([lang_fn], kinds=["sampled"])
    print("done.")


if __name__ == "__main__":
    main()
