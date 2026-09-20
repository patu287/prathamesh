"""
EXERCISE 08 · Tuples & sets

    ▶ run        : python3 exercises/ex_08_tuples_sets.py
    ▶ solution   : python3 exercises/ex_08_tuples_sets.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def unique_sorted(nums):
    """The distinct values, sorted ascending.
    unique_sorted([3, 1, 3, 2]) -> [1, 2, 3]
    """
    raise NotImplementedError


def are_anagrams(a, b):
    """True when both strings use exactly the same letters (ignore case).
    are_anagrams("Listen", "Silent") -> True
    """
    raise NotImplementedError


def common_elements(a, b):
    """Sorted list of values present in BOTH lists, without duplicates."""
    raise NotImplementedError


def min_max_pair(nums):
    """Return (min, max) as a tuple.  min_max_pair([4, 1, 9]) -> (1, 9)"""
    raise NotImplementedError


def missing_number(nums, n):
    """nums contains 1..n with exactly one number missing. Return it.
    missing_number([1, 2, 4, 5], 5) -> 3
    """
    raise NotImplementedError


def has_duplicates(nums):
    """True when any value appears more than once (use a set)."""
    raise NotImplementedError


def unique_names(pairs):
    """pairs is a list of (name, age) tuples. Return the sorted unique names."""
    raise NotImplementedError


CASES = [
    ("unique sorted",        "unique_sorted([3, 1, 3, 2])",        [1, 2, 3]),
    ("unique empty",         "unique_sorted([])",                  []),
    ("are anagrams",         "are_anagrams('Listen', 'Silent')",   True),
    ("not anagrams",         "are_anagrams('hello', 'world')",     False),
    ("anagrams different lengths", "are_anagrams('abc', 'ab')",    False),
    ("common elements",      "common_elements([1, 2, 3], [2, 3, 4])", [2, 3]),
    ("common empty",         "common_elements([1], [2])",          []),
    ("min max pair",         "min_max_pair([4, 1, 9])",            (1, 9)),
    ("missing number",       "missing_number([1, 2, 4, 5], 5)",    3),
    ("missing number 1",     "missing_number([2, 3, 4], 4)",       1),
    ("has duplicates",       "has_duplicates([1, 2, 2])",          True),
    ("no duplicates",        "has_duplicates([1, 2, 3])",          False),
    ("unique names",         "unique_names([('ravi', 20), ('asha', 21), ('ravi', 22)])", ["asha", "ravi"]),
]

SOLUTION = '''
def unique_sorted(nums):
    return sorted(set(nums))


def are_anagrams(a, b):
    return sorted(a.lower()) == sorted(b.lower())


def common_elements(a, b):
    return sorted(set(a) & set(b))


def min_max_pair(nums):
    return min(nums), max(nums)


def missing_number(nums, n):
    return (set(range(1, n + 1)) - set(nums)).pop()


def has_duplicates(nums):
    return len(set(nums)) != len(nums)


def unique_names(pairs):
    return sorted({name for name, _ in pairs})
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 08 · tuples & sets", CASES, namespace)
    summary()
