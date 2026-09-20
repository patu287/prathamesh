"""
PROBLEM p03 · Two Sum                               [Easy · hash map, arrays]

Given a list of numbers and a target, find the two indices whose values add up
to the target. Return (i, j) with i < j, or None when there is no such pair.

    two_sum([2, 7, 11, 15], 9) -> (0, 1)      # 2 + 7
    two_sum([1, 2, 3], 100)    -> None

Do it in ONE pass with a dictionary (`seen = {value: index}`): for each number
you need `target - number` to already be in the dictionary. That is O(n).

Then write `count_pairs(nums, target)` — how many index pairs sum to the
target? Duplicates matter (indices, not values), so [3, 3] has one pair.

    ▶ run        : python3 problems/p03_two_sum.py
    ▶ solution   : python3 problems/p03_two_sum.py --solution
    ▶ topic      : dsa/dsa_03_hashmaps.py
    ▶ complexity : O(n) time, O(n) space  (the brute force is O(n^2))
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def two_sum(nums, target):
    """Return (i, j) with i < j, or None."""
    raise NotImplementedError


def count_pairs(nums, target):
    """Count index pairs (i < j) whose values sum to the target."""
    raise NotImplementedError


CASES = [
    ("classic two sum",     "two_sum([2, 7, 11, 15], 9)",      (0, 1)),
    ("later pair",          "two_sum([1, 3, 4, 6], 10)",       (2, 3)),
    ("duplicate values",    "two_sum([3, 3], 6)",              (0, 1)),
    ("no pair",             "two_sum([1, 2], 100)",            None),
    ("negative numbers",    "two_sum([-3, 4, 3, 90], 0)",      (0, 2)),
    ("empty list",          "two_sum([], 5)",                  None),
    ("count pairs",         "count_pairs([1, 1, 2, 3, 4], 5)", 3),
    ("count no pairs",      "count_pairs([1, 2, 3], 100)",     0),
    ("count with repeats",  "count_pairs([5, 5, 5, 5], 10)",   6),
]

SOLUTION = '''
def two_sum(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return (seen[complement], index)
        seen[value] = index
    return None


def count_pairs(nums, target):
    seen = {}
    total = 0
    for index, value in enumerate(nums):
        total += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return total
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p03 · two sum", CASES, globals())
    summary()
