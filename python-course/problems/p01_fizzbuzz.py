"""
PROBLEM p01 · FizzBuzz                                  [Easy · loops, conditions]

Print the numbers 1..n, but:
  * multiples of 15 -> "FizzBuzz"
  * multiples of 3  -> "Fizz"
  * multiples of 5  -> "Buzz"
  * everything else -> the number as a string

    fizzbuzz(5)  -> ["1", "2", "Fizz", "4", "Buzz"]
    fizzbuzz(15)[-1] -> "FizzBuzz"

Watch out: check 15 BEFORE 3 and 5, otherwise you never reach FizzBuzz.

Also implement `sum_fizzbuzz(n)`: the sum of all numbers from 1..n that are
divisible by 3 or 5.
    sum_fizzbuzz(10) -> 3+5+6+9+10 = 33

    ▶ run        : python3 problems/p01_fizzbuzz.py
    ▶ solution   : python3 problems/p01_fizzbuzz.py --solution
    ▶ topic      : lessons/lesson_06_loops.py, lessons/lesson_05_conditions.py
    ▶ complexity : O(n) time, O(n) space for the list
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def fizzbuzz(n):
    """Return the list of strings for 1..n.  n <= 0 -> []."""
    raise NotImplementedError


def sum_fizzbuzz(n):
    """Return the sum of every number in 1..n divisible by 3 or 5."""
    raise NotImplementedError


CASES = [
    ("fizzbuzz 5",       "fizzbuzz(5)",       ["1", "2", "Fizz", "4", "Buzz"]),
    ("fizzbuzz 3",       "fizzbuzz(3)",       ["1", "2", "Fizz"]),
    ("fizzbuzz 15 last", "fizzbuzz(15)[-1]",  "FizzBuzz"),
    ("fizzbuzz list len", "len(fizzbuzz(20))", 20),
    ("fizzbuzz 0",       "fizzbuzz(0)",       []),
    ("fizzbuzz negative", "fizzbuzz(-5)",     []),
    ("sum to 10",        "sum_fizzbuzz(10)",  33),
    ("sum to 100",       "sum_fizzbuzz(100)", 2418),
]

SOLUTION = '''
def fizzbuzz(n):
    result = []
    for number in range(1, n + 1):
        if number % 15 == 0:
            result.append("FizzBuzz")
        elif number % 3 == 0:
            result.append("Fizz")
        elif number % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(number))
    return result


def sum_fizzbuzz(n):
    return sum(number for number in range(1, n + 1)
               if number % 3 == 0 or number % 5 == 0)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p01 · fizzbuzz", CASES, globals())
    summary()
