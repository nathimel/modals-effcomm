#!/bin/sh

for RATIO in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
do 
    python3 src/cogsci_measure_tradeoff.py configs/cogsci/base.yml outputs/cogsci/base/weighted_utility_linear_search/ratio=$RATIO
done