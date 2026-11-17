# Task 3 – Routing Engine under Changing Network Conditions (10 marks)

**File:** `Source_Code/routing.py` · **Output:** `Output/output.txt`

8 vertices, 13 directed edges.

- Stage A: Dijkstra (distances, paths, predecessors, finalisation order).
- Stage B: negative edge G→F(−5) with a printed prediction; Dijkstra vs Bellman-Ford.
- Stage C: negative cycle D↔E (−3) detected by the extra |V|-th Bellman-Ford pass, cycle reported, no distances returned; Floyd cross-check.
- Stage D: Floyd distance matrix and Warshall reachability matrix.

Run: `cd Source_Code && python3 routing.py`
