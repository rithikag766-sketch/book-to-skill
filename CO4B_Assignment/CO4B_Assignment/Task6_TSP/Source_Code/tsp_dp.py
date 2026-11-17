"""Task 6 - Last-mile delivery route optimisation: TSP with Dynamic Programming (Held-Karp).

Location 0 is the distribution hub; locations 1..n are deliveries.
S is a bitmask over the delivery locations: bit (k-1) set means location k has been visited.

    DP[S][j] = minimum cost of a path that STARTS at the hub, visits exactly the deliveries in S,
               and ENDS at delivery j (j must belong to S)
    base      DP[{j}][j]         = cost[0][j]
    recurrence DP[S][j]          = min over i in S\\{j} of  DP[S\\{j}][i] + cost[i][j]
    answer    min over j of      DP[FULL][j] + cost[j][0]          (return to hub)
"""
import itertools
import random
import time
import tracemalloc

INF = float("inf")


def validate_matrix(cost):
    n = len(cost)
    if n < 2:
        raise ValueError("need a hub and at least one delivery location")
    for i, row in enumerate(cost):
        if len(row) != n:
            raise ValueError("cost matrix must be square")
        for j, c in enumerate(row):
            if c < 0:
                raise ValueError(f"negative travel cost at ({i},{j})")
    return n - 1   # number of deliveries


def held_karp(cost):
    """Return (best_cost, route, stats). route is a list of location indices starting and ending at 0."""
    n = validate_matrix(cost)
    full = (1 << n) - 1
    dp = {}        # (mask, last) -> cost
    parent = {}    # (mask, last) -> previous last
    states = transitions = 0
    for j in range(1, n + 1):
        dp[(1 << (j - 1), j)] = cost[0][j]
        states += 1
    for mask in range(1, full + 1):
        for j in range(1, n + 1):
            bit = 1 << (j - 1)
            if not mask & bit or mask == bit:
                continue
            prev_mask = mask ^ bit
            best, arg = INF, -1
            for i in range(1, n + 1):
                if prev_mask & (1 << (i - 1)):
                    transitions += 1
                    cand = dp[(prev_mask, i)] + cost[i][j]
                    if cand < best:
                        best, arg = cand, i
            dp[(mask, j)] = best
            parent[(mask, j)] = arg
            states += 1
    best, last = INF, -1
    for j in range(1, n + 1):
        cand = dp[(full, j)] + cost[j][0]
        if cand < best:
            best, last = cand, j
    route, mask, cur = [0], full, last
    stack = []
    while cur != 0:
        stack.append(cur)
        nxt = parent.get((mask, cur), 0)
        mask ^= 1 << (cur - 1)
        cur = nxt
    route += stack[::-1] + [0]
    return best, route, {"states": states, "transitions": transitions, "table_entries": len(dp)}


def brute_force(cost):
    n = len(cost) - 1
    best, best_perm, all_routes = INF, None, []
    for perm in itertools.permutations(range(1, n + 1)):
        path = (0,) + perm + (0,)
        c = sum(cost[a][b] for a, b in zip(path, path[1:]))
        all_routes.append((path, c))
        if c < best:
            best, best_perm = c, path
    return best, best_perm, all_routes


def name(k, labels):
    return labels[k]


def fmt_route(route, labels):
    return " -> ".join(labels[k] for k in route)


def print_matrix(cost, labels):
    print("      " + "".join(f"{l:>5}" for l in labels))
    for i, row in enumerate(cost):
        print(f"  {labels[i]:<4}" + "".join(f"{c:>5}" for c in row))


def random_cost(n_delivery, seed):
    rnd = random.Random(seed)
    n = n_delivery + 1
    pts = [(rnd.randint(0, 100), rnd.randint(0, 100)) for _ in range(n)]
    return [[0 if i == j else abs(pts[i][0] - pts[j][0]) + abs(pts[i][1] - pts[j][1]) for j in range(n)]
            for i in range(n)]


if __name__ == "__main__":
    LABELS = ["Hub", "A", "B", "C", "D", "E", "F", "G"]
    COST = [
        [0, 12, 10, 19, 8, 14, 11, 16],
        [12, 0, 3, 7, 2, 9, 15, 6],
        [10, 3, 0, 6, 20, 5, 8, 13],
        [19, 7, 6, 0, 4, 12, 9, 7],
        [8, 2, 20, 4, 0, 10, 6, 11],
        [14, 9, 5, 12, 10, 0, 4, 8],
        [11, 15, 8, 9, 6, 4, 0, 5],
        [16, 6, 13, 7, 11, 8, 5, 0],
    ]

    print("########## 6.1 / 6.2  model and state (see report) ##########")
    print("  state = (S, j): S = set of deliveries already visited, j = current location")
    print("  two partial routes that both end at E but have visited {A,B,E} vs {C,D,E} are NOT interchangeable,")
    print("  because they still have different sets of locations left to visit.\n")

    print("########## 6.3  Route optimisation: hub + 7 delivery locations ##########")
    print("  Input cost matrix:")
    print_matrix(COST, LABELS)
    best, route, st = held_karp(COST)
    print(f"\n  Optimal route : {fmt_route(route, LABELS)}")
    print(f"  Visit order   : {' , '.join(LABELS[k] for k in route[1:-1])}")
    legs = [f"{LABELS[a]}->{LABELS[b]}={COST[a][b]}" for a, b in zip(route, route[1:])]
    print(f"  Leg costs     : {', '.join(legs)}")
    print(f"  Minimum Travel Cost = {best}   (leg sum check = {sum(COST[a][b] for a, b in zip(route, route[1:]))})")
    print(f"  DP work       : {st}")
    print()

    print("########## 6.4  Validation: hub + 4 deliveries (exhaustive enumeration) ##########")
    small_labels = LABELS[:5]
    small = [row[:5] for row in COST[:5]]
    print_matrix(small, small_labels)
    bf_best, bf_path, all_routes = brute_force(small)
    print("\n  All 4! = 24 candidate routes:")
    for path, c in sorted(all_routes, key=lambda r: r[1]):
        print(f"    {fmt_route(path, small_labels):<28} cost = {c}")
    dp_best, dp_route, dp_st = held_karp(small)
    print(f"\n  Exhaustive optimum : {bf_best}  via {fmt_route(bf_path, small_labels)}")
    print(f"  DP optimum         : {dp_best}  via {fmt_route(dp_route, small_labels)}")
    print(f"  Costs agree: {bf_best == dp_best}")
    mismatches = 0
    for s in range(300):
        c = random_cost(5, s)
        if held_karp(c)[0] != brute_force(c)[0]:
            mismatches += 1
    print(f"  Extra check: 300 random 5-delivery instances, DP vs brute force mismatches = {mismatches}")
    print()

    print("########## 6.5  State-space growth ##########")
    print(f"  {'n':>3}{'DP states':>12}{'n*2^(n-1)':>12}{'transitions':>14}{'time (s)':>11}{'peak memory (MB)':>19}"
          f"{'n! (brute force routes)':>25}")
    import math
    for n in range(4, 15):
        cm = random_cost(n, seed=n)
        tracemalloc.start()
        t0 = time.perf_counter()
        b, r, s = held_karp(cm)
        dt = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"  {n:>3}{s['states']:>12,}{n * 2 ** (n - 1):>12,}{s['transitions']:>14,}{dt:>11.3f}"
              f"{peak / 1e6:>19.2f}{math.factorial(n):>25,}")

    print()
    print("########## Boundary / failure tests ##########")
    b, r, _ = held_karp([[0, 5], [7, 0]])
    print(f"  1 delivery: cost={b}, route={r} (expected 5+7=12)")
    try:
        held_karp([[0, 1], [1, 0, 3]])
    except ValueError as e:
        print("  non-square matrix rejected ->", e)
    try:
        held_karp([[0, -1], [1, 0]])
    except ValueError as e:
        print("  negative cost rejected ->", e)
    asym = [[0, 1, 9], [9, 0, 1], [1, 9, 0]]
    b, r, _ = held_karp(asym)
    print(f"  asymmetric costs handled: cost={b}, route={r} (expected 3 via 0->1->2->0)")
