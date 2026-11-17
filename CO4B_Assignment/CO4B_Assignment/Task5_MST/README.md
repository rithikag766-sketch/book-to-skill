# Task 5 – Three Greedy Engineers, One Network (7 marks)

**File:** `Source_Code/mst.py` · **Output:** `Output/output.txt`

Kruskal (disjoint set), Prim (heap), Borůvka (rounds of cheapest outgoing edges) on one 8-vertex, 13-edge graph.

- Edge-selection traces for each algorithm.
- Tied-weight graph: 8 MSTs (exhaustive check), different algorithms/tie-breaks return different but equally optimal edge sets.
- Operation counts on sparse, dense and large sparse random graphs for the deployment discussion.
- Disconnected graphs are rejected.

Run: `cd Source_Code && python3 mst.py`
