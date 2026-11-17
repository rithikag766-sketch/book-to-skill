"""Task 2 - Greedy vs Dynamic Programming (Knapsack).

Solution A : Fractional Knapsack, greedy by value/weight ratio   -> optimal for the FRACTIONAL problem
Solution B : 0/1 Knapsack, dynamic programming                    -> optimal for the 0/1 problem
Extra      : 0/1 greedy (same ratio rule, whole items only)       -> used to expose the failure
Every routine returns the chosen items AND counters for work / memory.
"""
import random
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    item_id: str
    weight: int
    value: int

    @property
    def ratio(self):
        return self.value / self.weight


def validate(items, capacity):
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    for it in items:
        if it.weight <= 0 or it.value < 0:
            raise ValueError(f"invalid item {it}")


# ----------------------------------------------------------------- Solution A
def fractional_greedy(items, capacity, trace=False):
    validate(items, capacity)
    stats = {"comparisons": 0, "steps": 0}

    def key(it):
        stats["comparisons"] += 1          # counts key evaluations as a proxy for sort work
        return -it.ratio

    order = sorted(items, key=key)
    remaining, total, chosen = capacity, 0.0, []
    for it in order:
        stats["steps"] += 1
        if remaining == 0:
            break
        take = min(1.0, remaining / it.weight)
        gained = take * it.value
        total += gained
        remaining -= take * it.weight
        chosen.append((it.item_id, take, gained))
        if trace:
            kind = "whole" if take == 1.0 else f"FRACTION {take:.3f}"
            print(f"    take {it.item_id} (w={it.weight}, v={it.value}, ratio={it.ratio:.2f}) "
                  f"-> {kind}, gain={gained:.2f}, capacity left={remaining:.2f}")
    return total, chosen, stats


# ------------------------------------------------------- 0/1 greedy (baseline)
def greedy_01(items, capacity, trace=False):
    validate(items, capacity)
    order = sorted(items, key=lambda it: -it.ratio)
    remaining, total, chosen = capacity, 0, []
    for it in order:
        if it.weight <= remaining:
            remaining -= it.weight
            total += it.value
            chosen.append(it.item_id)
            if trace:
                print(f"    commit {it.item_id} (w={it.weight}, v={it.value}, ratio={it.ratio:.2f}) "
                      f"-> capacity left={remaining}")
        elif trace:
            print(f"    skip   {it.item_id} (w={it.weight}) does not fit in {remaining}")
    return total, chosen


# ----------------------------------------------------------------- Solution B
def knapsack_dp(items, capacity):
    """Classic 2-D table so the chosen set can be reconstructed."""
    validate(items, capacity)
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    cell_updates = 0
    for i in range(1, n + 1):
        w, v = items[i - 1].weight, items[i - 1].value
        for c in range(capacity + 1):
            cell_updates += 1
            table[i][c] = table[i - 1][c]
            if w <= c and table[i - 1][c - w] + v > table[i][c]:
                table[i][c] = table[i - 1][c - w] + v
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if table[i][c] != table[i - 1][c]:
            chosen.append(items[i - 1].item_id)
            c -= items[i - 1].weight
    chosen.reverse()
    return table[n][capacity], chosen, {"cell_updates": cell_updates, "table_cells": (n + 1) * (capacity + 1)}


def show_items(items):
    print(f"    {'ID':<4}{'Weight':>7}{'Value':>7}{'Value/Weight':>14}")
    for it in items:
        print(f"    {it.item_id:<4}{it.weight:>7}{it.value:>7}{it.ratio:>14.2f}")


def run_case(title, items, capacity):
    print(f"--- {title} (capacity = {capacity}) ---")
    show_items(items)
    print("  Greedy decision sequence (fractional):")
    gval, gch, gst = fractional_greedy(items, capacity, trace=True)
    print(f"  Fractional greedy value = {gval:.2f}   items = {[(i, round(f, 3)) for i, f, _ in gch]}")
    print("  Greedy (whole items only) decision sequence:")
    g01, g01ch = greedy_01(items, capacity, trace=True)
    dval, dch, dst = knapsack_dp(items, capacity)
    print(f"  0/1 greedy value = {g01}   items = {g01ch}")
    print(f"  0/1 DP optimum   = {dval}   items = {dch}   (cell updates={dst['cell_updates']})")
    print(f"  GreedyResult == DPOptimum ? {g01 == dval}")
    print()
    return gval, g01, dval


def instrumented_comparison(n, capacity, seed):
    rnd = random.Random(seed)
    items = [Item(f"I{k}", rnd.randint(1, 60), rnd.randint(1, 200)) for k in range(n)]
    t0 = time.perf_counter(); gval, _, gst = fractional_greedy(items, capacity); tg = time.perf_counter() - t0
    g01, _ = greedy_01(items, capacity)
    t0 = time.perf_counter(); dval, _, dst = knapsack_dp(items, capacity); td = time.perf_counter() - t0
    return gval, g01, dval, gst, dst, tg, td


if __name__ == "__main__":
    print("########## 2.1 Normal case: ratio-greedy is optimal ##########")
    normal = [Item("A", 10, 60), Item("B", 20, 100), Item("C", 30, 120), Item("D", 5, 20), Item("E", 15, 45)]
    run_case("Normal case 1 (capacity fits whole items exactly: 10+20+15+5=50)", normal, 50)
    run_case("Normal case 2 (fraction needed: fractional optimum is an upper bound)", normal, 62)

    print("########## 2.2 Break the greedy intuition ##########")
    bad = [Item("P", 10, 60), Item("Q", 20, 100), Item("R", 30, 120)]
    g, g01, d = run_case("Student-designed counterexample", bad, 50)
    print(f"  FIRST greedy commitment: P (ratio 6.00). After taking P only 40 units remain;")
    print(f"  Q fits (20 left) but R(30) then no longer fits, so greedy ends with {g01} < DP {d} (R+Q).")
    print()

    print("########## 2.3 Engineering comparison (instrumented) ##########")
    print(f"  {'n':>6}{'W':>8} | {'greedy ops(key evals)':>22}{'DP cell updates':>17}{'DP table cells':>16} | "
          f"{'frac':>9}{'0/1 greedy':>11}{'DP opt':>8}")
    for n, cap in [(10, 100), (100, 1000), (500, 5000), (1000, 10000)]:
        gval, g01, dval, gst, dst, tg, td = instrumented_comparison(n, cap, seed=n)
        print(f"  {n:>6}{cap:>8} | {gst['comparisons']:>22}{dst['cell_updates']:>17}{dst['table_cells']:>16} | "
              f"{gval:>9.1f}{g01:>11}{dval:>8}")
        print(f"          time: greedy={tg*1000:.3f} ms, DP={td*1000:.1f} ms")

    print()
    print("  Solution quality over 2000 random 0/1 instances (n=20, W=100):")
    gaps, misses = [], 0
    for s in range(2000):
        rnd = random.Random(10_000 + s)
        its = [Item(f"I{k}", rnd.randint(1, 60), rnd.randint(1, 200)) for k in range(20)]
        g01, _ = greedy_01(its, 100)
        dv, _, _ = knapsack_dp(its, 100)
        if g01 < dv:
            misses += 1
        gaps.append((dv - g01) / dv if dv else 0)
    print(f"    greedy was strictly worse than the DP optimum in {misses}/2000 instances")
    print(f"    mean gap = {100*sum(gaps)/len(gaps):.2f}%   worst gap = {100*max(gaps):.2f}%")
    print("  Fractional-greedy value is always >= 0/1 optimum (upper bound); checked on same set:")
    viol = 0
    for s in range(2000):
        rnd = random.Random(10_000 + s)
        its = [Item(f"I{k}", rnd.randint(1, 60), rnd.randint(1, 200)) for k in range(20)]
        fv, _, _ = fractional_greedy(its, 100)
        dv, _, _ = knapsack_dp(its, 100)
        if fv + 1e-9 < dv:
            viol += 1
    print(f"    violations of  fractional >= DP optimum : {viol}")

    print()
    print("########## 2.4 Changed requirement: 'very fast, near-optimal acceptable' ##########")
    for n, cap in [(1000, 10000), (2000, 50000)]:
        rnd = random.Random(n)
        its = [Item(f"I{k}", rnd.randint(1, 60), rnd.randint(1, 200)) for k in range(n)]
        t0 = time.perf_counter(); g01, _ = greedy_01(its, cap); tg = time.perf_counter() - t0
        t0 = time.perf_counter(); dv, _, st = knapsack_dp(its, cap); td = time.perf_counter() - t0
        print(f"  n={n}, W={cap}: greedy={g01} in {tg*1000:.2f} ms | DP={dv} in {td*1000:.0f} ms "
              f"({st['cell_updates']:,} cell updates) | greedy quality = {100*g01/dv:.2f}% of optimum "
              f"| DP is {td/tg:,.0f}x slower")
