# An Efficient Communication Analysis of Modal Typology

This code accompanies the following paper:

> N. Imel and S. Steinert-Threlkeld, Modals in natural language optimize the simplicity/informativeness
trade-off, in _Proceedings of Semantics and Linguistic Theory (SALT 32)_, 2022.

The repo contains code for constructing artificial languages and measuring them for communicative efficiency. In particular, the codebase is organized around the following steps

## Setting up an experiment
A single file specifies the parameters and filepaths for an experiment, e.g. `half_credit_literal.yml`. These will include:
- size of the semantic space to measure (number of quantificational forces and modal flavors).
- vocabulary size for artificial modal languages
- the number of total languages to generate
- how long to run algorithm to estimate optimal languages

## Sampling languages
Generate a large and diverse sample of mathematically possible languages

This is accomplished by the following steps:
- Expression generating from the set of meanings
- Sampling expresions into languages
- Use an evolutionary algorithm to estimate the optimal languages
- Explore the full space of possible languages using the same algorithm

A separate step is adding natural language data:
- Load data obtained from [A Database of Modal Typology](https://github.com/CLMBRs/modal-typology).
- Convert each natural language into the appropriate experiment data structure

## Analyzing the simplicity/informativeness trade-off
Next, we analyze the resulting sample for the relationship between efficiency and naturalness.
The notion of naturalness we use tracks 'closeness of languages to actual modal typological facts' by measuring the proportion of a language satisfying a modal semantic universal.
  
Measuring of languages:
- Complexity
- Communicative Cost
- Satisfaction of semantic universals (independence of force and flavor)
- Optimality wrt a pareto frontier

Analysis:
- compute correlation between naturalness and optimality
- plot tradeoff

To this end, the codebase is structured as follows:

```bash
.
├── configs
│ # YAML files that define experimental parameters for
│ # modal languages, sample size, the type of naturalness to measure,
│ # file output paths, etc.
├── data 
│ # where natural languages are stored to be read in for the experiment
├── outputs
│ # readable intermediate output and experimental results, e.g.
│ # generated languages,
│ # the progress of the experiment printed to stdout,
│ # and final results, including dataframes and plots.
├── scripts
│   └── run_full_experiment.sh # the main script to run
└── src 
    ├── # python scripts to construct the space of possible languages, 
    │   # sample from this space, 
    │   # and measure the communicative efficiency of the sample 
    │   # by estimating a Pareto frontier using an evolutionary algorithm
    ├── modals
    │   # module that defines the meaning space for modals, 
    │   # the modal language data structure,
    │   # the measures of complexity and communicative cost, 
    │   # and mutations that may apply during the evolutionary algorithm
```    

## Requirements  

Get the required packages by running `conda env create -f environment.yml`
  
## Replicating the experimental results

The main experimental results can be reproduced by running `./scripts/run_full_experiment.sh configs/main_results/config.yml`.
