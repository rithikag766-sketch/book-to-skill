#!/usr/bin/env bash
# Runs every task and refreshes the Output/output.txt files.
set -e
cd "$(dirname "$0")"
run() { ( cd "$1/Source_Code" && python3 "$2" > ../Output/output.txt && echo "done: $1" ); }
run Task1_WordWrap word_wrap.py
run Task2_Knapsack knapsack.py
run Task3_Routing routing.py
run Task4_AssemblyLine assembly_line.py
run Task5_MST mst.py
run Task6_TSP tsp_dp.py
