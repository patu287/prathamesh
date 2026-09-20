"""
EXERCISE 07 · Lists

    ▶ run        : python3 exercises/ex_07_lists.py
    ▶ solution   : python3 exercises/ex_07_lists.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def second_largest(nums):
    """The second largest DISTINCT value, or None if there isn't one.
    second_largest([4, 9, 2, 9, 7]) -> 7
    """
    raise NotImplementedError


def remove_duplicates(nums):
    """Remove duplicates while keeping the first occurrence order.
    remove_duplicates([3, 1, 3, 2, 1]) -> [3, 1, 2]
    """
    raise NotImplementedError


def rotate_right(nums, k):
    """Rotate the list to the right by k places (return a NEW list).
    rotate_right([1, 2, 3, 4, 5], 2) -> [4, 5, 1, 2, 3]
    Handle k > len(nums), and negative k (which rotates to the LEFT instead,
    because Python's % always returns a non-negative result:
    -1 % 3 == 2, so rotating by -1 == rotating right by 2).
    """
    raise NotImplementedError


def move_zeroes(nums):
    """Move all zeroes to the end, keeping the order of the other values.
    move_zeroes([0, 1, 0, 3, 12]) -> [1, 3, 12, 0, 0]
    """
    raise NotImplementedError


def running_sum(nums):
    """Running totals: [1,2,3] -> [1,3,6]"""
    raise NotImplementedError


def flatten(matrix):
    """Turn a list of lists into a single list.
    flatten([[1, 2], [3], []]) -> [1, 2, 3]
    """
    raise NotImplementedError


def evens_and_odds(nums):
    """Return the tuple (list of evens, list of odds) preserving order."""
    raise NotImplementedError


CASES = [
    ("second largest",       "second_largest([4, 9, 2, 9, 7])",   7),
    ("second largest dupes", "second_largest([5, 5, 5])",         None),
    ("second largest short", "second_largest([1])",               None),
    ("second largest 2 items", "second_largest([1, 2])",          1),
    ("remove duplicates",    "remove_duplicates([3, 1, 3, 2, 1])", [3, 1, 2]),
    ("remove duplicates none", "remove_duplicates([1, 2, 3])",    [1, 2, 3]),
    ("rotate by 2",          "rotate_right([1, 2, 3, 4, 5], 2)",  [4, 5, 1, 2, 3]),
    ("rotate by 0",          "rotate_right([1, 2, 3], 0)",        [1, 2, 3]),
    ("rotate by more than len", "rotate_right([1, 2, 3], 7)",     [3, 1, 2]),
    ("rotate negative (left)", "rotate_right([1, 2, 3], -1)",      [2, 3, 1]),
    ("move zeroes",          "move_zeroes([0, 1, 0, 3, 12])",     [1, 3, 12, 0, 0]),
    ("move zeroes no zero",  "move_zeroes([1, 2])",               [1, 2]),
    ("running sum",          "running_sum([1, 2, 3])",            [1, 3, 6]),
    ("running sum empty",    "running_sum([])",                   []),
    ("flatten",              "flatten([[1, 2], [3], []])",        [1, 2, 3]),
    ("evens and odds",       "evens_and_odds([1, 2, 3, 4])",      ([2, 4], [1, 3])),
]

SOLUTION = '''
def second_largest(nums):
    distinct = sorted(set(nums), reverse=True)
    return distinct[1] if len(distinct) >= 2 else None


def remove_duplicates(nums):
    seen = set()
    result = []
    for value in nums:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def rotate_right(nums, k):
    if not nums:
        return []
    k %= len(nums)
    return nums[-k:] + nums[:-k] if k else nums[:]


def move_zeroes(nums):
    result = [value for value in nums if value != 0]
    return result + [0] * (len(nums) - len(result))


def running_sum(nums):
    total = 0
    result = []
    for value in nums:
        total += value
        result.append(total)
    return result


def flatten(matrix):
    return [value for row in matrix for value in row]


def evens_and_odds(nums):
    return [value for value in nums if value % 2 == 0], [value for value in nums if value % 2]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 07 · lists", CASES, namespace)
    summary()
