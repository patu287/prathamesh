"""
EXERCISE 05 · Making decisions (if / elif / else)

    ▶ run        : python3 exercises/ex_05_conditions.py
    ▶ solution   : python3 exercises/ex_05_conditions.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def grade(score):
    """90+ -> "A", 75+ -> "B", 60+ -> "C", 40+ -> "D", below -> "F".
    Anything outside 0..100 -> "invalid".
    """
    raise NotImplementedError


def leap_year(year):
    """True when the year is a leap year: divisible by 4, except centuries,
    except every 400 years.  2000 -> True, 1900 -> False, 2024 -> True
    """
    raise NotImplementedError


def triangle_type(a, b, c):
    """"equilateral", "isosceles", "scalene" or "not a triangle"
    (sides must be positive and the sum of any two must exceed the third).
    """
    raise NotImplementedError


def fizzbuzz_value(number):
    """"FizzBuzz" if divisible by 15, "Fizz" by 3, "Buzz" by 5, else str(number).
    Check 15 FIRST, or you will get the classic bug.
    """
    raise NotImplementedError


def max_of_three(a, b, c):
    """The largest of the three, using if/else (not the max() built-in)."""
    raise NotImplementedError


def sign(number):
    """1 for positive, -1 for negative, 0 for zero."""
    raise NotImplementedError


CASES = [
    ("grade A",            "grade(95)",              "A"),
    ("grade B",            "grade(80)",              "B"),
    ("grade boundary 75",  "grade(75)",              "B"),
    ("grade C",            "grade(61)",              "C"),
    ("grade D",            "grade(40)",              "D"),
    ("grade F",            "grade(39)",              "F"),
    ("grade invalid",      "grade(101)",             "invalid"),
    ("grade invalid neg",  "grade(-1)",              "invalid"),
    ("2024 leap",          "leap_year(2024)",        True),
    ("1900 not leap",      "leap_year(1900)",        False),
    ("2000 leap",          "leap_year(2000)",        True),
    ("2023 not leap",      "leap_year(2023)",        False),
    ("equilateral",        "triangle_type(3, 3, 3)", "equilateral"),
    ("isosceles",          "triangle_type(3, 3, 5)", "isosceles"),
    ("scalene",            "triangle_type(3, 4, 5)", "scalene"),
    ("not a triangle",     "triangle_type(1, 2, 10)", "not a triangle"),
    ("not a triangle zero", "triangle_type(0, 2, 2)", "not a triangle"),
    ("fizzbuzz 15",        "fizzbuzz_value(15)",     "FizzBuzz"),
    ("fizzbuzz 3",         "fizzbuzz_value(3)",      "Fizz"),
    ("fizzbuzz 5",         "fizzbuzz_value(5)",      "Buzz"),
    ("fizzbuzz 7",         "fizzbuzz_value(7)",      "7"),
    ("max of three",       "max_of_three(4, 9, 2)",  9),
    ("max with negatives", "max_of_three(-5, -1, -9)", -1),
    ("sign positive",      "sign(3)",                1),
    ("sign negative",      "sign(-3)",               -1),
    ("sign zero",          "sign(0)",                0),
]

SOLUTION = '''
def grade(score):
    if not 0 <= score <= 100:
        return "invalid"
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def triangle_type(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return "not a triangle"
    if a + b <= c or a + c <= b or b + c <= a:
        return "not a triangle"
    if a == b == c:
        return "equilateral"
    if a == b or b == c or a == c:
        return "isosceles"
    return "scalene"


def fizzbuzz_value(number):
    if number % 15 == 0:
        return "FizzBuzz"
    if number % 3 == 0:
        return "Fizz"
    if number % 5 == 0:
        return "Buzz"
    return str(number)


def max_of_three(a, b, c):
    biggest = a
    if b > biggest:
        biggest = b
    if c > biggest:
        biggest = c
    return biggest


def sign(number):
    if number > 0:
        return 1
    if number < 0:
        return -1
    return 0
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 05 · conditions", CASES, namespace)
    summary()
