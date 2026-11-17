"""Task 4 - Two-line assembly scheduling with Dynamic Programming.

Inputs (stations numbered 1..n)
    a[l][i]  processing time of station i on line l (l = 0 or 1)
    t[l][i]  time to transfer AWAY from line l after station i (i = 1..n-1), i.e. into the other line
    e[l]     entry time onto line l            x[l]  exit time from line l

DP definition
    f[l][i]  fastest time for a product to be COMPLETED at station i of line l
    f[l][1] = e[l] + a[l][1]
    f[l][i] = a[l][i] + min( f[l][i-1]            (stay),
                              f[1-l][i-1] + t[1-l][i-1]   (transfer in from the other line) )
    answer  = min( f[0][n] + x[0], f[1][n] + x[1] )
Back-pointers keep which option was chosen so the route can be rebuilt.
"""


def validate(a, t, e, x):
    n = len(a[0])
    if n == 0 or len(a[1]) != n:
        raise ValueError("both lines need the same, non-zero number of stations")
    if len(t[0]) != n - 1 or len(t[1]) != n - 1:
        raise ValueError("transfer lists need n-1 entries")
    if any(v < 0 for row in (a[0], a[1], t[0], t[1], list(e), list(x)) for v in row):
        raise ValueError("times must be non-negative")
    return n


def solve(a, t, e, x):
    n = validate(a, t, e, x)
    f = [[0] * n for _ in range(2)]
    came_from = [[None] * n for _ in range(2)]        # line index we arrived from at station i
    trace = []                                         # per-station decision records
    for l in (0, 1):
        f[l][0] = e[l] + a[l][0]
    for i in range(1, n):
        rec = {"station": i + 1}
        for l in (0, 1):
            stay = f[l][i - 1] + a[l][i]
            move = f[1 - l][i - 1] + t[1 - l][i - 1] + a[l][i]
            if stay <= move:
                f[l][i], came_from[l][i] = stay, l
                pick = "stay"
            else:
                f[l][i], came_from[l][i] = move, 1 - l
                pick = "transfer"
            rec[l] = (stay, move, pick)
        trace.append(rec)
    finish = [f[0][n - 1] + x[0], f[1][n - 1] + x[1]]
    last = 0 if finish[0] <= finish[1] else 1
    best = finish[last]
    route = [0] * n
    route[n - 1] = last
    for i in range(n - 1, 0, -1):
        route[i - 1] = came_from[route[i]][i]
    return best, route, f, trace, finish


def print_trace(a, e, f, trace, finish, x):
    print(f"  Station 1: f1 = {e[0]}+{a[0][0]} = {f[0][0]},  f2 = {e[1]}+{a[1][0]} = {f[1][0]}   (entry only)")
    print(f"  {'Stn':<4}| {'L1 stay':>8}{'L1 transfer':>12}{'pick':>10} | {'L2 stay':>8}{'L2 transfer':>12}{'pick':>10} | f1  f2")
    for rec in trace:
        s1, m1, p1 = rec[0]
        s2, m2, p2 = rec[1]
        i = rec["station"] - 1
        print(f"  {rec['station']:<4}| {s1:>8}{m1:>12}{p1:>10} | {s2:>8}{m2:>12}{p2:>10} | {f[0][i]:>2}  {f[1][i]:>2}")
    print(f"  Exit: line1 {f[0][-1]}+{x[0]} = {finish[0]}, line2 {f[1][-1]}+{x[1]} = {finish[1]}")


def print_route(route, best):
    print("  Entry")
    prev = None
    for i, l in enumerate(route):
        if prev is not None and l != prev:
            print(f"    | TRANSFER (line {prev + 1} -> line {l + 1})")
        else:
            print("    |")
        print(f"  Line {l + 1} - Station {i + 1}")
        prev = l
    print("    |")
    print("  Exit")
    transfers = [(i + 1, route[i] + 1, route[i + 1] + 1) for i in range(len(route) - 1) if route[i] != route[i + 1]]
    print(f"  Lines per station: {[l + 1 for l in route]}")
    print(f"  Transfer points (after station, from line, to line): {transfers}")
    print(f"  Minimum Production Time = {best}")


def run(title, a, t, e, x, show_trace=True):
    print(f"--- {title} ---")
    best, route, f, trace, finish = solve(a, t, e, x)
    if show_trace:
        print_trace(a, e, f, trace, finish, x)
    print_route(route, best)
    print()
    return best, route


A1 = [7, 9, 3, 4, 8, 4]
A2 = [8, 5, 6, 4, 5, 7]
T1 = [2, 3, 1, 3, 4]         # leave line 1 after station i
T2 = [2, 1, 2, 2, 1]         # leave line 2 after station i
E = [2, 4]
X = [3, 2]

if __name__ == "__main__":
    print("INPUT")
    print("  Line 1 times:", A1, " transfer-from-line-1:", T1, " entry/exit:", E[0], X[0])
    print("  Line 2 times:", A2, " transfer-from-line-2:", T2, " entry/exit:", E[1], X[1])
    print()
    print("########## 4.1 + 4.2 base case ##########")
    base_best, base_route = run("Base case", [A1, A2], [T1, T2], E, X)

    # ------------------------------------------------------------------ 4.3
    print("########## 4.3 Predict before you execute ##########")
    print("  Change: transfer time leaving line 1 after station 1 (T1[1]) rises from 2 to 20.")
    print("  PREDICTION (recorded before running):")
    print("   * The route WILL change. The base route starts on line 1 and immediately transfers to line 2")
    print("     after station 1; that transfer is the decision most likely affected.")
    print("   * A product starting on line 1 would now stay for station 2 (cost 9) instead of paying 20,")
    print("     or the product would start on line 2 (entry 4 + 8 = 12) and avoid the transfer altogether.")
    print("   * The minimum total time should INCREASE (the base optimum used the now-expensive edge), but by")
    print("     far less than 18, because cheaper alternatives exist.")
    t1_mod = T1.copy(); t1_mod[0] = 20
    mod_best, mod_route = run("Modified: T1[1] = 20", [A1, A2], [t1_mod, T2], E, X)
    print(f"  OBSERVED: route changed = {mod_route != base_route}; time {base_best} -> {mod_best} "
          f"(change {mod_best - base_best:+d})")
    print(f"  Lines per station: base {[l + 1 for l in base_route]}  modified {[l + 1 for l in mod_route]}")
    print()

    # ------------------------------------------------------------------ 4.4
    print("########## 4.4 Production disruption ##########")
    a1_slow = A1.copy(); a1_slow[2] = 25     # line 1, station 3 temporarily slow (3 -> 25)
    print("  Change: line 1 station 3 slows from 3 to 25.")
    print("  PREDICTION: the base route uses line 1 at station 3 after a transfer; the optimiser should avoid it,")
    print("  staying on line 2 through station 3, and total time should rise by well under 22.")
    d_best, d_route = run("Disruption: line 1 station 3 = 25", [a1_slow, A2], [T1, T2], E, X)
    print(f"  Route changed: {d_route != base_route}; time {base_best} -> {d_best} ({d_best - base_best:+d})")
    first_diff = next((i + 1 for i in range(len(d_route)) if d_route[i] != base_route[i]), None)
    print(f"  First station where the route differs from the base route: {first_diff}")
    print()

    # ------------------------------------------------------------------ boundaries
    print("########## Boundary / failure tests ##########")
    b, r, *_ = solve([[5], [3]], [[], []], [1, 1], [1, 1])
    print(f"  n = 1 station: time={b}, route lines={[l + 1 for l in r]}  (expected 1+3+1 = 5 on line 2)")
    b, r, *_ = solve([[1, 1, 1], [1, 1, 1]], [[0, 0], [0, 0]], [0, 0], [0, 0])
    print(f"  all-equal times, zero transfers: time={b}, route={[l + 1 for l in r]} (tie -> stays on line 1)")
    try:
        solve([[1, 2], [3]], [[1], [1]], [0, 0], [0, 0])
    except ValueError as exc:
        print(f"  unequal line lengths rejected: {exc}")
    try:
        solve([[1, -2], [3, 4]], [[1], [1]], [0, 0], [0, 0])
    except ValueError as exc:
        print(f"  negative time rejected: {exc}")
