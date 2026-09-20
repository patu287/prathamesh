"""
PROBLEM p14 · Recursion fundamentals                   [Medium · recursion]

Every recursive function needs a base case and a smaller sub-problem. Write
these recursively (that is the point of the exercise), then ask yourself which
ones you would rewrite as a loop in real code.

1. `factorial(n)` -> n! with factorial(0) = 1.
        factorial(5) -> 120

2. `sum_digits(n)` -> the sum of the digits, recursively.
        sum_digits(9876) -> 30
   (hint: n % 10 + sum_digits(n // 10), and n == 0 is the base case)

3. `power(base, exponent)` -> base**exponent recursively. For a bonus, make it
   O(log n) with fast exponentiation: base^n = (base^(n/2))^2 when n is even.
        power(2, 10) -> 1024

4. `gcd(a, b)` -> Euclid's algorithm, recursively.
        gcd(48, 18) -> 6
   (hint: gcd(a, b) = gcd(b, a % b), and gcd(a, 0) = a)

5. `reverse_list_recursive(items)` -> the list backwards, using recursion
   rather than slicing tricks.

    ▶ run        : python3 problems/p14_recursion.py
    ▶ solution   : python3 problems/p14_recursion.py --solution
    ▶ topic      : dsa/dsa_06_recursion.py
    ▶ complexity : factorial/sum_digits O(n), power O(log n), gcd O(log n)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def factorial(n):
    """n <= 0 -> 1."""
    raise NotImplementedError


def sum_digits(n):
    """Sum of the decimal digits. Negative numbers: use the absolute value."""
    raise NotImplementedError


def power(base, exponent):
    """base ** exponent for exponent >= 0, recursively."""
    raise NotImplementedError


def gcd(a, b):
    """Greatest common divisor, Euclid's way."""
    raise NotImplementedError


def reverse_list_recursive(items):
    """Return the reversed list using recursion."""
    raise NotImplementedError


CASES = [
    ("factorial 5",         "factorial(5)",                     120),
    ("factorial 0",         "factorial(0)",                     1),
    ("factorial 10",        "factorial(10)",                    3628800),
    ("sum digits",          "sum_digits(9876)",                 30),
    ("sum digits single",   "sum_digits(5)",                    5),
    ("sum digits zero",     "sum_digits(0)",                    0),
    ("sum digits negative", "sum_digits(-123)",                 6),
    ("power 2^10",          "power(2, 10)",                     1024),
    ("power 5^0",           "power(5, 0)",                      1),
    ("power 3^4",           "power(3, 4)",                      81),
    ("gcd 48, 18",          "gcd(48, 18)",                      6),
    ("gcd coprime",         "gcd(17, 5)",                       1),
    ("gcd with zero",       "gcd(9, 0)",                        9),
    ("reverse recursive",   "reverse_list_recursive([1, 2, 3])", [3, 2, 1]),
    ("reverse empty",       "reverse_list_recursive([])",       []),
]

SOLUTION = '''
def factorial(n):
    if n <= 0:
        return 1
    return n * factorial(n - 1)


def sum_digits(n):
    n = abs(n)
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)


def power(base, exponent):
    if exponent == 0:
        return 1
    if exponent % 2 == 0:
        half = power(base, exponent // 2)
        return half * half
    return base * power(base, exponent - 1)


def gcd(a, b):
    if b == 0:
        return abs(a)
    return gcd(b, a % b)


def reverse_list_recursive(items):
    if len(items) <= 1:
        return list(items)
    return reverse_list_recursive(items[1:]) + [items[0]]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p14 · recursion fundamentals", CASES, globals())
    summary()
