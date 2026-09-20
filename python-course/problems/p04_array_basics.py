"""
PROBLEM p04 · Array basics: min, max, second largest     [Easy · arrays, one pass]

1. `min_max(nums)` -> (minimum, maximum). Empty list -> (None, None).
2. `second_largest(nums)` -> the second largest DISTINCT value, or None.
        second_largest([4, 9, 2, 9, 7]) -> 7
        second_largest([5, 5, 5])       -> None
   Do it in ONE pass without sorting (keep two running values).
3. `average(nums)` -> the mean rounded to 2 decimals; empty -> 0.0
4. `is_sorted(nums)` -> True when the list is non-decreasing. Empty and
   single-element lists are sorted.

    ▶ run        : python3 problems/p04_array_basics.py
    ▶ solution   : python3 problems/p04_array_basics.py --solution
    ▶ topic      : dsa/dsa_01_arrays.py
    ▶ complexity : O(n) time, O(1) space for each
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def min_max(nums):
    """Return (min, max) or (None, None) for an empty list."""
    raise NotImplementedError


def second_largest(nums):
    """Second largest distinct value, or None. One pass, no sorting."""
    raise NotImplementedError


def average(nums):
    """Mean rounded to 2 decimals; 0.0 for an empty list."""
    raise NotImplementedError


def is_sorted(nums):
    """True when every element is >= the one before it."""
    raise NotImplementedError


CASES = [
    ("min max",              "min_max([4, 1, 9])",              (1, 9)),
    ("min max single",       "min_max([7])",                    (7, 7)),
    ("min max empty",        "min_max([])",                     (None, None)),
    ("min max negatives",    "min_max([-3, -1, -9])",           (-9, -1)),
    ("second largest",       "second_largest([4, 9, 2, 9, 7])", 7),
    ("second largest dupes", "second_largest([5, 5, 5])",       None),
    ("second largest short", "second_largest([1])",             None),
    ("second largest 2",     "second_largest([1, 2])",          1),
    ("average",              "average([1, 2, 3, 4])",           2.5),
    ("average rounding",     "average([1, 2])",                 1.5),
    ("average empty",        "average([])",                     0.0),
    ("is sorted true",       "is_sorted([1, 2, 2, 3])",         True),
    ("is sorted false",      "is_sorted([1, 3, 2])",            False),
    ("is sorted empty",      "is_sorted([])",                   True),
]

SOLUTION = '''
def min_max(nums):
    if not nums:
        return None, None
    smallest = largest = nums[0]
    for value in nums[1:]:
        if value < smallest:
            smallest = value
        if value > largest:
            largest = value
    return smallest, largest


def second_largest(nums):
    largest = second = None
    for value in nums:
        if largest is None or value > largest:
            largest, second = value, largest
        elif value != largest and (second is None or value > second):
            second = value
    return second


def average(nums):
    if not nums:
        return 0.0
    return round(sum(nums) / len(nums), 2)


def is_sorted(nums):
    for index in range(1, len(nums)):
        if nums[index] < nums[index - 1]:
            return False
    return True
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p04 · array basics", CASES, globals())
    summary()
