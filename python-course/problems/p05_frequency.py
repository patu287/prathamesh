"""
PROBLEM p05 · Frequency counting                     [Easy · dict / Counter]

1. `frequency(items)` -> {item: count} for any list.
        frequency("banana")        -> {"b": 1, "a": 3, "n": 2}
        frequency([1, 1, 2])       -> {1: 2, 2: 1}
2. `most_common(items)` -> the value with the highest count.
   Ties go to whichever value appears FIRST in the input.
        most_common([1, 1, 2, 2])  -> 1
3. `unique_in_order(items)` -> the distinct values, in order of first appearance.
        unique_in_order([3, 1, 3, 2]) -> [3, 1, 2]
4. `top_k(items, k)` -> the k most frequent values, ordered by count
   descending and then ALPHABETICALLY (so the result is deterministic).
        top_k(["b", "b", "a"], 2)  -> ["b", "a"]

    ▶ run        : python3 problems/p05_frequency.py
    ▶ solution   : python3 problems/p05_frequency.py --solution
    ▶ topic      : dsa/dsa_03_hashmaps.py, lessons/lesson_09_dicts.py
    ▶ complexity : O(n) (top_k: O(n + m log m) where m = distinct values)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def frequency(items):
    raise NotImplementedError


def most_common(items):
    """Ties -> the value seen first. Empty input -> None."""
    raise NotImplementedError


def unique_in_order(items):
    raise NotImplementedError


def top_k(items, k):
    """k most frequent, ties broken alphabetically. k larger than the number of
    distinct values returns everything."""
    raise NotImplementedError


CASES = [
    ("frequency of a string", "frequency('banana')",            {"b": 1, "a": 3, "n": 2}),
    ("frequency of a list",   "frequency([1, 1, 2])",           {1: 2, 2: 1}),
    ("frequency empty",       "frequency([])",                  {}),
    ("most common",           "most_common([3, 1, 3, 2])",      3),
    ("most common tie",       "most_common([1, 1, 2, 2])",      1),
    ("most common empty",     "most_common([])",                None),
    ("unique in order",       "unique_in_order([3, 1, 3, 2])",  [3, 1, 2]),
    ("unique empty",          "unique_in_order([])",            []),
    ("top k",                 "top_k(['b', 'b', 'c', 'a', 'a'], 2)", ["a", "b"]),
    ("top k tie alphabet",    "top_k(['b', 'b', 'a'], 2)",      ["b", "a"]),
    ("top k too big",         "top_k([1, 2], 5)",               [1, 2]),
]

SOLUTION = '''
from collections import Counter, defaultdict


def frequency(items):
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1
    return dict(counts)


def most_common(items):
    if not items:
        return None
    counts = Counter(items)
    best = max(counts.values())
    for item in items:
        if counts[item] == best:
            return item
    return None


def unique_in_order(items):
    return list(dict.fromkeys(items))


def top_k(items, k):
    counts = Counter(items)
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], str(pair[0])))
    return [item for item, _ in ordered[:k]]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p05 · frequency counting", CASES, globals())
    summary()
