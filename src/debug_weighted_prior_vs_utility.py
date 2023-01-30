from modals.modal_language import ModalExpression, ModalLanguage, ModalMeaning, ModalMeaningPoint, ModalMeaningSpace

from altk.effcomm.informativity import informativity

from misc import file_util
import numpy as np

# Build one language and analyze in terms of two priors, two utility funcs

IMPOSSIBILITY = "impossibility"
NONNECESSITY = "nonnecessity"

EPISTEMIC = "epistemic"
DEONTIC = "deontic"
CIRCUMSTANTIAL = "circumstantial"
TELEOLOGICAL = "teleological"


space = ModalMeaningSpace(
    forces=[IMPOSSIBILITY, NONNECESSITY], 
    flavors=[EPISTEMIC, DEONTIC, CIRCUMSTANTIAL, TELEOLOGICAL],
    )

# maximally ambiguous meaning is collection of all points
points = [ModalMeaningPoint(force=force, flavor=flavor) for force in space.forces for flavor in space.flavors]

# single expression
language_ambig = ModalLanguage(
    expressions=[
        ModalExpression(
            form="word", meaning=ModalMeaning(
                points=points,
                meaning_space=space,
            ),
            lot_expression=None # We're not measuring complexity rn, so don't worry
        )
    ],
)

language_precise = ModalLanguage(
    expressions=[
        ModalExpression(
            form="imp,ep",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=EPISTEMIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,deon",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=DEONTIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),

        ModalExpression(
            form="non,ep",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=EPISTEMIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,deon",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=DEONTIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
    ]
)

# TRY NO DEONTIC LEXICALIZED
language_no_deontic = ModalLanguage(
    expressions=[
        ModalExpression(
            form="imp,ep",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=EPISTEMIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        # ModalExpression(
        #     form="imp,deon",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=DEONTIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="imp,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),

        ModalExpression(
            form="non,ep",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=EPISTEMIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        # ModalExpression(
        #     form="non,deon",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=NONNECESSITY, flavor=DEONTIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="non,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
    ]
)


# TRY NO DEONTIC OR EPISTEMIC LEXICALIZED
language_neither = ModalLanguage(
    expressions=[
        # ModalExpression(
        #     form="imp,ep",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=EPISTEMIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        # ModalExpression(
        #     form="imp,deon",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=DEONTIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="imp,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),

        # ModalExpression(
        #     form="non,ep",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=NONNECESSITY, flavor=EPISTEMIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        # ModalExpression(
        #     form="non,deon",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=NONNECESSITY, flavor=DEONTIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="non,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
    ]
)


language_no_epistemic_yes_deontic = ModalLanguage(
    expressions=[
        # ModalExpression(
        #     form="imp,ep",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=EPISTEMIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="imp,deon",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=DEONTIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="imp,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=IMPOSSIBILITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),

        # ModalExpression(
        #     form="non,ep",
        #     meaning=ModalMeaning(
        #         points=[ModalMeaningPoint(force=NONNECESSITY, flavor=EPISTEMIC)],
        #     meaning_space=space,
        #     ),
        #     lot_expression=None,
        # ),
        ModalExpression(
            form="non,deon",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=DEONTIC)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,circ",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=CIRCUMSTANTIAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
        ModalExpression(
            form="non,tel",
            meaning=ModalMeaning(
                points=[ModalMeaningPoint(force=NONNECESSITY, flavor=TELEOLOGICAL)],
            meaning_space=space,
            ),
            lot_expression=None,
        ),
    ]
)

uniform_prior = np.ones(8)/8
weighted_prior = file_util.load_prior("outputs/cogsci/base/weighted_utility_linear_search/ratio=10/utility.yml") # bc they're the same exact contents
weighted_prior = space.prior_to_array(weighted_prior)


base_utility = file_util.load_utility("half_credit")
# 10:1
utility_weights = file_util.load_prior("outputs/cogsci/base/weighted_utility_linear_search/ratio=10/utility.yml")

# normalize so that informativity <= 1
# total = sum([float(weight) for weight in utility_weights.values()])
z = max([float(weight) for weight in utility_weights.values()])
weights_normed = {}
for point in space.referents:
    weight_normed = float(utility_weights[point.data]) / z
    weights_normed[point.data] = weight_normed
# reassign
utility_weights = weights_normed

# Weight utility function
# u(p, p') weight(p) * ( fo(p) = fo(p') + fo(p) = fo(p') )
weighted_utility = lambda m, m_: utility_weights[m.data] * base_utility(m, m_)


# Set language
language = language_no_epistemic_yes_deontic


# compute informativity for three cases:

# 1: Flat prior, flat utility

flat_flat = informativity(
    language=language,
    prior=uniform_prior,
    utility=base_utility,
)

# 2: Flat prior, weighted utility,

flat_weighted = informativity(
    language=language,
    prior=uniform_prior,
    utility=weighted_utility,
)


# 3: Weighted prior, flat utility
weighted_flat = informativity(
    language=language,
    prior=weighted_prior,
    utility=base_utility,
)


print("--------------------------------------------------------------------")
# print("results for language that is maximally precise but lacks deontic:")
# print("results for maximally ambiguous language with one word")
# print("results for perfectly precise language")
print()
print("Flat prior, flat utility")
print()
print(flat_flat)
print("-------------------------")
print("Flat prior, weighted utility")
print()
print(flat_weighted)
print("-------------------------")
print("Weighted prior, flat utility")
print(weighted_flat)
print()
print("--------------------------------------------------------------------")
