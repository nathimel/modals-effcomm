"""Script for estimating probability distribution over modal meaning points from a dataset."""
import itertools
import sys
import spacy
import pandas as pd
from spacy.tokens import Doc
from misc import file_util
from modals.modal_meaning import ModalMeaningSpace
from tqdm import tqdm


def generate_uniform(space: ModalMeaningSpace) -> dict[str, float]:
    """Generate a uniform communicative need distribution / prior over meaning points."""
    return {point.name: 1 / len(space) for point in space.referents}

def renumber_sentences(dfs: list[pd.DataFrame]) -> list[pd.DataFrame]:
    """Helper function to renumber the sentence_ids to be unique wrt all sentences in the dataset, not just within a file."""
    sentence_count = 0
    for i, df in enumerate(dfs):
        df["sentence_id"] += sentence_count
        sentence_count = df["sentence_id"].max() + 1
    return dfs

##############################################################################
# Hard-coded constants / annotations necessary to extract prior.
##############################################################################

# Map Modality Corpus 'gold_modal' annotations to experiment flavors
labels_to_flavors = {
    "S_knowledge": "epistemic",
    "S_rules": "deontic",
    "S_world": "circumstantial",
}

#  Tokens instantiating epistemic, deontic or circumstantial:
gold_tokens = {
    "would",
    "ought",
    "may",
    "was",
    "might",
    "shall",
    "ca",
    "could",
    "need",
    "can",
    "'d",  # would, e.g. I'd, we'd, they'd
    "should",
    "must",
}

# Hand annotate forces for each token, excluding will/shall
token_to_force = {
    "would": "strong",
    "ought": "strong",
    "may": "weak",
    "was": None,
    "might": "weak",
    "shall": None,
    "ca": "weak",
    "could": "weak",
    "need": "strong",
    "can": "weak",
    "'d": "strong",
    "should": "strong",
    "must": "strong",
}

##############################################################################
# Main driver code
##############################################################################


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/estimate_pareto_frontier.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    print("Estimating prior...")

    config_fn = sys.argv[1]
    configs = file_util.load_configs(config_fn)
    prior_fn = configs["file_paths"]["prior"]
    prior_df_fn = configs["file_paths"]["prior_df"]
    space = file_util.load_space(configs["file_paths"]["meaning_space"])
    modality_corpus = configs["file_paths"]["modality_corpus"]

    print("Constructing uniform prior")
    prior = generate_uniform(space)

    if True: # TODO: move option for uniform/estimated to config file

        ##########################################################################
        # Load and parse corpus to extract auxiliaries
        ##########################################################################

        print("Loading dataframes...")
        # list of filenames of each dataset used
        fns = [fn for folder in modality_corpus for fn in modality_corpus[folder].values()]
        # load dataframe of all files concatenated    
        df_all = pd.concat(renumber_sentences([pd.read_csv(fn, sep="\t") for fn in fns]))

        # for dev
        # df_all = df_all.head(n=1000)

        # run sentences through a parser to extract the verbal auxiliaries
        nlp = spacy.load("en_core_web_md")

        # Run spacy pipeline on all sentences from full dataframe
        sentence_id_max = df_all["sentence_id"].max()
        dataset = [
            list(df_all[df_all["sentence_id"] == i]["token"])
            for i in range(sentence_id_max + 1)
        ]  # a list of lists

        print("Parsing and tagging sentences...")
        docs = [nlp(Doc(nlp.vocab, sent)) for sent in tqdm(dataset)]  # this takes about 6m

        # inject tags back as columns for the dataframe
        pos_tags = [tok.pos_ for doc in docs for tok in doc]
        df_all["POS"] = pos_tags

        # Subset just the verbal auxiliaries
        df_aux = df_all[df_all["POS"] == "AUX"]

        # Correct typos, e.g. S-knowledge to S_knowledge
        df_aux["gold_modal"] = df_aux["gold_modal"].str.replace(
            r"([a-z])\-([a-z])", r"\1_\2", n=0, case=False
        )

        # lowercase all auxiliaries to collapse e.g, Can and can
        df_aux["token"] = df_aux["token"].str.lower()

        ##########################################################################
        # Estimate relative frequencies of flavors
        ##########################################################################

        # replace gold_modal annotations with our flavors
        for label in labels_to_flavors:
            df_aux["gold_modal"] = df_aux["gold_modal"].str.replace(
                label, labels_to_flavors[label]
            )

        # drop any flavors not belonging, e.g. S_agent
        df_aux = df_aux[df_aux["gold_modal"].isin(labels_to_flavors.values())]

        # annotate forces by mapping a token to its force label
        token_dfs = []
        for token in token_to_force:
            df_token = df_aux[df_aux["token"] == token]
            df_token["force"] = token_to_force[token]
            token_dfs.append(df_token)

        df_force_flavor = pd.concat(token_dfs)
        df_force_flavor = df_force_flavor.rename(columns={"gold_modal": "flavor"})

        # Get number counts for force-flavor combinations
        # Note that the meaning space must be perfectly compatible with our hand-annotations
        point_counts = {point.name: 0 for point in space.referents}
        points_dfs = []
        for force, flavor in itertools.product(space.forces, space.flavors):
            # find occurrences of the meaning point in the data
            df_point = df_force_flavor[
                (df_force_flavor["force"] == force) & (df_force_flavor["flavor"] == flavor)
            ]
            points_dfs.append(df_point)
            # update our counts
            point = f"{force}+{flavor}"
            point_counts[point] = len(df_point)

        # Save a minimal dataframe of counts for later easy reference
        df_points = pd.concat(points_dfs)
        df_points = df_points.drop(columns=["sentence_id", "POS"])

        total = sum(point_counts.values())

        # convert counts to relative frequencies
        prior = {point: point_counts[point] / total for point in point_counts}

    ##########################################################################
    # Save results
    ##########################################################################

    # save prior for experiment
    file_util.save_prior(prior_fn, prior)
    # save dataframe of counts
    df_points.to_csv(prior_df_fn, index=False)

    print("done.")


if __name__ == "__main__":
    main()
