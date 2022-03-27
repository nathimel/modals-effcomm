"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off."""

import sys
from misc.file_util import load_configs, load_expressions, save_languages
from modals.modal_meaning import Modal_Meaning_Space
from modals.modal_language_of_thought import Modal_Language_of_Thought
from modals.modal_measures import Modal_Complexity_Measure, Modal_Informativity_Measure
from modals.modal_optimizer import Modal_Evolutionary_Optimizer
from sample_languages import generate_languages
from modals.modal_language import Modal_Expression
from modals.modal_meaning import Modal_Meaning
from modals.modal_language import Modal_Language
from modals.modal_language import is_iff
from misc.file_util import load_languages

def main():
    if len(sys.argv) != 4:
        print("Incorrect number of arguments.")
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file path_to_expressions_file path_to_artificial_languages")
        raise TypeError() #TODO: create an actual error class for the package

    print("Estimating pareto frontier ...", sep=' ')

    config_fn = sys.argv[1]
    expressions_fn = sys.argv[2]    
    save_all_langs_fn = sys.argv[3]

    # Load configs
    configs = load_configs(config_fn)

    evolutionary_alg_configs = configs['evolutionary_alg']
    sample_size = evolutionary_alg_configs['seed_population_size']
    max_mutations = evolutionary_alg_configs['max_mutations']
    generations = evolutionary_alg_configs['num_generations']
    processes = evolutionary_alg_configs['num_processes']
    lang_size = evolutionary_alg_configs['maximum_lang_size']

    # Set parameters for evolutionary algorithm optimizer

    expressions = load_expressions(expressions_fn)
    seed_population = generate_languages(expressions, lang_size, sample_size)

    space = expressions[0].get_meaning().get_meaning_space()
    complexity_measure = Modal_Complexity_Measure(
        Modal_Language_of_Thought(space, configs['language_of_thought']))
    informativity_measure = Modal_Informativity_Measure()

    optimizer = Modal_Evolutionary_Optimizer(
        comp_measure=complexity_measure,
        inf_measure=informativity_measure,
        expressions=expressions,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
        processes=processes
    )

    # Run the algorithm
    (_, explored_langs) = optimizer.fit(seed_population=seed_population)

    # Sanity check: create a perfectly informative language.
    vocab = []
    points = space.get_objects()
    for expression in expressions:
        points_ = expression.get_meaning().get_points()
        if len(points_) == 1:
            point, = points_
            vocab.append(expression)
    assert len(vocab) == len(points)
    lang = Modal_Language(vocab)
    lang.set_name('Sanity_Check')
    explored_langs.append(lang)

    # Add explored langs to the pool of sampled langs
    pool = load_languages(save_all_langs_fn)
    pool.extend(explored_langs)
    pool = list(set(pool))

    save_languages(save_all_langs_fn, pool)

    print('done.')

if __name__ == "__main__":
    main()