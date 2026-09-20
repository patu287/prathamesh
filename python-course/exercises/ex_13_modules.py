"""
EXERCISE 13 · Modules & the standard library

    ▶ run        : python3 exercises/ex_13_modules.py
    ▶ solution   : python3 exercises/ex_13_modules.py --solution

For this one you may import whatever you like from the standard library
(math, statistics, random, collections, heapq, bisect, itertools...).
Looking at the docs is not cheating — it is the job.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def distance(x1, y1, x2, y2):
    """Euclidean distance, rounded to 4 decimals (use math.hypot or ** 0.5)."""
    raise NotImplementedError


def digit_count(number):
    """How many digits does the positive integer have? (math.log10 + 1, or len(str))"""
    raise NotImplementedError


def median_of(nums):
    """The median using the statistics module."""
    raise NotImplementedError


def most_common_element(items):
    """The most common element using collections.Counter."""
    raise NotImplementedError


def k_smallest(nums, k):
    """The k smallest values, sorted (heapq.nsmallest)."""
    raise NotImplementedError


def first_index_at_least(sorted_nums, value):
    """The first index whose value is >= `value`, using bisect."""
    raise NotImplementedError


def interleave(a, b):
    """Interleave two lists: [1, 2] and "ab" -> [1, 'a', 2, 'b']
    (hint: itertools.chain.from_iterable(zip(a, b)))"""
    raise NotImplementedError


def running_totals(nums):
    """Running totals using itertools.accumulate -> list(...)"""
    raise NotImplementedError


def seeded_choice(seed, options):
    """Pick one option with random.seed(seed) applied first, so it is repeatable."""
    raise NotImplementedError


CASES = [
    ("distance 3-4-5",        "distance(0, 0, 3, 4)",              5.0),
    ("distance same point",   "distance(2, 2, 2, 2)",              0.0),
    ("digit count",           "digit_count(12345)",                5),
    ("digit count 1",         "digit_count(7)",                    1),
    ("median odd",            "median_of([1, 3, 2])",              2),
    ("median even",           "median_of([1, 2, 3, 4])",           2.5),
    ("most common",           "most_common_element([1, 2, 2, 3])", 2),
    ("k smallest",            "k_smallest([5, 1, 9, 3], 2)",       [1, 3]),
    ("bisect first index",    "first_index_at_least([1, 3, 5, 7], 5)", 2),
    ("bisect past the end",   "first_index_at_least([1, 3, 5], 99)", 3),
    ("interleave",            "interleave([1, 2], ['a', 'b'])",    [1, "a", 2, "b"]),
    ("running totals",        "running_totals([1, 2, 3])",         [1, 3, 6]),
    ("seeded choice is stable", "seeded_choice(42, ['a', 'b', 'c'])", "c"),
]

SOLUTION = '''
import bisect
import math
import random
import statistics
from collections import Counter
from itertools import accumulate, chain
from heapq import nsmallest


def distance(x1, y1, x2, y2):
    return round(math.hypot(x2 - x1, y2 - y1), 4)


def digit_count(number):
    return len(str(number))


def median_of(nums):
    return statistics.median(nums)


def most_common_element(items):
    return Counter(items).most_common(1)[0][0]


def k_smallest(nums, k):
    return nsmallest(k, nums)


def first_index_at_least(sorted_nums, value):
    return bisect.bisect_left(sorted_nums, value)


def interleave(a, b):
    return list(chain.from_iterable(zip(a, b)))


def running_totals(nums):
    return list(accumulate(nums))


def seeded_choice(seed, options):
    random.seed(seed)
    return random.choice(options)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 13 · modules & standard library", CASES, namespace)
    summary()
