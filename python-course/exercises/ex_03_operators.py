"""
EXERCISE 03 · Numbers & operators

    ▶ run        : python3 exercises/ex_03_operators.py
    ▶ solution   : python3 exercises/ex_03_operators.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def is_even(number):
    """True when the number is divisible by 2."""
    raise NotImplementedError


def last_digit(number):
    """The last digit of a positive integer.  last_digit(4729) -> 9"""
    raise NotImplementedError


def digit_sum(number):
    """Sum of the digits, without converting to a string.

    digit_sum(4729) -> 22      (hint: % 10 gives the last digit, // 10 drops it)
    """
    raise NotImplementedError


def is_divisible(number, divisor):
    """True when number is evenly divisible by divisor.
    Careful: what should happen when divisor is 0? Return False.
    """
    raise NotImplementedError


def divmod_pair(a, b):
    """Return (a // b, a % b) as a tuple."""
    raise NotImplementedError


def power_mod(base, exponent, modulus):
    """Return base**exponent % modulus efficiently (one built-in call does it)."""
    raise NotImplementedError


def minutes_and_seconds(total_seconds):
    """Return the tuple (minutes, seconds).  minutes_and_seconds(125) -> (2, 5)"""
    raise NotImplementedError


CASES = [
    ("4 is even",            "is_even(4)",                       True),
    ("7 is not even",        "is_even(7)",                       False),
    ("0 is even",            "is_even(0)",                       True),
    ("last digit of 4729",   "last_digit(4729)",                 9),
    ("last digit of 10",     "last_digit(10)",                   0),
    ("digit sum",            "digit_sum(4729)",                  22),
    ("digit sum of 5",       "digit_sum(5)",                     5),
    ("divisible by 3",       "is_divisible(12, 3)",              True),
    ("not divisible",        "is_divisible(12, 5)",              False),
    ("divide by zero",       "is_divisible(12, 0)",              False),
    ("divmod 17, 5",         "divmod_pair(17, 5)",               (3, 2)),
    ("negative divmod",      "divmod_pair(-7, 2)",               (-4, 1)),
    ("power mod",            "power_mod(3, 4, 5)",               1),
    ("big power mod",        "power_mod(2, 100, 1000)",          376),
    ("minutes and seconds",  "minutes_and_seconds(125)",         (2, 5)),
]

SOLUTION = '''
def is_even(number):
    return number % 2 == 0


def last_digit(number):
    return number % 10


def digit_sum(number):
    total = 0
    while number > 0:
        total += number % 10
        number //= 10
    return total


def is_divisible(number, divisor):
    if divisor == 0:
        return False
    return number % divisor == 0


def divmod_pair(a, b):
    return a // b, a % b


def power_mod(base, exponent, modulus):
    return pow(base, exponent, modulus)


def minutes_and_seconds(total_seconds):
    return total_seconds // 60, total_seconds % 60
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 03 · numbers & operators", CASES, namespace)
    summary()
