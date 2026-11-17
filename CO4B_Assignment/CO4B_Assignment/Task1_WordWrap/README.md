# Task 1 – Word Wrap as a Document-Layout Engine (8 marks)

**File:** `Source_Code/word_wrap.py` · **Output:** `Output/output.txt`

Dynamic programming over the suffixes of the text: `dp[i]` = minimum penalty for laying out `words[i:]`, `dp[n] = 0`, non-final line penalty = (unused spaces)², final line free.

- 1.1 prints minimum penalty, words per line, unused spaces and penalty per line.
- 1.2 prints every DP state (all candidate lines, cost and total) from right to left.
- 1.3 runs W = 16, 24, 30 against the base W = 20.
- 1.4 boundary tests: word length = W, single word, one-line text, empty text, word longer than W (raises `ValueError`), and a greedy-trap text.

Run: `cd Source_Code && python3 word_wrap.py`
