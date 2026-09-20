"""
PROBLEM p11 · Merging sorted lists                     [Medium · two pointers]

This is the merge step of merge sort, and the core of "combine two sorted
things" questions. Use two indices, and never `sorted(a + b)` — that would be
O((n+m) log(n+m)) instead of O(n+m).

1. `merge_two_sorted(a, b)` -> one sorted list containing both.
        merge_two_sorted([1, 3, 5], [2, 4]) -> [1, 2, 3, 4, 5]

2. `merge_k_sorted(lists)` -> merge any number of sorted lists.
        merge_k_sorted([[1, 4], [2, 5], [3]]) -> [1, 2, 3, 4, 5]

3. `median_of_two_sorted(a, b)` -> the median of the combined data
   (no need to be clever here: merge and take the middle).
        median_of_two_sorted([1, 3], [2])     -> 2
        median_of_two_sorted([1, 2], [3, 4])  -> 2.5

4. `kth_smallest_merged(a, b, k)` -> the k-th smallest value (1-indexed) of the
   combined data.
        kth_smallest_merged([1, 3, 5], [2, 4], 3) -> 3

    ▶ run        : python3 problems/p11_merge_sorted.py
    ▶ solution   : python3 problems/p11_merge_sorted.py --solution
    ▶ topic      : dsa/dsa_04_sorting.py, dsa/dsa_05_binary_search.py
    ▶ complexity : O(n + m) for merging, O(n + m) for the median
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def merge_two_sorted(a, b):
    raise NotImplementedError


def merge_k_sorted(lists):
    raise NotImplementedError


def median_of_two_sorted(a, b):
    raise NotImplementedError


def kth_smallest_merged(a, b, k):
    """k is 1-indexed. Return None when k is out of range."""
    raise NotImplementedError


CASES = [
    ("merge two",            "merge_two_sorted([1, 3, 5], [2, 4])",   [1, 2, 3, 4, 5]),
    ("merge with empty",     "merge_two_sorted([], [1, 2])",          [1, 2]),
    ("merge both empty",     "merge_two_sorted([], [])",              []),
    ("merge with dupes",     "merge_two_sorted([1, 1], [1, 2])",      [1, 1, 1, 2]),
    ("merge k sorted",       "merge_k_sorted([[1, 4], [2, 5], [3]])", [1, 2, 3, 4, 5]),
    ("merge k with empty",   "merge_k_sorted([[], [1], [0, 2]])",     [0, 1, 2]),
    ("median odd",           "median_of_two_sorted([1, 3], [2])",     2),
    ("median even",          "median_of_two_sorted([1, 2], [3, 4])",  2.5),
    ("median with empties",  "median_of_two_sorted([], [5])",         5),
    ("kth smallest",         "kth_smallest_merged([1, 3, 5], [2, 4], 3)", 3),
    ("kth smallest first",   "kth_smallest_merged([1, 3], [2], 1)",   1),
    ("kth out of range",     "kth_smallest_merged([1], [2], 5)",      None),
]

SOLUTION = '''
import heapq


def merge_two_sorted(a, b):
    i = j = 0
    merged = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    merged.extend(a[i:])
    merged.extend(b[j:])
    return merged


def merge_k_sorted(lists):
    return list(heapq.merge(*lists))


def median_of_two_sorted(a, b):
    merged = merge_two_sorted(a, b)
    if not merged:
        return None
    middle = len(merged) // 2
    if len(merged) % 2:
        return merged[middle]
    return (merged[middle - 1] + merged[middle]) / 2


def kth_smallest_merged(a, b, k):
    merged = merge_two_sorted(a, b)
    if k < 1 or k > len(merged):
        return None
    return merged[k - 1]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p11 · merging sorted lists", CASES, globals())
    summary()
