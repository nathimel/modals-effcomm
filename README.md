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

# TODO

- update configs with universal (iff vs sav)
- read `TODO` comments in source, update `altk` accordingly

Slides: much improved; great job!! A few quick and minor thoughts:
State what Nauze's universal is on slide 2 (can vary in flavor or force but not both)
Informativeness slide: v close! Two things: (i) animate it :slightly_smiling_face: (ii) I think the thought bubble from the speaker should have one pair, the one they want to communicate, not both

Unrelated comments, but one long message while I work on the plane :slightly_smiling_face: (I honestly love working for a bit on planes lol before napping and/or catching up on movies, missed it during covid).  I did some debugging / refactoring stuff (you can check out shane-debugging branch if you're curious, can also update at our next meeting), and am v happy w/ the half_credit_literal results.  But the indicator_literal ones turn werid.  This is pareto_data.csv: note that there are two languages here, both with comm_cost 0.3333, but one has compl 12 and the other 14 (see rows 5/6).  So the latter one shouldn't be in there.  Any idea where this may be leaking in?
   Unnamed: 0              name  naturalness  simplicity  informativity  optimality    Language  comm_cost  complexity  counts
0           2   sampled_lang_62          1.0         NaN         0.1667      1.0000  artificial     0.8333           1       6
1           9  sampled_lang_332          1.0         NaN         0.2222      1.0000  artificial     0.7778           3       3
2          19   sampled_lang_62          1.0         NaN         0.3333      1.0000  artificial     0.6667           4       3
3           8   sampled_lang_62          1.0         NaN         0.5000      0.9999  artificial     0.5000           6       3
4           1   sampled_lang_62          1.0         NaN         0.5417      0.9999  artificial     0.4583          10       2
5          12   sampled_lang_62          1.0         NaN         0.6667      1.0000  artificial     0.3333          12       1
6           3   sampled_lang_62          1.0         NaN         0.6667      0.9999  artificial     0.3333          14       1
7           4   sampled_lang_62          1.0         NaN         0.7083      1.0000  artificial     0.2917          16       1
8          16   sampled_lang_62          1.0         NaN         0.7500      1.0000  artificial     0.2500          18       1
9           0   sampled_lang_62          1.0         NaN         0.8333      1.0000  artificial     0.1667          20       1
[FWIW, I noticed this b/c the generated plot had a "vertical line" in it from the interpolation, so I was tracing down which points were causing it, and found these two.]. Maybe it's a matter of rounding to e.g. 4 places before looking up non-dominated pts?