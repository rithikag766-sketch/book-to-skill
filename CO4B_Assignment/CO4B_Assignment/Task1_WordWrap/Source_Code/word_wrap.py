"""Task 1 - Word Wrap as a Document-Layout Engine (Dynamic Programming).

Penalty of a non-final line = (unused spaces)^2 ; the final line costs 0.

Suffix formulation:
    dp[i] = minimum penalty for laying out words[i:]
    dp[n] = 0                                   (nothing left to place)
    dp[i] = min over j > i such that words[i:j] fits on one line of
            cost(i, j) + dp[j]
            cost(i, j) = 0 if j == n else (W - length(i, j))**2
"""

INF = float("inf")


def line_length(words, i, j):
    """Characters needed for words[i:j] separated by single spaces."""
    return sum(len(w) for w in words[i:j]) + (j - i - 1)


def validate(words, width):
    if width <= 0:
        raise ValueError("Line width must be positive")
    for w in words:
        if len(w) > width:
            raise ValueError(f"Word '{w}' (len {len(w)}) is longer than width {width}")


def word_wrap(words, width, trace=False):
    """Return (min_penalty, lines, dp, choice, states).

    lines  = list of (start, end, unused, penalty)
    states = per-index decision records when trace=True
    """
    validate(words, width)
    n = len(words)
    dp = [INF] * (n + 1)
    choice = [-1] * (n + 1)
    dp[n] = 0
    states = []
    for i in range(n - 1, -1, -1):
        options = []
        for j in range(i + 1, n + 1):
            length = line_length(words, i, j)
            if length > width:
                break
            unused = width - length
            cost = 0 if j == n else unused ** 2
            total = cost + dp[j]
            options.append((j, unused, cost, total))
            if total < dp[i]:
                dp[i] = total
                choice[i] = j
        if trace:
            states.append((i, options, dp[i], choice[i]))
    lines = []
    i = 0
    while i < n:
        j = choice[i]
        unused = width - line_length(words, i, j)
        pen = 0 if j == n else unused ** 2
        lines.append((i, j, unused, pen))
        i = j
    return dp[0], lines, dp, choice, states


def greedy_penalty(words, width):
    """Greedy first-fit baseline, used only for comparison."""
    n, i, total = len(words), 0, 0
    while i < n:
        j = i + 1
        while j < n and line_length(words, i, j + 1) <= width:
            j += 1
        if j != n:
            total += (width - line_length(words, i, j)) ** 2
        i = j
    return total


def report(words, width, show_states=False, title=""):
    best, lines, dp, choice, states = word_wrap(words, width, trace=show_states)
    print(f"=== {title} | W = {width} ===")
    print(f"Minimum total penalty = {best}")
    print(f"{'Line':<5}{'Words on line':<48}{'Unused':>7}{'Penalty':>9}")
    for k, (i, j, unused, pen) in enumerate(lines, 1):
        print(f"{k:<5}{' '.join(words[i:j]):<48}{unused:>7}{pen:>9}")
    print(f"Greedy first-fit penalty (comparison only) = {greedy_penalty(words, width)}")
    if show_states:
        print("\nDP states (computed from the END of the text backwards):")
        print("  dp[i]   = minimum penalty for laying out words[i:]")
        print("  next[i] = index of the first word of the line that follows the line starting at i")
        for i, options, d, c in states:
            opt = "; ".join(f"[{i}:{j}) unused={u} cost={cst} -> {cst}+dp[{j}]={tot}"
                            for j, u, cst, tot in options)
            print(f"  i={i:<2} '{words[i]}': dp[{i}]={d}, next={c} | {opt}")
        print(f"  i={len(words)} (empty suffix): dp[{len(words)}]=0")
    print()
    return best, lines


TEXT = ("Dynamic programming breaks a hard problem into smaller overlapping "
        "subproblems and stores their answers so that nothing is computed twice").split()

if __name__ == "__main__":
    print("########## 1.1 + 1.2  Base case with DP states ##########")
    report(TEXT, 20, show_states=True, title="Base case")

    print("########## 1.3  Requirement change: three different widths ##########")
    for w in (16, 24, 30):
        report(TEXT, w, title="Modified case")

    print("########## 1.4  Boundary tests ##########")
    tests = {
        "word length == W": (["abcde", "fg", "hijkl"], 5),
        "single word": (["hello"], 10),
        "everything fits on one line (last line is free)": (["a", "bb", "ccc"], 50),
        "empty text": ([], 10),
    }
    for name, (ws, w) in tests.items():
        best, lines, *_ = word_wrap(ws, w)
        print(f"{name}: W={w}, words={ws} -> penalty={best}, "
              f"lines={[' '.join(ws[i:j]) for i, j, _, _ in lines]}")
    try:
        word_wrap(["extraordinary", "x"], 5)
    except ValueError as e:
        print(f"word longer than W: correctly rejected -> {e}")

    print("\nGreedy-vs-DP trap text, W=6")
    report("aaa bb cc ddddd".split(), 6, title="Greedy trap")
