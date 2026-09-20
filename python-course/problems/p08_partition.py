"""
PROBLEM p08 · Partitioning an array                  [Medium · two pointers]

1. `move_zeroes(nums)` -> a NEW list with every 0 moved to the end, keeping the
   order of the non-zero values.
        move_zeroes([0, 1, 0, 3, 12]) -> [1, 3, 12, 0, 0]

2. `partition_evens_odds(nums)` -> evens first, then odds, each group keeping
   its original order (this is a "stable partition").
        partition_evens_odds([1, 2, 3, 4]) -> [2, 4, 1, 3]

3. `sort_colors(nums)` -> the list contains only 0, 1 and 2; sort it in ONE
   pass with O(1) extra space (the Dutch national flag problem).
   You may sort in place and also return the list.
        sort_colors([2, 0, 2, 1, 1, 0]) -> [0, 0, 1, 1, 2, 2]

4. `rotate_right(nums, k)` -> rotate by k places to the right, returning a new
   list (handle k > len and empty input).
        rotate_right([1, 2, 3, 4, 5], 2) -> [4, 5, 1, 2, 3]

    ▶ run        : python3 problems/p08_partition.py
    ▶ solution   : python3 problems/p08_partition.py --solution
    ▶ topic      : dsa/dsa_01_arrays.py, dsa/dsa_04_sorting.py
    ▶ complexity : O(n) time, O(1) extra space for sort_colors
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def move_zeroes(nums):
    raise NotImplementedError


def partition_evens_odds(nums):
    raise NotImplementedError


def sort_colors(nums):
    """One pass, O(1) extra space (Dutch national flag)."""
    raise NotImplementedError


def rotate_right(nums, k):
    raise NotImplementedError


CASES = [
    ("move zeroes",          "move_zeroes([0, 1, 0, 3, 12])",   [1, 3, 12, 0, 0]),
    ("move zeroes none",     "move_zeroes([1, 2])",             [1, 2]),
    ("move zeroes all zero", "move_zeroes([0, 0])",             [0, 0]),
    ("partition",            "partition_evens_odds([1, 2, 3, 4])", [2, 4, 1, 3]),
    ("partition mixed",      "partition_evens_odds([2, 1, 4, 3, 6])", [2, 4, 6, 1, 3]),
    ("sort colors",          "sort_colors([2, 0, 2, 1, 1, 0])", [0, 0, 1, 1, 2, 2]),
    ("sort colors sorted",   "sort_colors([0, 1, 2])",          [0, 1, 2]),
    ("rotate by 2",          "rotate_right([1, 2, 3, 4, 5], 2)", [4, 5, 1, 2, 3]),
    ("rotate by 0",          "rotate_right([1, 2, 3], 0)",      [1, 2, 3]),
    ("rotate more than len", "rotate_right([1, 2, 3], 7)",      [3, 1, 2]),
    ("rotate empty",         "rotate_right([], 3)",             []),
]

SOLUTION = '''
def move_zeroes(nums):
    kept = [value for value in nums if value != 0]
    return kept + [0] * (len(nums) - len(kept))


def partition_evens_odds(nums):
    evens = [value for value in nums if value % 2 == 0]
    odds = [value for value in nums if value % 2]
    return evens + odds


def sort_colors(nums):
    low = middle = 0
    high = len(nums) - 1
    while middle <= high:
        if nums[middle] == 0:
            nums[low], nums[middle] = nums[middle], nums[low]
            low += 1
            middle += 1
        elif nums[middle] == 1:
            middle += 1
        else:
            nums[middle], nums[high] = nums[high], nums[middle]
            high -= 1
    return nums


def rotate_right(nums, k):
    if not nums:
        return []
    k %= len(nums)
    return nums[-k:] + nums[:-k] if k else nums[:]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p08 · partitioning", CASES, globals())
    summary()
