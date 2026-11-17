# Task 2 – Greedy vs Dynamic Programming (9 marks)

**File:** `Source_Code/knapsack.py` · **Output:** `Output/output.txt`

Solution A: fractional knapsack by value/weight ratio. Solution B: 0/1 knapsack by DP with item reconstruction. Also a whole-item ratio greedy used to expose the failure.

- 2.1 normal case with the greedy decision sequence.
- 2.2 counterexample (P, Q, R; capacity 50): greedy 160 ≠ DP 220; first bad commitment is P.
- 2.3 counts key evaluations, DP cell updates, table size, and solution quality over 2000 random instances.
- 2.4 fast-and-near-optimal requirement measured on n = 1000 / 2000.

Run: `cd Source_Code && python3 knapsack.py` (about 30 s because of the large DP runs)
