# CSA06 – Design and Analysis of Algorithms
## Assignment 4 – Part II (CO4): Algorithm Engineering – Implement, Test, Debug & Optimise

Course outcome **CO4** – solve optimisation problems using Dynamic Programming and Greedy strategies.  
Individual assignment · 50 marks · Language: **Python 3** (standard library only, no installs needed)

| Student | Register No. |
|---|---|
| Rithika G | _fill in_ |

## Repository layout

```
CO4B_Assignment/
├── README.md
├── run_all.sh                     # runs all six programs and refreshes every Output/output.txt
├── Report/
│   ├── CO4B_Report.docx           # full report (evidence, traces, predictions, interpretation, source appendix)
│   └── CO4B_Report.pdf
├── Task1_WordWrap/       (8 marks)  Source_Code/word_wrap.py        Output/output.txt
├── Task2_Knapsack/       (9 marks)  Source_Code/knapsack.py         Output/output.txt
├── Task3_Routing/       (10 marks)  Source_Code/routing.py          Output/output.txt
├── Task4_AssemblyLine/   (7 marks)  Source_Code/assembly_line.py    Output/output.txt
├── Task5_MST/            (7 marks)  Source_Code/mst.py              Output/output.txt
└── Task6_TSP/            (9 marks)  Source_Code/tsp_dp.py           Output/output.txt
```

## How to run

```bash
python3 --version          # 3.8 or newer
bash run_all.sh            # everything (about 1 minute; Task 2 and Task 6 contain timing experiments)
# or one task:
cd Task3_Routing/Source_Code && python3 routing.py
```

Counts of states, operations, comparisons, rounds and scans are deterministic (fixed random seeds).
Wall-clock times and memory figures depend on the machine, so they will differ slightly from the report.

## Results at a glance

| Task | Topic | Headline result |
|---|---|---|
| 1 | Word wrap, DP | W = 20: minimum penalty **144** (greedy first-fit 160); W = 16 / 24 / 30 give 281 / 72 / 38 |
| 2 | Fractional greedy vs 0/1 DP | Counterexample P(10,60) Q(20,100) R(30,120), capacity 50: greedy **160** vs DP **220**; greedy worse in 903 of 2000 random cases |
| 3 | Dijkstra, Bellman-Ford, Floyd, Warshall | Negative edge G→F(−5): Dijkstra gives F = 10, H = 14; Bellman-Ford gives F = 9, H = 13; negative cycle E→D→E (−3) detected on pass 8 |
| 4 | Assembly line scheduling, DP | Minimum production time **38**, lines [1,2,1,2,2,1]; transfer 2→20 or slow station: 39 with a different route |
| 5 | Kruskal, Prim, Borůvka | MST cost **31**; with ties the graph has **8** MSTs and different algorithms return different (equally valid) edge sets |
| 6 | TSP, Held-Karp DP | Hub→D→C→G→F→E→B→A→Hub, cost **48**; DP = brute force on 4 locations (32); states = n·2^(n−1) |

## Software engineering notes

- Algorithm functions return data; separate functions print the traces.
- Every program validates input (word longer than width, negative costs, disconnected graph, non-square matrix, unequal line lengths) and raises a clear error.
- Each task prints intermediate evidence (DP tables, decision traces, finalisation order, edge-selection order, state counts) and boundary/failure tests.
