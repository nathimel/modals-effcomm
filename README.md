# An Efficient Communication Analysis of Modal Typology

This code accompanies the following paper:

> N. Imel and S. Steinert-Threlkeld, Modals in natural language optimize the simplicity/informativeness
trade-off, in _Proceedings of Semantics and Linguistic Theory (SALT 32)_, 2022.

and an extension thereof. The codebase is structured to support computational experiments measuring natural and artificial modal vocabularies for communicative efficiency.

## Setting up an experiment

A single file specifies the parameters and filepaths for an experiment, e.g. `half_credit_literal.yml`. These will include:

- size of the semantic space to measure (number of quantificational forces and modal flavors).
- vocabulary size for artificial modal languages
- the number of total languages to generate
- how long to run algorithm to estimate optimal languages

## Sampling languages

Generate a large and diverse sample of mathematically possible languages.

This is accomplished by the scripts `generate_expressions.py` `sample_languages.py` and `estimate_pareto_frontier.py`, which perform the following steps:

- Expression generating from the set of meanings
- Sampling expresions into languages
- Use an evolutionary algorithm to estimate the optimal languages
- Explore the space of possible languages using the same algorithm

## Adding natural languages

To add the natural language modal inventories to measure in an experiment, we use the `add_natural_languages.py` script to:

- Load data obtained from [A Database of Modal Typology](https://github.com/CLMBRs/modal-typology), stored in this repo under [data/natural_languages](data/natural_languages/).
- Convert each natural language into the appropriate experiment data structure

## Estimating the communicative need distribution

To estimate the prior probability of a (force, flavor) meaning point, we obtain relative frequency statistics using the [Modality Corpus](https://github.com/OnlpLab/Modality-Corpus). Run the script `extract_prior.py` to:

- Load the data annotated for modal flavors, stored in this repo under [data/modality_corpus](data/modality_corpus/).
- Run each sentence through a parser to exract the verbal auxiliaries.
- Automatically annotate the modals for force
- Count the occurrences of the (force, flavor) pairs used in the experiment's meaning space.

## Analyzing the simplicity/informativeness trade-off

Finally, analyze the resulting pool of languages for the relationship between efficiency and naturalness. We directly measure natural languages for their efficiency, and the hypothetical languages for their efficiency and satisfaction with semantic universals (e.g. IFF, SAV, DLSAV).
  
Measuring of languages:

- Complexity
- Communicative Cost
- Satisfaction of semantic universal(s)
- Optimality w.r.t a Pareto frontier

Analysis:

- perform statistical analyses, including correlation between naturalness and optimality
- plot tradeoff

## Structure of the codebase

<details>
<summary>Map of repo</summary>
<br>

```bash
.
├── configs
│ # YAML files that define experimental parameters for
│ # modal languages, sample size, the type of naturalness to measure,
│ # file output paths, etc.
│   ├── half_credit_literal.yml
│   └── ...
├── data
│   └── natural_languages
│       ├── Gitksan
│       │   └── modals.csv
│       └── ...
├── outputs
│ # readable intermediate output and experimental results, e.g.
│   └── half_credit_literal
│       ├── analysis
│       │   │  # resulting dataframes and figures
│       │   ├── ...
│       │   ├── all_data.csv
│       │   └── plot.png
│       ├── expressions.yml
│       ├── languages
│       │   ├── # generated languages
│       │   ├── artificial.yml
│       │   └── natural.yml
│       └── system_output.txt # progress of the experiment printed to stdout,
├── scripts
│   └── run_full_experiment.sh # the main script to run
└── src
    │ # python scripts to construct the space of possible languages,
    │ # sample from this space,
    │ # and measure the communicative efficiency of the sample
    │ # by estimating a Pareto frontier using an evolutionary algorithm
    ├── ...
    ├── sample_languages.py
    └── modals
        │ # module that defines the meaning space for modals,
        │ # the modal language data structure,
        │ # measures of complexity and communicative cost,
        │ # and mutations that may apply during the evolutionary algorithm
        ├── ...
        └── modal_language.py
```
</details>

## Requirements  

Get the required packages by running

`conda env create -f environment.yml`

Additionally, this project requires [the artificial language toolkit (ALTK)](https://github.com/nathimel/altk). Install it via git with

`python3 -m pip install git+https://github.com/nathimel/altk.git@e20657a122a54ff607344f6dc8c4f04a34a06bd0`
  
## Replicating the experimental results

The main experimental results can be reproduced by running `./scripts/run_full_experiment.sh configs/salt.yml`.

This just runs the following python scripts, which can also be run individually:
<details>
<summary>individual scripts</summary>
<br>

`python3 src/create_folders.py path_to_config`

`python3 src/build_meaning_space.py path_to_config`

`python3 src/generate_expressions.py path_to_config`

`python3 src/sample_languages.py path_to_config`

`python3 src/add_natural_languages.py path_to_config`

`python3 src/extract_prior.py path_to_config`

`python3 src/estimate_pareto_frontier.py path_to_config`

`python3 src/measure_tradeoff.py path_to_config`

`python3 src/analyze.py path_to_config`
</details>

## Citation

To cite this work, please use the following:

```
@article{Imeletal2023,
  author    = {Imel, Nathaniel, and Guo, Qingxia, and Steinert-Threlkeld, Shane},
  title     = {An efficient communication analysis of modal typology},
  year      = {2023},
  journal = {lingbuzz},
  url = {https://ling.auf.net/lingbuzz/007392},
}
```
