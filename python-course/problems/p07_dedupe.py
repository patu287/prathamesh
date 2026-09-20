"""
PROBLEM p07 · Duplicates & dedupe                     [Easy-Medium · sets]

1. `remove_duplicates(items)` -> the values without repetition, keeping the
   order of first appearance. One pass, using a set for "have I seen this?".
        remove_duplicates([3, 1, 3, 2, 1]) -> [3, 1, 2]

2. `find_duplicates(items)` -> the values that appear more than once, in order
   of first appearance.
        find_duplicates([1, 2, 1, 3, 2]) -> [1, 2]

3. `single_number(nums)` -> every value appears twice except one; find it.
   The clean answer uses XOR (^) or a set — that is why it is a classic.
        single_number([4, 1, 2, 1, 2]) -> 4

4. `missing_number(nums, n)` -> the numbers 1..n are all present except one.
        missing_number([1, 2, 4, 5], 5) -> 3

    ▶ run        : python3 problems/p07_dedupe.py
    ▶ solution   : python3 problems/p07_dedupe.py --solution
    ▶ topic      : dsa/dsa_03_hashmaps.py, lessons/lesson_08_tuples_sets.py
    ▶ complexity : O(n) time, O(n) space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def remove_duplicates(items):
    raise NotImplementedError


def find_duplicates(items):
    raise NotImplementedError


def single_number(nums):
    """All values appear exactly twice except one (which appears once)."""
    raise NotImplementedError


def missing_number(nums, n):
    """nums holds n-1 of the numbers 1..n. Return the missing one."""
    raise NotImplementedError


CASES = [
    ("remove duplicates",     "remove_duplicates([3, 1, 3, 2, 1])", [3, 1, 2]),
    ("remove none",           "remove_duplicates([1, 2, 3])",      [1, 2, 3]),
    ("remove from empty",     "remove_duplicates([])",             []),
    ("find duplicates",       "find_duplicates([1, 2, 1, 3, 2])",  [1, 2]),
    ("find duplicates none",  "find_duplicates([1, 2, 3])",        []),
    ("single number",         "single_number([4, 1, 2, 1, 2])",    4),
    ("single number negative", "single_number([-1, -1, 7])",       7),
    ("missing number",        "missing_number([1, 2, 4, 5], 5)",   3),
    ("missing number 1",      "missing_number([2, 3, 4], 4)",      1),
    ("missing number last",   "missing_number([1, 2, 3], 4)",      4),
]

SOLUTION = '''
def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def find_duplicates(items):
    seen = set()
    duplicates = []
    for item in items:
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)
    return duplicates


def single_number(nums):
    result = 0
    for value in nums:
        result ^= value          # XOR: a ^ a == 0, so pairs cancel out
    return result


def missing_number(nums, n):
    return n * (n + 1) // 2 - sum(nums)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p07 · duplicates & dedupe", CASES, globals())
    summary()
