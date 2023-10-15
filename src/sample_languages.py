"""Script for sampling languages."""

import sys
from altk.language.sampling import generate_languages
from modals import modal_language
from modals.modal_language import ModalLanguage
from experiment import Experiment

import hydra
from misc.file_util import set_seed
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    experiment = Experiment(
        config, 
        load_files=["expressions", "artificial_languages"]
    )

    # Load parameters for languages
    lang_size = config.experiment.sampling.maximum_lang_size
    sample_size = config.experiment.sampling.unbiased.sample_size

    # Turn the knob on universal property
    expressions = experiment.expressions
    universal_property = getattr(modal_language, config.experiment.universal_property)

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
    experiment.artificial_languages = {"languages": languages, "id_start": id_start}
    experiment.write_files(["artificial_languages"], kinds=["sampled"])
    print("done.")


if __name__ == "__main__":
    main()
