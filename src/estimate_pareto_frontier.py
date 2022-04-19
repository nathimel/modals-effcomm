"""Script for estimating the pareto frontier of languages optimizing the simplicity/informativeness trade-off."""

import sys
from misc.file_util import load_configs, load_expressions, save_languages
from modals.modal_language_of_thought import ModalLOT
from modals.modal_measures import ModalComplexityMeasure, ModalInformativityMeasure
from modals.modal_optimizer import Modal_Evolutionary_Optimizer
from sample_languages import generate_languages
from modals.modal_language import ModalLanguage
from misc.file_util import load_languages, set_seed


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

    # Construct a measure of informativity
    space = expressions[0].get_meaning().get_meaning_space()
    complexity_measure = ModalComplexityMeasure(
        ModalLOT(space, configs["language_of_thought"])
    )
    informativity_measure = ModalInformativityMeasure()

    # Initialize optimizer and run algorithm
    optimizer = Modal_Evolutionary_Optimizer(
        comp_measure=complexity_measure,
        inf_measure=informativity_measure,
        expressions=expressions,
        sample_size=sample_size,
        max_mutations=max_mutations,
        generations=generations,
        lang_size=lang_size,
        processes=processes,
    )
    (_, explored_langs) = optimizer.fit(seed_population=seed_population)

    # Sanity check for debugging: create a perfectly informative language.
    vocab = []
    points = space.get_objects()
    for expression in expressions:
        points_ = expression.get_meaning().get_points()
        if len(points_) == 1:
            vocab.append(expression)
    assert len(vocab) == len(points)  # 1:1 map from expressions to meanings
    lang = ModalLanguage(vocab)
    lang.set_name("Sanity_Check")
    explored_langs.append(lang)

    # Add explored langs to the pool of sampled langs
    pool = load_languages(save_all_langs_fn)
    pool.extend(explored_langs)
    pool = list(set(pool))

    save_languages(save_all_langs_fn, pool)

    print("done.")


if __name__ == "__main__":
    main()
