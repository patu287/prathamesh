"""
PROBLEM p10 · Binary search                            [Medium · searching]

The input is SORTED. Every step throws away half of what is left, so the cost
is O(log n) instead of O(n). Write the loops by hand here — in real code you
would use `bisect`.

1. `binary_search(nums, target)` -> the index of the target, or -1.
        binary_search([1, 3, 5, 7], 5) -> 2

2. `lower_bound(nums, target)` -> the first index whose value is >= target
   (may be len(nums)).
        lower_bound([1, 2, 2, 3], 2) -> 1     # first 2
        lower_bound([1, 2, 2, 3], 9) -> 4     # past the end

3. `count_occurrences(nums, target)` -> how many times it appears, in O(log n):
   `lower_bound(target + 1) - lower_bound(target)` works for integers.
        count_occurrences([1, 2, 2, 2, 3], 2) -> 3

4. `search_insert(nums, target)` -> the index where the target is, or where it
   would be inserted to keep the list sorted.
        search_insert([1, 3, 5], 4) -> 2

    ▶ run        : python3 problems/p10_binary_search.py
    ▶ solution   : python3 problems/p10_binary_search.py --solution
    ▶ topic      : dsa/dsa_05_binary_search.py
    ▶ complexity : O(log n) time, O(1) space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def binary_search(nums, target):
    raise NotImplementedError


def lower_bound(nums, target):
    raise NotImplementedError


def count_occurrences(nums, target):
    raise NotImplementedError


def search_insert(nums, target):
    raise NotImplementedError


CASES = [
    ("find in the middle",  "binary_search([1, 3, 5, 7, 9], 5)",    2),
    ("find the first",      "binary_search([1, 3, 5], 1)",          0),
    ("find the last",       "binary_search([1, 3, 5], 5)",          2),
    ("missing target",      "binary_search([1, 3, 5], 4)",          -1),
    ("empty list",          "binary_search([], 1)",                 -1),
    ("even-length list",    "binary_search([1, 2, 3, 4], 3)",       2),
    ("lower bound dupes",   "lower_bound([1, 2, 2, 3], 2)",         1),
    ("lower bound past end", "lower_bound([1, 2, 2, 3], 9)",        4),
    ("lower bound empty",   "lower_bound([], 1)",                   0),
    ("count occurrences",   "count_occurrences([1, 2, 2, 2, 3], 2)", 3),
    ("count none",          "count_occurrences([1, 2, 3], 9)",       0),
    ("search insert here",  "search_insert([1, 3, 5], 4)",           2),
    ("search insert first", "search_insert([2, 4], 1)",              0),
    ("search insert last",  "search_insert([2, 4], 9)",              2),
]

SOLUTION = '''
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        middle = (left + right) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def lower_bound(nums, target):
    left, right = 0, len(nums)
    while left < right:
        middle = (left + right) // 2
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def count_occurrences(nums, target):
    return lower_bound(nums, target + 1) - lower_bound(nums, target)


def search_insert(nums, target):
    return lower_bound(nums, target)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p10 · binary search", CASES, globals())
    summary()
