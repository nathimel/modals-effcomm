"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off."""

import sys
from altk.effcomm.optimization import Evolutionary_Optimizer
from misc.file_util import load_configs, load_expressions, save_languages
from modals.modal_language_of_thought import ModalLOT
from modals.modal_measures import ModalComplexityMeasure
from sample_languages import generate_languages
from misc.file_util import load_languages, set_seed
from modals.modal_mutations import *
from altk.effcomm.informativity import *
from modals.modal_language import ModalLanguage


def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError()  # TODO: create an actual error class for the package

    print("Estimating pareto frontier ...", sep=" ")

    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expressions_fn = configs["file_paths"]["expressions"]
    save_all_langs_fn = configs["file_paths"]["artificial_languages"]

    # Load optimization params
    evolutionary_alg_configs = configs["evolutionary_alg"]
    sample_size = evolutionary_alg_configs["generation_size"]
    max_mutations = evolutionary_alg_configs["max_mutations"]
    generations = evolutionary_alg_configs["num_generations"]
    processes = evolutionary_alg_configs["num_processes"]
    lang_size = evolutionary_alg_configs["maximum_lang_size"]

    set_seed(configs["random_seed"])

    # Create the first generation of languages
    expressions = load_expressions(expressions_fn)
    seed_population = generate_languages(expressions, lang_size, sample_size)

    # construct measures of complexity and informativity
    space = expressions[0].get_meaning().get_universe()
    complexity_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    informativity_measure = SST_Informativity_Measure(
        prior=uniform_prior(space),
        utility=build_utility_matrix(space, indicator),
    )

    # Load modals-specifc mutations
    mutations = [
        Add_Modal(),
        Remove_Modal(),
        # Remove_Point(),
        # Add_Point(),
        # Interchange_Modal(),
    ]

    # Initialize optimizer and run algorithm
    optimizer = Evolutionary_Optimizer(
        comp_measure=complexity_measure,
        inf_measure=informativity_measure,
        expressions=expressions,
        mutations=mutations,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
        processes=processes,
    )
    _, explored_langs = optimizer.fit(seed_population=seed_population)

    # Sanity checks
    vocab = []
    points = space.get_objects()

    # create a perfectly informative language.
    for expression in expressions:
        points_ = expression.get_meaning().get_objects()
        if len(points_) == 1:
            vocab.append(expression)
    assert len(vocab) == len(points)
    lang = ModalLanguage(vocab, "Sanity_Check_1_inf")
    explored_langs.append(lang)

    # create a minimally informative language, e.g. inf=prior
    vocab = []
    for expression in expressions:
        points_ = expression.get_meaning().get_objects()
        if len(points_) == 1:
            vocab.append(expression)
            break
    assert len(vocab) == 1
    lang = ModalLanguage(vocab, "Sanity_Check_min_inf")
    explored_langs.append(lang)

    # Add explored langs to the pool of sampled langs
    pool = load_languages(save_all_langs_fn)
    pool.extend(explored_langs)
    pool = list(set(pool))

    save_languages(save_all_langs_fn, pool)

    print("done.")


if __name__ == "__main__":
    main()
