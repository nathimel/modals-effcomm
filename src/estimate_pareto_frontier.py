"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off."""

import sys
from altk.effcomm.optimization import Evolutionary_Optimizer
from misc.file_util import *
from modals.modal_language_of_thought import ModalLOT
from modals.modal_measures import ModalComplexityMeasure
from sample_languages import generate_languages
from misc.file_util import load_languages, set_seed
from modals.modal_mutations import *
from altk.effcomm.informativity import *


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Estimating pareto frontier ...")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expressions_fn = configs["file_paths"]["expressions"]
    space_fn = configs["file_paths"]["meaning_space"]
    save_all_langs_fn = configs["file_paths"]["artificial_languages"]
    dom_langs_fn = configs["file_paths"]["dominant_languages"]

    # Load optimization params
    evolutionary_alg_configs = configs["evolutionary_alg"]
    agent_type = configs["agent_type"]
    sample_size = evolutionary_alg_configs["generation_size"]
    max_mutations = evolutionary_alg_configs["max_mutations"]
    generations = evolutionary_alg_configs["num_generations"]
    processes = evolutionary_alg_configs["num_processes"]
    lang_size = evolutionary_alg_configs["maximum_lang_size"]

    set_seed(configs["random_seed"])

    # Create the first generation of languages
    print("Sampling seed generation...")
    expressions = load_expressions(expressions_fn)
    seed_population = generate_languages(
        ModalLanguage,
        expressions,
        lang_size,
        sample_size,
        # verbose=True,
    )

    # construct measures of complexity and informativity as optimization objectives
    space = load_space(space_fn)
    complexity_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    informativity_measure = SST_Informativity_Measure(
        prior=uniform_prior(space),
        utility=build_utility_matrix(space, load_utility(configs["utility"])),
        agent_type=agent_type,
    )
    objectives = {
        "comm_cost": lambda lang: 1
        - informativity_measure.language_informativity(lang),
        "complexity": complexity_measure.language_complexity,
    }

    # Load modals-specifc mutations
    mutations = [
        Add_Modal(),
        Remove_Modal(),
        Remove_Point(),
        Add_Point(),
        Interchange_Modal(),
    ]

    # Initialize optimizer and run algorithm
    optimizer = Evolutionary_Optimizer(
        objectives=objectives,
        expressions=expressions,
        mutations=mutations,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
        processes=processes,
    )
    result = optimizer.fit(seed_population=seed_population)
    dominant_langs = result["dominating_languages"]
    explored_langs = result["explored_languages"]

    # Explore additionally
    # result = optimizer.fit(explored_langs, explore=1.0)

    # Add explored langs to the pool of sampled langs
    pool = load_languages(save_all_langs_fn)
    pool.extend(explored_langs)
    pool = list(set(pool))
    dominant_langs = list(set(dominant_langs))


    # # sanity check: perfectly informative language
    # vocab = []
    # points = space.objects
    # # Sanity check: create a perfectly informative language.
    # for expression in expressions:
    #     points_ = expression.meaning.objects
    #     if len(points_) == 1:
    #         vocab.append(expression)
    # assert len(vocab) == len(points)
    # lang = ModalLanguage(vocab)
    # lang.name = 'Sanity_Check'
    # # explored_langs.append(lang)
    # dominant_langs.append(lang)

    # print([str(lang) for lang in dominant_langs])


    save_languages(save_all_langs_fn, pool, kind="sampled")
    save_languages(dom_langs_fn, dominant_langs, kind="dominant")

    print("done.")


if __name__ == "__main__":
    main()
