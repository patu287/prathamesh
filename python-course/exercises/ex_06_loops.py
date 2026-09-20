"""
EXERCISE 06 · Loops

    ▶ run        : python3 exercises/ex_06_loops.py
    ▶ solution   : python3 exercises/ex_06_loops.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def sum_to_n(n):
    """1 + 2 + ... + n using a loop. sum_to_n(5) -> 15.  n <= 0 -> 0."""
    raise NotImplementedError


def factorial(n):
    """n! using a loop. factorial(5) -> 120.  factorial(0) -> 1."""
    raise NotImplementedError


def count_divisible(limit, divisor):
    """How many numbers from 1 to limit (inclusive) are divisible by divisor?"""
    raise NotImplementedError


def fizzbuzz_list(n):
    """List of n fizzbuzz strings for 1..n. fizzbuzz_list(5) -> ['1','2','Fizz','4','Buzz']"""
    raise NotImplementedError


def multiplication_table(n):
    """List of the strings "1 x 7 = 7" ... "10 x 7 = 70" for the given number."""
    raise NotImplementedError


def reverse_number(number):
    """Reverse the digits of a positive integer using % and //.
    reverse_number(4729) -> 9274
    """
    raise NotImplementedError


def first_multiple_of(divisor, lower_bound):
    """The smallest multiple of `divisor` that is >= lower_bound.
    first_multiple_of(7, 20) -> 21
    (hint: -(-lower_bound // divisor) * divisor, or a while loop)
    """
    raise NotImplementedError


def pyramid(rows):
    """Return the pyramid as a list of strings using "* " per row.
    pyramid(3) -> ['* ', '* * ', '* * * ']
    """
    raise NotImplementedError


CASES = [
    ("sum to 5",            "sum_to_n(5)",                        15),
    ("sum to 0",            "sum_to_n(0)",                        0),
    ("sum to negative",     "sum_to_n(-3)",                       0),
    ("sum to 100",          "sum_to_n(100)",                      5050),
    ("factorial 5",         "factorial(5)",                       120),
    ("factorial 0",         "factorial(0)",                       1),
    ("factorial 10",        "factorial(10)",                      3628800),
    ("count divisible",     "count_divisible(100, 7)",            14),
    ("count divisible by 1", "count_divisible(10, 1)",            10),
    ("fizzbuzz list",       "fizzbuzz_list(5)",                   ["1", "2", "Fizz", "4", "Buzz"]),
    ("fizzbuzz 15",         "fizzbuzz_list(15)[-1]",              "FizzBuzz"),
    ("table length",        "len(multiplication_table(7))",       10),
    ("table row 3",         "multiplication_table(7)[2]",         "3 x 7 = 21"),
    ("reverse number",      "reverse_number(4729)",               9274),
    ("reverse 120",         "reverse_number(120)",                21),
    ("first multiple",      "first_multiple_of(7, 20)",           21),
    ("first multiple exact", "first_multiple_of(5, 20)",          20),
    ("pyramid",             "pyramid(3)",                         ["* ", "* * ", "* * * "]),
]

SOLUTION = '''
def sum_to_n(n):
    total = 0
    for number in range(1, n + 1):
        total += number
    return total


def factorial(n):
    result = 1
    for number in range(2, n + 1):
        result *= number
    return result


def count_divisible(limit, divisor):
    count = 0
    for number in range(1, limit + 1):
        if number % divisor == 0:
            count += 1
    return count


def fizzbuzz_list(n):
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


def multiplication_table(n):
    return [f"{i} x {n} = {i * n}" for i in range(1, 11)]


def reverse_number(number):
    reversed_number = 0
    while number > 0:
        reversed_number = reversed_number * 10 + number % 10
        number //= 10
    return reversed_number


def first_multiple_of(divisor, lower_bound):
    return -(-lower_bound // divisor) * divisor


def pyramid(rows):
    return ["* " * row for row in range(1, rows + 1)]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 06 · loops", CASES, namespace)
    summary()
