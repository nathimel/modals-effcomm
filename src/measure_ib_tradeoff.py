"""Script for measuring the Deterministic Information Bottleneck trade-off."""

import sys
from misc import file_util
from modals.modal_language import iff, sav, dlsav
from modals.modal_meaning import generate_meaning_distributions
from altk.effcomm.tradeoff import tradeoff
from altk.effcomm.analysis import get_dataframe
from altk.effcomm.information import ib_comm_cost, ib_complexity, ib_informativity


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/measure_IB_tradeoff.py path_to_config")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Measuring IB tradeoff ...")

    # Load the experimental data and paths to save results
    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)

    paths = configs["file_paths"]
    space_fn = paths["meaning_space"]
    prior_fn = paths["prior"]
    sampled_languages_fn = paths["artificial_languages"]
    natural_languages_fn = paths["natural_languages"]
    dominant_languages_fn = paths["dominant_languages"]

    df_fn = paths["analysis"]["data"]

    ib_curve_fn = paths["ib_curve"]

    file_util.set_seed(configs["random_seed"])

    # load languages
    print("Loading all languages ...")
    print("sampled...")
    sampled_result = file_util.load_languages(sampled_languages_fn)
    print("dominant...")
    dominant_result = file_util.load_languages(dominant_languages_fn)
    print("natural...")
    natural_result = file_util.load_languages(natural_languages_fn)

    id_start = sampled_result["id_start"]
    sampled_languages = sampled_result["languages"]
    dominant_languages = dominant_result["languages"]
    natural_languages = natural_result["languages"]

    langs = list(set(sampled_languages + dominant_languages + natural_languages))
    print(f"{len(langs)} total langs.")

    # Load semantic space, prior, and IB bound
    space = file_util.load_space(space_fn)
    prior = space.prior_to_array(file_util.load_prior(prior_fn))
    ib_curve = file_util.load_ib_curve(ib_curve_fn)
    meaning_dists = generate_meaning_distributions(space)

    comp_measure = lambda lang: ib_complexity(
        language=lang,
        prior=prior,
    )

    comm_cost_measure = lambda lang: ib_comm_cost(
        language=lang,
        prior=prior,
        meaning_dists=meaning_dists,
    )

    inf_measure = lambda lang: ib_informativity(
        language=lang,
        prior=prior,
        meaning_dists=meaning_dists,
    )

    # Get trade-off results
    properties_to_measure = {
        "complexity": comp_measure,
        "simplicity": lambda lang: None,  # reset simplicity from evol alg exploration
        "informativity": inf_measure,
        "comm_cost": comm_cost_measure,
        "iff": lambda lang: lang.degree_property(iff),
        "sav": lambda lang: lang.degree_property(sav),
        "dlsav": dlsav,
    }

    result = tradeoff(
        languages=langs,
        properties=properties_to_measure,
        x="comm_cost",
        y="complexity",
        frontier=ib_curve,
    )
    # dom_langs = result["dominating_languages"]
    langs = result["languages"]

    nat_langs = [lang for lang in langs if lang.natural]

    file_util.save_languages(sampled_languages_fn, langs, id_start, kind="sampled")

    file_util.save_languages(
        natural_languages_fn, nat_langs, id_start=None, kind="natural"
    )
    print("saved languages.")

    # TODO: store the language.data fields in a common spot for repeat access in a uniform way
    all_data = get_dataframe(
        langs, columns=list(properties_to_measure.keys()) + ["optimality"]
    )
    all_data["natural"] = [lang.natural for lang in langs]
    # all_data["dominant"] = [lang in dom_langs for lang in langs]
    all_data["name"] = [lang.data["name"] for lang in langs]
    all_data.to_csv(df_fn, index=False)
    print("saved df.")


if __name__ == "__main__":
    main()
