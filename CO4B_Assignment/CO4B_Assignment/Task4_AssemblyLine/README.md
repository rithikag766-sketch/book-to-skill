# Task 4 – Smart Manufacturing Optimisation (7 marks)

**File:** `Source_Code/assembly_line.py` · **Output:** `Output/output.txt`

Two-line assembly scheduling DP: `f[l][i] = a[l][i] + min(stay, transfer)`, back-pointers rebuild the route.

- 4.1/4.2 minimum time 38, route diagram, per-station stay-vs-transfer trace.
- 4.3 transfer time raised (prediction printed first).
- 4.4 slow station on line 1 (route change and explanation).
- 4.5 three-line extension is explained in the report (not implemented, as required).
- Boundary tests: one station, ties, unequal lengths, negative times.

Run: `cd Source_Code && python3 assembly_line.py`
