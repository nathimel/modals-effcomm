"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off, and robust exploration of the 2D space of possible modal languages."""

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
    if not config.experiment.overwrites.languages.dominant and experiment.path_exists("dominant_languages"):
        print(" found and will not be overwritten; skipping evolutionary algorithm exploration of languages.")
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
        result = generate_languages(
            language_class=ModalLanguage,
            expressions=expressions,
            lang_size=lang_size,
            sample_size=sample_size,
            id_start=id_start if id_start is not None else 0,
        )
        seed_population.extend(result["languages"])
        id_start = result["id_start"]

    comp = experiment.complexity_measure
    inf = experiment.informativity_measure

    # Use optimizer as an exploration / sampling method as follows:
    # estimate FOUR pareto frontiers using the evolutionary algorithm; one for each corner of the 2D space of possible langs
    directions = {
        "lower_left": ("comm_cost", "complexity"),
        "lower_right": ("informativity", "complexity"),
        "upper_left": ("comm_cost", "simplicity"),
        "upper_right": ("informativity", "simplicity"),
    }
    objectives = {
        "comm_cost": lambda lang: 1 - inf(lang),
        "informativity": inf,
        "complexity": comp,
        "simplicity": lambda lang: 1
        / comp(
            lang
        ),  # this is different from the simplicity value computed during analysis. The data['simplicity'] field will be reset to None before then, in measure_tradeoff.
    }

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
        mutations=mutations,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
    )


    # TODO: To debug why evol alg is not finding more than 1 dominant, 
    # copypaste the indefinites example evol alg.

    # Explore all four corners of the possible language space
    results = {k: None for k in directions}
    pool = []
    for direction in evolutionary_alg_configs.directions:
        # set directions of optimization
        x, y = directions[direction]
        optimizer.objectives = [objectives[x], objectives[y]]
        print(f"Minimizing for {x}, {y} ...")


        # run algorithm
        result = optimizer.fit(
            seed_population=seed_population,
            # id_start=id_start,
            explore=explore,
        )

        # collect results
        results[direction] = result
        id_start += len(result["explored_languages"])
        pool.extend(results[direction]["explored_languages"])

    # the Pareto langs for the complexity/comm_cost trade-off.
    dominant_langs = results["lower_left"]["dominating_languages"]

    print(f"Discovered {len(pool)} languages.")
    print(f"Filtering languages...")

    pool = list(set(pool))
    dominant_langs = list(set(dominant_langs))

    # remove some non-dominant to limit final pool to a standard size
    # TODO: remove this hack
    num_natural_langs = len(experiment.natural_languages["languages"]) if experiment.natural_languages is not None else 0
    cap = config.experiment.sampling.total_pool_cap - len(dominant_langs) - num_natural_langs
    candidate_langs = [lang for lang in pool if lang not in dominant_langs]
    if len(pool) > cap:
        reduced_pool = random.sample(candidate_langs, cap)
        pool = reduced_pool + dominant_langs
    
    print("Saving languages...")
    experiment.artificial_languages = {"languages": pool, "id_start": id_start}
    experiment.dominant_languages = {"languages": dominant_langs, "id_start": id_start}
    experiment.write_files(["artificial_languages", "dominant_languages"])
    print("done.")


if __name__ == "__main__":
    main()
