"""
PROBLEM p00 · Warm-up                       [Trivial]

Start here to see how the problem files work.

    ▶ run        : python3 problems/p00_warmup.py
    ▶ solution   : python3 problems/p00_warmup.py --solution
    ▶ grade all  : python3 tools/grade.py problems

How it works
------------
Every problem file has the same shape:
  1. a problem statement (this docstring),
  2. some functions with `raise NotImplementedError` — that is your work,
  3. a CASES list of (name, expression, expected value) tests,
  4. a main block that runs the tests and prints your score.

Expressions are evaluated with YOUR functions, so the tests only measure the
behaviour you were asked for — not how you wrote it.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def add(a, b):
    """Return the sum of a and b."""
    raise NotImplementedError


def is_even(n):
    """Return True when n is divisible by 2."""
    raise NotImplementedError


def first_element(items):
    """Return the first item. For an empty list, return None instead of raising."""
    raise NotImplementedError


CASES = [
    ("add two numbers",     "add(2, 3)",           5),
    ("add negatives",       "add(-2, 3)",          1),
    ("is_even true",        "is_even(8)",          True),
    ("is_even false",       "is_even(7)",          False),
    ("first element",       "first_element([9, 8])", 9),
    ("first of empty",      "first_element([])",   None),
]

SOLUTION = '''
def add(a, b):
    return a + b


def is_even(n):
    return n % 2 == 0


def first_element(items):
    return items[0] if items else None
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p00 · warm-up", CASES, globals())
    summary()
