"""
EXERCISE 10 · Functions

    ▶ run        : python3 exercises/ex_10_functions.py
    ▶ solution   : python3 exercises/ex_10_functions.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def apply_twice(func, value):
    """Call func twice: apply_twice(square, 3) -> 81 (square(square(3)))."""
    raise NotImplementedError


def square(x):
    """Return x * x (used by apply_twice above)."""
    raise NotImplementedError


def sum_all(*numbers):
    """Sum any number of arguments. sum_all() -> 0"""
    raise NotImplementedError


def biggest(*numbers):
    """The largest argument, or None when nothing was passed."""
    raise NotImplementedError


def stats(numbers):
    """Return the tuple (count, total, minimum, maximum, average).
    For an empty list return (0, 0, None, None, None). Average rounded to 2 dp.
    """
    raise NotImplementedError


def apply_discount(price, percent=10):
    """Return the discounted price, rounded to 2 decimals."""
    raise NotImplementedError


def make_multiplier(factor):
    """Return a function that multiplies its argument by `factor`.
    double = make_multiplier(2); double(5) -> 10
    """
    raise NotImplementedError


def is_prime(n):
    """True when n is a prime number (n < 2 -> False). Try divisors up to sqrt(n)."""
    raise NotImplementedError


CASES = [
    ("square",             "square(4)",                           16),
    ("apply twice",        "apply_twice(square, 3)",              81),
    ("apply twice strings", "apply_twice(str.upper, 'hi')",       "HI"),
    ("sum all",            "sum_all(1, 2, 3)",                    6),
    ("sum all empty",      "sum_all()",                           0),
    ("biggest",            "biggest(4, 9, 2)",                    9),
    ("biggest empty",      "biggest()",                           None),
    ("stats",              "stats([1, 2, 3, 4])",                 (4, 10, 1, 4, 2.5)),
    ("stats empty",        "stats([])",                           (0, 0, None, None, None)),
    ("discount default",   "apply_discount(200)",                 180.0),
    ("discount custom",    "apply_discount(200, 25)",             150.0),
    ("make multiplier",    "make_multiplier(2)(5)",               10),
    ("make multiplier 3",  "make_multiplier(3)(5)",               15),
    ("is prime 7",         "is_prime(7)",                         True),
    ("is prime 9",         "is_prime(9)",                         False),
    ("is prime 1",         "is_prime(1)",                         False),
    ("is prime 2",         "is_prime(2)",                         True),
]

SOLUTION = '''
def apply_twice(func, value):
    return func(func(value))


def square(x):
    return x * x


def sum_all(*numbers):
    total = 0
    for number in numbers:
        total += number
    return total


def biggest(*numbers):
    if not numbers:
        return None
    largest = numbers[0]
    for number in numbers[1:]:
        if number > largest:
            largest = number
    return largest


def stats(numbers):
    if not numbers:
        return 0, 0, None, None, None
    return len(numbers), sum(numbers), min(numbers), max(numbers), round(sum(numbers) / len(numbers), 2)


def apply_discount(price, percent=10):
    return round(price * (1 - percent / 100), 2)


def make_multiplier(factor):
    def multiply(value):
        return value * factor
    return multiply


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 10 · functions", CASES, namespace)
    summary()
