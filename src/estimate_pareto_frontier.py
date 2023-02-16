"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off, and robust exploration of the 2D space of possible modal languages."""

import sys
from altk.effcomm.optimization import EvolutionaryOptimizer
from misc import file_util
from modals.modal_language_of_thought import ModalLOT
from modals.modal_language import ModalLanguage
from modals.modal_measures import language_complexity
from sample_languages import generate_languages
from modals.modal_mutations import (
    Add_Modal,
    Add_Point,
    Remove_Modal,
    Remove_Point,
    Interchange_Modal,
)
from altk.effcomm.informativity import informativity


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Estimating pareto frontier ...")

    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)
    expressions_fn = configs["file_paths"]["expressions"]
    space_fn = configs["file_paths"]["meaning_space"]
    prior_fn = configs["file_paths"]["prior"]
    artificial_langs_fn = configs["file_paths"]["artificial_languages"]
    dom_langs_fn = configs["file_paths"]["dominant_languages"]

    # Load optimization params
    evolutionary_alg_configs = configs["evolutionary_alg"]
    agent_type = configs["agent_type"]
    sample_size = evolutionary_alg_configs["generation_size"]
    max_mutations = evolutionary_alg_configs["max_mutations"]
    generations = evolutionary_alg_configs["num_generations"]
    processes = evolutionary_alg_configs["num_processes"]
    lang_size = evolutionary_alg_configs["maximum_lang_size"]
    explore = evolutionary_alg_configs["explore"]

    file_util.set_seed(configs["random_seed"])

    # Create the first generation of languages

    result = file_util.load_languages(artificial_langs_fn)
    sampled_languages = result["languages"]
    id_start = result["id_start"]

    print("Sampling seed generation...")
    expressions = file_util.load_expressions(expressions_fn)
    result = generate_languages(
        language_class=ModalLanguage,
        expressions=expressions,
        lang_size=lang_size,
        sample_size=sample_size,
        id_start=id_start,
    )
    seed_population = result["languages"]
    id_start = result["id_start"]

    # construct measures of complexity and informativity as optimization objectives
    space = file_util.load_space(space_fn)
    prior = space.prior_to_array(file_util.load_prior(prior_fn))

    complexity_measure = lambda lang: language_complexity(
        language=lang,
        mlot=ModalLOT(space, configs["language_of_thought"]),
    )

    informativity_measure = lambda lang: informativity(
        language=lang,
        prior=prior,
        utility=file_util.load_utility(configs["utility"]),
        agent_type=agent_type,
    )

    # Use optimizer as an exploration / sampling method as follows:
    # estimate FOUR pareto frontiers using the evolutionary algorithm; one for each corner of the 2D space of possible langs
    directions = {
        "lower_left": ("comm_cost", "complexity"),
        "lower_right": ("informativity", "complexity"),
        "upper_left": ("comm_cost", "simplicity"),
        "upper_right": ("informativity", "simplicity"),
    }
    objectives = {
        "comm_cost": lambda lang: 1 - informativity_measure(lang),
        "informativity": informativity_measure,
        "complexity": complexity_measure,
        "simplicity": lambda lang: 1
        / complexity_measure(
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
        processes=processes,
    )

    # Explore all four corners of the possible language space
    results = {k: None for k in directions}
    pool = []
    for direction in directions:
        # set directions of optimization
        x, y = directions[direction]
        optimizer.x = x
        optimizer.y = y
        print(f"Minimizing for {x}, {y} ...")

        # run algorithm
        result = optimizer.fit(
            seed_population=seed_population,
            id_start=id_start,
            explore=explore,
        )

        # collect results
        results[direction] = result
        id_start = result["id_start"]
        pool.extend(results[direction]["explored_languages"])

    # the Pareto langs for the complexity/comm_cost trade-off.
    dominant_langs = results["lower_left"]["dominating_languages"]

    print(f"Discovered {len(pool)} languages.")
    pool.extend(sampled_languages)
    pool = list(set(pool))
    dominant_langs = list(set(dominant_langs))

    file_util.save_languages(
        artificial_langs_fn, pool, id_start=id_start, kind="explored"
    )
    file_util.save_languages(
        dom_langs_fn, dominant_langs, id_start=id_start, kind="dominant"
    )

    print("done.")


if __name__ == "__main__":
    main()
