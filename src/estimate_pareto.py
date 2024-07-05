"""To debug explore."""

import hydra
import random
from ultk.effcomm.optimization import EvolutionaryOptimizer
from experiment import Experiment
from misc.file_util import set_seed
from modals.modal_language import ModalLanguage
from sample_languages import generate_languages
from modals.modal_mutations import (
    Add_Modal,
    Add_Point,
    Remove_Modal,
    Remove_Point,
    Interchange_Modal,
)
from omegaconf import DictConfig

from ultk.language.sampling import random_languages


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    print("Estimating pareto frontier ...")
    # Load optimization params
    evolutionary_alg_configs = config.experiment.sampling.evol
    sample_size = evolutionary_alg_configs.generation_size
    max_mutations = evolutionary_alg_configs.max_mutations
    generations = evolutionary_alg_configs.num_generations
    explore = evolutionary_alg_configs.explore
    lang_size = config.experiment.sampling.maximum_lang_size

    # Create the first generation of languages
    experiment = Experiment(
        config,
    )

    experiment.set_filepaths(["artificial_languages", "dominant_languages"])
    if not config.experiment.overwrites.languages.dominant and experiment.path_exists(
        "dominant_languages"
    ):
        print(
            " found and will not be overwritten; skipping evolutionary algorithm exploration of languages."
        )
        return

    experiment.load_files(["expressions", "artificial_languages", "natural_languages"])

    expressions = experiment.expressions

    # Load seed generation
    seed_population: list[ModalLanguage] = []
    seed_pool_configs = evolutionary_alg_configs.seed_generation_pool
    id_start = None

    if "existing" in seed_pool_configs:
        result = experiment.artificial_languages
        if result is not None:
            seed_population.extend(result["languages"])
            id_start = result["id_start"]

    if "natural" in seed_pool_configs:
        result = experiment.natural_languages
        if result is not None:
            seed_population.extend(result["languages"])

    if "random" in seed_pool_configs:
        print("Sampling seed generation...")

        langs = random_languages(
            expressions,
            sampling_strategy="stratified",
            sample_size=1000,
            max_size=10,
            language_class=ModalLanguage,
        )
        seed_population.extend(langs)

    comp = experiment.complexity_measure
    inf = experiment.informativity_measure
    comm_cost = lambda lang: 1 - inf(lang)
    objectives = [comp, comm_cost]

    # Load modals-specifc mutations
    mutations = [
        Add_Modal(),
        Remove_Modal(),
        Remove_Point(),
        Add_Point(),
        Interchange_Modal(),
    ]

    # Initialize optimizer
    optimizer = EvolutionaryOptimizer(
        objectives=objectives,
        expressions=expressions,
        # mutations=mutations,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
    )

    print(f"Minimizing for complexity, comm_cost ...")
    result = optimizer.fit(seed_population)

    dominant_langs = result["dominating_languages"]

    # assign dummy names
    for idx, lang in enumerate(dominant_langs):
        lang.data["name"] = f"sampled_lang_{idx}"

    dominant_langs = list(set(dominant_langs))

    print("Saving languages...")
    experiment.dominant_languages = {"languages": dominant_langs, "id_start": id_start}
    experiment.write_files(["dominant_languages"])
    print("done.")


if __name__ == "__main__":
    main()
