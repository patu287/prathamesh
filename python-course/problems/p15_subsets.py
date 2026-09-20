"""
PROBLEM p15 · Subsets (the power set)                [Medium-Hard · backtracking]

Every list of n distinct values has exactly 2^n subsets (including the empty
set). Generating them is the classic introduction to backtracking: at each
element you have two choices — take it or leave it.

1. `subsets(nums)` -> every subset as a list of lists, in any order.
        len(subsets([1, 2, 3])) -> 8
   Tests sort the result for you, so order does not matter.

2. `subsets_with_sum(nums, target)` -> the subsets whose values add up to the
   target (each element used at most once).
        subsets_with_sum([1, 2, 3], 3) -> [[1, 2], [3]]   (in any order)

3. `count_subsets(nums)` -> how many subsets there are, computed as 2^n
   (do not generate them).

4. `subset_sums(nums)` -> the sorted list of every subset's total.
        subset_sums([1, 2]) -> [0, 1, 2, 3]

    ▶ run        : python3 problems/p15_subsets.py
    ▶ solution   : python3 problems/p15_subsets.py --solution
    ▶ topic      : dsa/dsa_06_recursion.py
    ▶ complexity : O(2^n * n) time to build them all
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def subsets(nums):
    """All 2^n subsets as a list of lists (any order)."""
    raise NotImplementedError


def subsets_with_sum(nums, target):
    """Subsets summing to the target (any order; each element used once)."""
    raise NotImplementedError


def count_subsets(nums):
    """2 ** len(nums) — computed, not generated."""
    raise NotImplementedError


def subset_sums(nums):
    """Sorted list of the sums of every subset.  [1, 2] -> [0, 1, 2, 3]"""
    raise NotImplementedError


CASES = [
    ("subsets of [1, 2]",      "sorted(map(tuple, subsets([1, 2])))",
     [(), (1,), (1, 2), (2,)]),
    ("subsets of [1, 2, 3]",   "sorted(map(tuple, subsets([1, 2, 3])))",
     [(), (1,), (1, 2), (1, 2, 3), (1, 3), (2,), (2, 3), (3,)]),
    ("subsets count",          "len(subsets([1, 2, 3, 4]))",           16),
    ("subsets of empty",       "sorted(map(tuple, subsets([])))",      [()]),
    ("subsets with sum",       "sorted(map(tuple, subsets_with_sum([1, 2, 3], 3)))",
     [(1, 2), (3,)]),
    ("subsets with no sum",    "subsets_with_sum([2, 4], 7)",          []),
    ("count subsets",          "count_subsets(list(range(10)))",       1024),
    ("count subsets empty",    "count_subsets([])",                    1),
    ("subset sums",            "subset_sums([1, 2])",                  [0, 1, 2, 3]),
    ("subset sums equal",      "subset_sums([2, 2])",                  [0, 2, 2, 4]),
]

SOLUTION = '''
def subsets(nums):
    result = []

    def explore(index, path):
        if index == len(nums):
            result.append(path[:])
            return
        explore(index + 1, path)              # skip nums[index]
        path.append(nums[index])              # take nums[index]
        explore(index + 1, path)
        path.pop()

    explore(0, [])
    return result


def subsets_with_sum(nums, target):
    result = []

    def explore(index, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        if index == len(nums) or remaining < 0:
            return
        explore(index + 1, path, remaining)                # skip
        path.append(nums[index])
        explore(index + 1, path, remaining - nums[index])  # take
        path.pop()

    explore(0, [], target)
    return result


def count_subsets(nums):
    return 2 ** len(nums)


def subset_sums(nums):
    totals = [0]
    for value in nums:
        totals += [total + value for total in totals]
    return sorted(totals)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p15 · subsets", CASES, globals())
    summary()
