"""
PROBLEM p09 · Prefix sums & subarrays                [Medium · prefix sums]

A prefix sum lets you answer "what is the sum of a[i:j]?" in O(1) after one
O(n) build. Master this: it turns many O(n^2) solutions into O(n).

1. `build_prefix(nums)` -> a list of length n+1 where prefix[i] is the sum of
   the first i elements. So prefix[0] = 0 and prefix[n] = sum(nums).
        build_prefix([5, 2, 8]) -> [0, 5, 7, 15]

2. `range_sum(prefix, i, j)` -> sum of nums[i:j] (half-open, like slicing).
        range_sum([0, 5, 7, 15], 1, 3) -> 10

3. `count_subarrays_with_sum(nums, target)` -> how many contiguous subarrays
   sum to the target? Use a dict of prefix sums: O(n).
        count_subarrays_with_sum([1, 1, 1], 2) -> 2

4. `max_subarray_sum(nums)` -> the largest sum of any non-empty contiguous
   subarray (Kadane's algorithm, one pass).
        max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) -> 6

    ▶ run        : python3 problems/p09_prefix_sums.py
    ▶ solution   : python3 problems/p09_prefix_sums.py --solution
    ▶ topic      : dsa/dsa_01_arrays.py
    ▶ complexity : O(n) each (the brute force for 3 and 4 is O(n^2))
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def build_prefix(nums):
    raise NotImplementedError


def range_sum(prefix, i, j):
    raise NotImplementedError


def count_subarrays_with_sum(nums, target):
    raise NotImplementedError


def max_subarray_sum(nums):
    """Kadane's algorithm. Assume the list is non-empty."""
    raise NotImplementedError


CASES = [
    ("build prefix",         "build_prefix([5, 2, 8])",                       [0, 5, 7, 15]),
    ("build prefix empty",   "build_prefix([])",                              [0]),
    ("range sum",            "range_sum([0, 5, 7, 15], 1, 3)",                10),
    ("range sum whole",      "range_sum([0, 5, 7, 15], 0, 3)",                15),
    ("range sum empty",      "range_sum([0, 5, 7, 15], 2, 2)",                0),
    ("count subarrays",      "count_subarrays_with_sum([1, 1, 1], 2)",        2),
    ("count subarrays zeros", "count_subarrays_with_sum([0, 0, 0], 0)",       6),
    ("count subarrays none", "count_subarrays_with_sum([1, 2], 100)",         0),
    ("count with negatives", "count_subarrays_with_sum([1, -1, 0], 0)",       3),
    ("max subarray",         "max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4])", 6),
    ("max subarray all negatives", "max_subarray_sum([-5, -2, -9])",          -2),
    ("max subarray single",  "max_subarray_sum([7])",                          7),
]

SOLUTION = '''
def build_prefix(nums):
    prefix = [0] * (len(nums) + 1)
    for index, value in enumerate(nums):
        prefix[index + 1] = prefix[index] + value
    return prefix


def range_sum(prefix, i, j):
    return prefix[j] - prefix[i]


def count_subarrays_with_sum(nums, target):
    counts = {0: 1}
    running = 0
    total = 0
    for value in nums:
        running += value
        total += counts.get(running - target, 0)
        counts[running] = counts.get(running, 0) + 1
    return total


def max_subarray_sum(nums):
    best_ending_here = best = nums[0]
    for value in nums[1:]:
        best_ending_here = max(value, best_ending_here + value)
        best = max(best, best_ending_here)
    return best
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p09 · prefix sums & subarrays", CASES, globals())
    summary()
