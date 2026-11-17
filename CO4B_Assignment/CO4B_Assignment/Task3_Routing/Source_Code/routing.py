"""Task 3 - Routing engine: Dijkstra, Bellman-Ford, Floyd, Warshall.

Network: 8 logistics hubs (A..H), 13 directed edges.
Stage A  : Dijkstra on the non-negative network
Stage B  : add a negative edge, PREDICT first, then compare Dijkstra and Bellman-Ford
Stage C  : add a reachable negative cycle, detect it (do not return misleading paths)
Stage D  : all-pairs costs (Floyd) and reachability (Warshall)
"""
import heapq

INF = float("inf")
VERTICES = ["A", "B", "C", "D", "E", "F", "G", "H"]

# Stage A graph : directed, all weights >= 0 (13 edges)
BASE_EDGES = [
    ("A", "B", 4), ("A", "C", 2), ("B", "D", 5), ("C", "B", 1),
    ("C", "D", 8), ("C", "E", 10), ("D", "F", 2), ("E", "D", 2),
    ("E", "G", 3), ("F", "G", 6), ("F", "H", 4), ("G", "H", 1),
    ("D", "E", 3),
]


# ------------------------------------------------------------------ helpers
def build_adj(vertices, edges):
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def path_to(pred, source, target):
    if target != source and pred.get(target) is None:
        return None
    path = [target]
    guard = 0
    while path[-1] != source:
        path.append(pred[path[-1]])
        guard += 1
        if guard > 1000:           # protects against predecessor cycles
            return None
    return path[::-1]


def show_result(title, vertices, dist, pred, source):
    print(f"  {title}")
    print(f"  {'Vertex':<7}{'Distance':>9}  {'Pred':<5} Path")
    for v in vertices:
        d = dist[v]
        p = path_to(pred, source, v)
        print(f"  {v:<7}{('inf' if d == INF else d):>9}  {str(pred[v]):<5} "
              f"{' -> '.join(p) if p else 'unreachable'}")


# ------------------------------------------------------------------ Dijkstra
def dijkstra(vertices, edges, source):
    adj = build_adj(vertices, edges)
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[source] = 0
    done, order = set(), []
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)                # u is FINALISED: this assumes no negative edge can lower it later
        order.append((u, d))
        for v, w in adj[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w
                pred[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, pred, order


# -------------------------------------------------------------- Bellman-Ford
def bellman_ford(vertices, edges, source):
    """Return (dist, pred, negative_cycle_vertices_or_None, passes_used)."""
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[source] = 0
    passes = 0
    for _ in range(len(vertices) - 1):
        changed = False
        passes += 1
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed = True
        if not changed:
            break
    # |V|-th pass: any further relaxation proves a reachable negative cycle
    bad = None
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            bad = (u, v, w)
            break
    if bad is None:
        return dist, pred, None, passes
    # walk back |V| steps to land inside the cycle, then collect it
    x = bad[1]
    pred[x] = bad[0]
    for _ in range(len(vertices)):
        x = pred[x]
    cycle, y = [x], pred[x]
    while y != x:
        cycle.append(y)
        y = pred[y]
    cycle.append(x)
    return dist, pred, cycle[::-1], passes + 1


# --------------------------------------------------------- Floyd and Warshall
def floyd(vertices, edges):
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        d[idx[u]][idx[v]] = min(d[idx[u]][idx[v]], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    neg_cycle = any(d[i][i] < 0 for i in range(n))
    return d, neg_cycle


def warshall(vertices, edges):
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    r = [[False] * n for _ in range(n)]
    for i in range(n):
        r[i][i] = True
    for u, v, _ in edges:
        r[idx[u]][idx[v]] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                r[i][j] = r[i][j] or (r[i][k] and r[k][j])
    return r


def print_matrix(title, vertices, m, fmt):
    print(f"  {title}")
    print("      " + "".join(f"{v:>6}" for v in vertices))
    for i, v in enumerate(vertices):
        print(f"  {v:<4}" + "".join(f"{fmt(m[i][j]):>6}" for j in range(len(vertices))))


def fmt_dist(x):
    return "inf" if x == INF else str(x)


def fmt_bool(x):
    return "1" if x else "0"


def cycle_weight(edges, cycle):
    """Weight of a closed walk, using the cheapest parallel edge for each hop."""
    best = {}
    for u, v, w in edges:
        best[(u, v)] = min(w, best.get((u, v), INF))
    return sum(best[(a, b)] for a, b in zip(cycle, cycle[1:]))


if __name__ == "__main__":
    print(f"Network: {len(VERTICES)} vertices, {len(BASE_EDGES)} directed edges")
    print("Edges:", ", ".join(f"{u}->{v}({w})" for u, v, w in BASE_EDGES))
    print()

    # ---------------------------------------------------------------- Stage A
    print("########## STAGE A - Dijkstra, source A ##########")
    dist, pred, order = dijkstra(VERTICES, BASE_EDGES, "A")
    show_result("Shortest distances, predecessors and paths", VERTICES, dist, pred, "A")
    print("  Order in which vertices are finalised:", " , ".join(f"{u}({d})" for u, d in order))
    print()

    # ---------------------------------------------------------------- Stage B
    print("########## STAGE B - negative edge G->F (-5) ##########")
    print("  PREDICTION (recorded BEFORE running the modified graph):")
    print("   1. Dijkstra will NOT remain valid. F is finalised at distance 10 (via D) before G is")
    print("      finalised at 13. The new edge G->F(-5) offers F a cost of 13-5 = 8, but Dijkstra never")
    print("      revisits a finalised vertex, so it will keep F = 10.")
    print("   2. The decisions affected are the routes to F and to H (H is reached through F):")
    print("      expected true cost of H = 8 + 4 = 12 instead of Dijkstra's 14, and the route to H")
    print("      should change from A-C-B-D-F-H to a route that passes through G and returns to F.")
    print("   3. The edge was chosen so that F->G->F has weight 6-5 = +1 > 0, so no negative cycle")
    print("      exists and Bellman-Ford should converge normally.")
    NEG_EDGES = BASE_EDGES + [("G", "F", -5)]
    d1, p1, order1 = dijkstra(VERTICES, NEG_EDGES, "A")
    d2, p2, cyc, passes = bellman_ford(VERTICES, NEG_EDGES, "A")
    print()
    show_result("Dijkstra on the modified graph (UNRELIABLE)", VERTICES, d1, p1, "A")
    print("  Dijkstra finalisation order:", " , ".join(f"{u}({d})" for u, d in order1))
    print()
    print("  Bellman-Ford negative cycle reported:", cyc)
    show_result(f"Bellman-Ford on the modified graph ({passes} passes)", VERTICES, d2, p2, "A")
    print()
    print("  Vertices where Dijkstra and Bellman-Ford disagree:")
    for v in VERTICES:
        if d1[v] != d2[v]:
            print(f"    {v}: Dijkstra={d1[v]} via {' -> '.join(path_to(p1, 'A', v))}   "
                  f"Bellman-Ford={d2[v]} via {' -> '.join(path_to(p2, 'A', v))}")
    print()

    # ---------------------------------------------------------------- Stage C
    print("########## STAGE C - reachable negative cycle ##########")
    CYCLE_EDGES = BASE_EDGES + [("D", "E", -5)]   # E->D(2) + D->E(-5) = -3
    print("  Added edge D->E(-5). Cycle D -> E -> D has weight -5 + 2 = -3 and is reachable from A.")
    dist_c, pred_c, cyc_c, passes_c = bellman_ford(VERTICES, CYCLE_EDGES, "A")
    if cyc_c:
        print(f"  NEGATIVE CYCLE DETECTED on pass {passes_c}: {' -> '.join(cyc_c)}  "
              f"(cycle weight = {cycle_weight(CYCLE_EDGES, cyc_c)})")
        print("  No shortest-path table is returned: distances are undefined for every vertex reachable")
        print("  from the cycle (D, E, F, G, H).")
    else:
        print("  no negative cycle")
    d_cd, _ = floyd(VERTICES, CYCLE_EDGES)
    print("  Floyd cross-check, vertices with a negative diagonal entry:",
          [VERTICES[i] for i in range(len(VERTICES)) if d_cd[i][i] < 0])
    print()
    print("  Detection mechanism: with |V| = 8 any shortest SIMPLE path has at most 7 edges, so 7 passes of")
    print("  relaxing every edge are enough. If an edge can still be relaxed on pass 8, some path has more")
    print("  than 7 edges and is still getting cheaper, which is only possible through a negative cycle.")
    print("  The cycle itself is recovered by walking predecessor links back |V| steps.")
    print()

    # ---------------------------------------------------------------- Stage D
    print("########## STAGE D - all pairs (Floyd) and reachability (Warshall), base graph ##########")
    fl, _ = floyd(VERTICES, BASE_EDGES)
    wa = warshall(VERTICES, BASE_EDGES)
    print_matrix("Floyd distance matrix", VERTICES, fl, fmt_dist)
    print()
    print_matrix("Warshall reachability matrix (1 = reachable)", VERTICES, wa, fmt_bool)
    print()
    fln, nc = floyd(VERTICES, NEG_EDGES)
    print_matrix("Floyd distance matrix on the G->F(-5) graph", VERTICES, fln, fmt_dist)
    print("  Floyd row A equals Bellman-Ford distances:",
          all(fln[0][i] == d2[VERTICES[i]] for i in range(len(VERTICES))))
    print("  negative cycle present:", nc)
