"""Task 5 - Kruskal, Prim and Boruvka on the same weighted undirected graph.

Every algorithm prints the order in which edges are accepted and why.
Edge = (u, v, w).  Each edge also gets a stable index used as a tie-break.
"""
import heapq
import random
from fractions import Fraction

VERTICES = ["A", "B", "C", "D", "E", "F", "G", "H"]

# Original graph (all weights distinct -> the MST is unique). Four tight pairs joined by heavier links,
# so Boruvka needs two rounds.
EDGES = [
    ("A", "B", 1), ("C", "D", 2), ("E", "F", 3), ("G", "H", 4),
    ("B", "C", 6), ("D", "E", 7), ("F", "G", 8), ("A", "C", 9),
    ("B", "D", 10), ("C", "E", 11), ("E", "G", 12), ("D", "F", 13),
    ("A", "H", 14),
]

# Modified graph: several link weights made equal so more than one MST exists
TIE_EDGES = [
    ("A", "B", 1), ("C", "D", 2), ("E", "F", 3), ("G", "H", 4),
    ("B", "C", 6), ("A", "C", 6), ("D", "E", 7), ("C", "E", 7),
    ("F", "G", 8), ("E", "G", 8), ("B", "D", 10), ("D", "F", 13),
    ("A", "H", 14),
]


class DisjointSet:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
        self.find_calls = 0

    def find(self, x):
        self.find_calls += 1
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def is_connected(vertices, edges):
    ds = DisjointSet(vertices)
    for u, v, _ in edges:
        ds.union(u, v)
    return len({ds.find(v) for v in vertices}) == 1


def kruskal(vertices, edges, tie_break="index", verbose=True):
    if not is_connected(vertices, edges):
        raise ValueError("graph is disconnected: no spanning tree exists")
    indexed = list(enumerate(edges))
    if tie_break == "reverse":
        indexed.sort(key=lambda p: (p[1][2], -p[0]))
    else:
        indexed.sort(key=lambda p: (p[1][2], p[0]))
    ds = DisjointSet(vertices)
    mst, total = [], 0
    if verbose:
        print("  Kruskal - maintains: a sorted edge list and a disjoint-set (component labels)")
    for _, (u, v, w) in indexed:
        if ds.union(u, v):
            mst.append((u, v, w)); total += w
            if verbose:
                print(f"    accept {u}-{v} ({w}): joins two different components -> tree has {len(mst)} edges")
        elif verbose:
            print(f"    reject {u}-{v} ({w}): both ends already in one component (would form a cycle)")
        if len(mst) == len(vertices) - 1:
            break
    return mst, total, {"find_calls": ds.find_calls, "sorted_edges": len(edges)}


def prim(vertices, edges, start="A", verbose=True):
    if not is_connected(vertices, edges):
        raise ValueError("graph is disconnected: no spanning tree exists")
    adj = {v: [] for v in vertices}
    for i, (u, v, w) in enumerate(edges):
        adj[u].append((w, i, v, u))
        adj[v].append((w, i, u, v))
    in_tree = {start}
    heap = list(adj[start])
    heapq.heapify(heap)
    pushes, pops = len(heap), 0
    mst, total = [], 0
    if verbose:
        print(f"  Prim from {start} - maintains: set of tree vertices and a heap of edges leaving the tree")
    while heap and len(mst) < len(vertices) - 1:
        w, i, v, u = heapq.heappop(heap)
        pops += 1
        if v in in_tree:
            continue
        in_tree.add(v)
        mst.append((u, v, w)); total += w
        if verbose:
            print(f"    accept {u}-{v} ({w}): cheapest edge leaving tree {sorted(in_tree - {v})} -> adds {v}")
        for item in adj[v]:
            if item[2] not in in_tree:
                heapq.heappush(heap, item); pushes += 1
    return mst, total, {"heap_pushes": pushes, "heap_pops": pops}


def boruvka(vertices, edges, consistent_ties=True, verbose=True):
    if not is_connected(vertices, edges):
        raise ValueError("graph is disconnected: no spanning tree exists")
    ds = DisjointSet(vertices)
    mst, total, rounds, scans = [], 0, 0, 0
    if verbose:
        print("  Boruvka - maintains: component label of every vertex; each round every component picks its cheapest outgoing edge")
    comps = len(vertices)
    while comps > 1:
        rounds += 1
        cheapest = {}
        for i, (u, v, w) in enumerate(edges):
            scans += 1
            cu, cv = ds.find(u), ds.find(v)
            if cu == cv:
                continue
            key = (w, i) if consistent_ties else (w,)
            for c in (cu, cv):
                if c not in cheapest or key < cheapest[c][0]:
                    cheapest[c] = (key, (u, v, w))
        added = []
        for c, (_, (u, v, w)) in sorted(cheapest.items()):
            if ds.union(u, v):
                mst.append((u, v, w)); total += w; comps -= 1
                added.append(f"{u}-{v}({w})")
        if verbose:
            print(f"    round {rounds}: components picked {added}; {comps} component(s) remain")
        if not added:
            break
    return mst, total, {"rounds": rounds, "edge_scans": scans}


def is_spanning_tree(vertices, tree):
    return len(tree) == len(vertices) - 1 and is_connected(vertices, tree)


def edge_set(tree):
    return frozenset(frozenset((u, v)) for u, v, _ in tree)


def count_msts(vertices, edges):
    """Matrix-tree theorem restricted to the subgraph of edges that can appear in some MST is
    complex; here we brute force by Kirchhoff on all-spanning-trees only for tie reasoning
    via enumeration of edge subsets (graph is small)."""
    from itertools import combinations
    n = len(vertices)
    best, found = None, []
    for subset in combinations(edges, n - 1):
        if is_spanning_tree(vertices, list(subset)):
            w = sum(e[2] for e in subset)
            if best is None or w < best:
                best, found = w, [subset]
            elif w == best:
                found.append(subset)
    return best, found


def random_graph(n, m, seed):
    rnd = random.Random(seed)
    vs = [str(i) for i in range(n)]
    es = {}
    for i in range(1, n):
        j = rnd.randrange(i)
        es[(vs[j], vs[i])] = rnd.randint(1, 10_000)
    while len(es) < m:
        a, b = rnd.sample(range(n), 2)
        key = (vs[min(a, b)], vs[max(a, b)])
        if key not in es:
            es[key] = rnd.randint(1, 10_000)
    return vs, [(u, v, w) for (u, v), w in es.items()]


if __name__ == "__main__":
    print("########## Original graph (distinct weights) ##########")
    print("Edges:", ", ".join(f"{u}-{v}({w})" for u, v, w in EDGES))
    results = {}
    for name, fn in (("Kruskal", kruskal), ("Prim", prim), ("Boruvka", boruvka)):
        print()
        tree, total, stats = fn(VERTICES, EDGES)
        results[name] = (tree, total)
        print(f"  {name}: MST edges = {[f'{u}-{v}({w})' for u, v, w in tree]}")
        print(f"  {name}: total cost = {total}; spanning tree valid = {is_spanning_tree(VERTICES, tree)}; work = {stats}")
    sets = {n: edge_set(t) for n, (t, _) in results.items()}
    print("\n  All three return the same edge set:", len(set(sets.values())) == 1)

    print("\n########## Stress the design: modified graph with tied weights ##########")
    print("Edges:", ", ".join(f"{u}-{v}({w})" for u, v, w in TIE_EDGES))
    runs = {}
    for label, fn, kw in (("Kruskal (ties by input order)", kruskal, {"tie_break": "index"}),
                          ("Kruskal (ties in reverse order)", kruskal, {"tie_break": "reverse"}),
                          ("Prim from A", prim, {"start": "A"}),
                          ("Prim from H", prim, {"start": "H"}),
                          ("Boruvka", boruvka, {})):
        print()
        print(f" [{label}]")
        tree, total, stats = fn(VERTICES, TIE_EDGES, **kw)
        runs[label] = (tree, total)
        print(f"  -> total cost = {total}, edges = {sorted(f'{min(u,v)}-{max(u,v)}({w})' for u, v, w in tree)}")
    print("\n  Summary of the tied graph")
    totals = {t for _, t in runs.values()}
    sets = {edge_set(t) for t, _ in runs.values()}
    print(f"  distinct total costs: {sorted(totals)}  |  distinct edge sets returned: {len(sets)}")
    best, all_msts = count_msts(VERTICES, TIE_EDGES)
    print(f"  exhaustive check: minimum spanning-tree cost = {best}, number of distinct MSTs = {len(all_msts)}")
    print("  Every returned tree is one of the exhaustive MSTs:",
          all(edge_set(t) in {edge_set(m) for m in all_msts} for t, _ in runs.values()))

    print("\n########## Boruvka tie-break defect (why ties need a consistent rule) ##########")
    tri_v = ["X", "Y", "Z"]
    tri_e = [("X", "Y", 1), ("Y", "Z", 1), ("X", "Z", 1)]
    print("  Triangle, all weights 1. Reasoning (hand-worked, not program output): if X picks X-Y, Y picks Y-Z and")
    print("  Z picks Z-X in the same round, all three edges are accepted and form a cycle.")
    print("  What this implementation does:")
    t1, c1, _ = boruvka(tri_v, tri_e, consistent_ties=False, verbose=False)
    t2, c2, _ = boruvka(tri_v, tri_e, consistent_ties=True, verbose=False)
    print(f"   without tie-break rule (relies on the union-find cycle guard): {[f'{u}-{v}' for u, v, _ in t1]}, cost {c1}")
    print(f"   with (weight, edge-index) tie-break rule                     : {[f'{u}-{v}' for u, v, _ in t2]}, cost {c2}")
    print("  The union-find guard is what stops the cycle; the consistent tie-break is what makes the choice")
    print("  deterministic and is required for the correctness proof when edges are accepted in parallel.")

    print("\n########## Instrumented comparison for deployment analysis ##########")
    print(f"  {'graph':<22}{'n':>6}{'m':>8}  {'Kruskal sort+find':>20}{'Prim pushes/pops':>20}{'Boruvka rounds/scans':>24}")
    for label, n, m in (("A sparse", 2000, 4000), ("B dense", 300, 30000), ("C large sparse", 20000, 60000)):
        vs, es = random_graph(n, m, seed=n)
        _, tk, sk = kruskal(vs, es, verbose=False)
        _, tp, sp = prim(vs, es, start=vs[0], verbose=False)
        _, tb, sb = boruvka(vs, es, verbose=False)
        assert tk == tp == tb
        print(f"  {label:<22}{n:>6}{m:>8}  {sk['sorted_edges']:>9} / {sk['find_calls']:>8}"
              f"{sp['heap_pushes']:>11} / {sp['heap_pops']:>6}{sb['rounds']:>12} / {sb['edge_scans']:>9}   cost={tk}")
    print("\n  Disconnected-graph failure test:")
    try:
        kruskal(["A", "B", "C"], [("A", "B", 1)], verbose=False)
    except ValueError as e:
        print("   rejected ->", e)
