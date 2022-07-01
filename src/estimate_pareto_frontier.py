"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off."""

import sys
from altk.effcomm.optimization import EvolutionaryOptimizer
from misc.file_util import *
from modals.modal_language_of_thought import ModalLOT
from modals.modal_measures import language_complexity
from sample_languages import generate_languages
from misc.file_util import load_languages, set_seed
from modals.modal_mutations import (
    Add_Modal,
    Remove_Modal,
    Interchange_Modal,
    Add_Point,
)
from altk.effcomm.informativity import (
    informativity,
    uniform_prior,
    build_utility_matrix,
)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Estimating pareto frontier ...")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expressions_fn = configs["file_paths"]["expressions"]
    space_fn = configs["file_paths"]["meaning_space"]
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

    set_seed(configs["random_seed"])

    # Create the first generation of languages

    result = load_languages(artificial_langs_fn)
    sampled_languages = result["languages"]
    id_start = result["id_start"]

    print("Sampling seed generation...")
    expressions = load_expressions(expressions_fn)
    seed_result = generate_languages(
        ModalLanguage,
        expressions,
        lang_size,
        sample_size,
        id_start=id_start,
        # verbose=True,
    )
    seed_population = seed_result["languages"]
    id_start = seed_result["id_start"]

    # construct measures of complexity and informativity as optimization objectives
    space = load_space(space_fn)

    complexity_measure = lambda lang: language_complexity(
        language=lang,
        mlot=ModalLOT(space, configs["language_of_thought"]),
    )

    informativity_measure = lambda lang: informativity(
        language=lang,
        prior=uniform_prior(space),
        utility=build_utility_matrix(space, load_utility(configs["utility"])),
        agent_type=agent_type,
    )
    objectives = {
        "comm_cost": lambda lang: 1 - informativity_measure(lang),
        "informativity": informativity_measure,
        "complexity": complexity_measure,
    }

    # Load modals-specifc mutations
    mutations = [
        Add_Modal(),
        Remove_Modal(),
        # Remove_Point(),
        Add_Point(),
        Interchange_Modal(),
    ]

    # sanity check: perfectly informative language
    vocab = []
    points = space.objects
    # Sanity check: create a perfectly informative language.
    for expression in expressions:
        points_ = expression.meaning.objects
        if len(points_) == 1:
            vocab.append(expression)
    assert len(vocab) == len(points)
    lang = ModalLanguage(vocab, name='Sanity_Check')

    # perfect informativeness but synonymy
    vocab1 = vocab
    for expression in expressions:
        points_ = expression.meaning.objects
        if len(points_) == 1:
            vocab1.append(expression) # add each synonym
    lang1 = ModalLanguage(vocab1, name='Synonymy')
    
    seed_population.append(lang)
    seed_population.append(lang1)

    # Initialize optimizer and run algorithm
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
    result = optimizer.fit(seed_population, id_start, explore=explore)
    dominant_langs = result["dominating_languages"]
    explored_langs = result["explored_languages"]
    id_start = result["id_start"]

    # Explore additionally
    # result = optimizer.fit(explored_langs, explore=1.0)

    # Save all explored langs
    pool = explored_langs + sampled_languages
    pool = list(set(pool))
    dominant_langs = list(set(dominant_langs))

    save_languages(artificial_langs_fn, pool, id_start=id_start, kind="sampled")
    save_languages(dom_langs_fn, dominant_langs, id_start=id_start, kind="dominant")

    print("done.")


if __name__ == "__main__":
    main()
