# Task 6 – Last-Mile Delivery Route Optimisation (9 marks)

**File:** `Source_Code/tsp_dp.py` · **Output:** `Output/output.txt`

Held-Karp: `DP[S][j]` = cheapest path from the hub through exactly the set S ending at j; answer = min over j of `DP[FULL][j] + cost[j][hub]`.

- 6.3 hub + 7 deliveries: optimal route and cost 48.
- 6.4 hub + 4 deliveries validated against all 24 tours, plus 300 random instances.
- 6.5 states, transitions, time and peak memory for n = 4 … 14.
- Boundary tests: one delivery, bad matrices, asymmetric costs.

Run: `cd Source_Code && python3 tsp_dp.py` (about 10 s)
