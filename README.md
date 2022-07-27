# Modal Semantic Universals Optimize the Simplicity/Informativeness Trade-off

This code accompanies the following paper:

> N. Imel and S. Steinert-Threlkeld, Modal semantic universals optimize the simplicity/informativeness
trade-off, in _Proceedings of Semantics and Linguistic Theory (SALT 32)_, 2022.

The repo contains code for constructing artificial languages and measuring them for communicative efficiency. The codebase is organized around the following steps of the experiment.

## Setting up an experiment

A single file specifies the parameters and filepaths for an experiment, e.g. `salt.yml`. These will include:

- size of the semantic space to measure (number of quantificational forces and modal flavors).
- vocabulary size for artificial modal languages
- the number of total languages to generate
- how long to run algorithm to estimate optimal languages

## Sampling languages

Generate a large and diverse sample of mathematically possible languages

This is accomplished by the following steps:

- Expression generating from the set of meanings
- Sampling expressions into languages
- Use an evolutionary algorithm to estimate the optimal languages
- Explore the space of possible languages using the same algorithm

## Analyzing the simplicity/informativeness trade-off

Next, we analyze the resulting sample for the relationship between efficiency and naturalness.
The notion of naturalness we use tracks closeness of languages to actual modal typological facts by measuring the proportion of a language satisfying a modal semantic universal.
  
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
│       │   ├── dominant.yml
│       │   └── artificial.yml
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

Additionally, this project [the artificial language toolkit (ALTK)](https://github.com/nathimel/altk). Install the correct version via git with

`python3 -m pip install git+https://github.com/nathimel/altk.git@07bfeec0fff2b99641922832e64938f61f5a634e`
  
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

`python3 src/estimate_pareto_frontier.py path_to_config`

`python3 src/measure_tradeoff.py path_to_config`

`python3 src/analyze.py path_to_config`
</details>

## Citation

To cite this work, please use the following:

```
@inproceedings{Imel2022,
  author    = {Imel, Nathaniel, and Shane Steinert-Threlkeld},
  title     = {Modal semantic universals optimize the simplicity/informativeness trade-off},
  year      = {2022},
  booktitle = {Proceedings of Semantics and Linguistic Theory (SALT 32)},
}
```
