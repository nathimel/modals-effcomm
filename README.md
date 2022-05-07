# An Efficient Communication Analysis of Modal Typology

This code accompanies XXX.

This repo has the following structure:  
  
- The _src_ folder contains the primary source code of the project.  
- The _scripts_ folder contains the main running scripts invoked from the command line (including a script to reproduce the main paper results).  
- The _configs_ folder contains parameter configurations for running different experiments.  
- The _data_ folder contains natural language modal data, sourced from [this database](https://github.com/CLMBRs/modal-typology).
- The _outputs_ folder contains outputs from scripts, including artificial language data, plots, etc.  

## Structure of this codebase
  
Generation:  

- Expression generating from the set of meanings using a boolean formula minimization heuristic
- Sampling expresions into languages
- Generating optimal languages using an evolutionary algorithm
  
Adding natural language data:

- Loading modal data from database stored at modal-typology
- Constructing each natural language as a language that can be measured for the trade-off
  
Measuring of languages

- Complexity
- Communicative Cost
- Satisfaction of semantic universals (independence of force and flavor)
- Optimality wrt a pareto frontier
  
## Requirements  

Get the required packages by running `conda env create -f environment.yml`
  
## Replicating the experimental results

The main experimental results can be reproduced by running the script `scripts/main_results.sh`.
