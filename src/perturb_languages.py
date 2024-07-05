"""Script to shuffle natural languages' vocabularies."""

import copy
import os
import hydra
import random

from experiment import Experiment
from modals.modal_language import ModalLanguage, ModalExpression
from modals.modal_meaning import ModalMeaningPoint, ModalMeaning, ModalMeaningSpace

from typing import Any

from misc.file_util import set_seed
from omegaconf import DictConfig

from itertools import permutations


def shuffle_point(
    referent: ModalMeaningPoint, universe: ModalMeaningSpace
) -> ModalMeaningPoint:
    new_referent = referent
    while new_referent == referent:
        force, flavor = referent.data

        if random.choice([0, 1]):
            # sample a force
            force = random.choice(universe.forces)
        else:
            # sample a flavor
            flavor = random.choice(universe.flavors)

        new_referent = ModalMeaningPoint(force, flavor)

    return new_referent


def shuffle_languages_by_expression(
    languages: list[ModalLanguage],
    expressions: list[ModalExpression],
    num_variants_per_language: int = 100,
) -> dict[str, Any]:
    """For each language, obtain a hypothetical variant, by for each expression, randomly changing the meanings it can express by swapping either the force or flavor of each meaning points."""
    variants = []
    for language in languages:
        for i in range(num_variants_per_language):
            new_vocab = []

            # Obtain a hypothetical variant of a language
            for expression in language.expressions:
                new_referents = []
                for referent in expression.meaning.referents:
                    # perturb a feature of the referent
                    new_referent = shuffle_point(referent, language.universe)
                    new_referents.append(new_referent)

                new_meaning = ModalMeaning(
                    points=new_referents, meaning_space=language.universe
                )
                # search the expressions for correct lot
                for candidate in expressions:
                    if candidate.meaning == new_meaning:
                        lot_expression = candidate.lot_expression

                new_expression = ModalExpression(
                    form=f"shuffled_{expression.form}_{i}",
                    meaning=new_meaning,
                    lot_expression=lot_expression,
                )
                new_vocab.append(new_expression)

            variant = ModalLanguage(
                expressions=new_vocab,
                name=f"{language.data['name']}_variant_{i}",
            )

            # ensure they are different; I don' think this is guaranteed
            # moreover, we can still end up equiv to one of the other naturals
            # assert tuple(sorted([e.lot_expression for e in variant.expressions])) != tuple(sorted([e.lot_expression for e in language.expressions]))

            variants.append(variant)

    variants = list(set(variants))  # weak guard against getting same lang again

    return variants


def perturb_meaning_space(
    universe: ModalMeaningSpace,
    languages: list[ModalLanguage],
    expressions: list[ModalExpression],
    num_variants_per_language: int = 1,
) -> dict[str, Any]:
    """Rotate a modal meaning space and obtain the resulting hypothetical variants resulting new meaning for each expression, for each language. Since there is no similarity structure within each axis, a 'rotation' of the meaning space amounts to shuffling the space of referents in the meaning space."""
    referents = universe.referents

    # A 'rotation' of the meaning space

    # TODO: make this all more general
    if len(referents) <= 6:
        perms = [x for x in permutations(referents) if x != referents]
        mappings = [
            {referents[idx]: perm[idx] for idx in range(len(referents))}
            for perm in perms[:num_variants_per_language]
        ]

    else:
        mappings = []
        for _ in range(num_variants_per_language):

            # only shuffle flavors
            flavors = [ref.flavor for ref in referents]
            shuffled_flavors = copy.deepcopy(flavors)
            # shuffled_referents = copy.deepcopy(referents)
            random.shuffle(shuffled_flavors)

            if shuffled_flavors == flavors:
                continue
            mappings.append(
                # Need to map each current meaning to the new meaning induced by the rotated meaning space
                # TODO: make the mapping (fo, fll) -> (fo, shuffled fl)
                {
                    referents[idx]: ModalMeaningPoint(
                        (referents[idx].force, shuffled_flavors[idx])
                    )
                    for idx in range(len(referents))
                }
            )

    # Iterate over languages and obtain their variants
    variants = []
    for language in languages:

        # TODO: you won't get more than one possible variant per language unless you shuffle the referents more than once. So do the shuffling num_variants times, and have a list of dicts, and iterate over it here.
        for variant_idx, referent_mapping in enumerate(mappings):
            new_vocab = []

            # Obtain a hypothetical variant of a language induced by the referent_mapping
            for expression in language.expressions:

                new_referents = tuple(
                    referent_mapping[referent]
                    for referent in expression.meaning.referents
                )

                new_meaning = ModalMeaning(
                    points=new_referents, meaning_space=language.universe
                )

                # search the expressions for correct lot
                for candidate in expressions:
                    if candidate.meaning == new_meaning:
                        lot_expression = candidate.lot_expression

                new_expression = ModalExpression(
                    form=f"perturbed_{expression.form}_{variant_idx}",
                    meaning=new_meaning,
                    lot_expression=lot_expression,
                )
                new_vocab.append(new_expression)

            variant = ModalLanguage(
                expressions=new_vocab,
                name=f"{language.data['name']}_variant_{variant_idx}",
            )

            variants.append(variant)

    # Since we actually want to compare each lang against its variants, its actually unclear that we should filter these variants for uniqueness.

    # variants = list(set(variants)) # weak guard against getting same lang again

    return variants


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(config: DictConfig):
    set_seed(config.seed)

    experiment = Experiment(
        config,
    )
    lang_fn = "artificial_languages"
    experiment.set_filepaths([lang_fn])
    if (
        not config.experiment.overwrites.languages.artificial
        and experiment.path_exists(lang_fn)
    ):
        print(
            "Language file found and will not be overwritten; skipping sampling of languages."
        )
        return

    print("natural...")
    experiment.load_files(["natural_languages", "expressions"])

    print("Shuffling natural languages ...")

    languages = perturb_meaning_space(
        universe=experiment.universe,
        languages=experiment.natural_languages["languages"],
        expressions=experiment.expressions,
        num_variants_per_language=config.experiment.sampling.variants.num_variants_per_language,
    )

    # languages = shuffle_languages_by_expression(
    #     languages=experiment.natural_languages["languages"],
    #     expressions=experiment.expressions,
    #     num_variants_per_language=config.experiment.sampling.shuffling.num_variants_per_language,
    #     )
    # languages = list(set(languages))

    experiment.artificial_languages = {"languages": languages, "id_start": None}
    experiment.write_files([lang_fn])


if __name__ == "__main__":
    main()
