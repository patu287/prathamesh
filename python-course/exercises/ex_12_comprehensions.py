"""
EXERCISE 12 · Comprehensions & generators

    ▶ run        : python3 exercises/ex_12_comprehensions.py
    ▶ solution   : python3 exercises/ex_12_comprehensions.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def squares(nums):
    """List of n * n for every n.  squares([1, 2, 3]) -> [1, 4, 9]"""
    raise NotImplementedError


def evens(nums):
    """List of the even values only."""
    raise NotImplementedError


def as_strings(nums):
    """List of the numbers as strings."""
    raise NotImplementedError


def words_longer_than(words, length):
    """List of words strictly longer than `length`."""
    raise NotImplementedError


def length_map(words):
    """Dict mapping each word to its length."""
    raise NotImplementedError


def invert(mapping):
    """Swap keys and values with a comprehension."""
    raise NotImplementedError


def unique_squares(nums):
    """A SET of the squared values.  unique_squares([1, -1]) -> {1}"""
    raise NotImplementedError


def sum_of_squares(nums):
    """Sum of squares using a GENERATOR expression inside sum() (no list!)."""
    raise NotImplementedError


def first_negative(nums):
    """The first negative value, or None. Use a generator with next(..., None)."""
    raise NotImplementedError


def flatten_once(matrix):
    """Flatten one level with a double comprehension."""
    raise NotImplementedError


CASES = [
    ("squares",              "squares([1, 2, 3])",                 [1, 4, 9]),
    ("squares empty",        "squares([])",                        []),
    ("evens",                "evens([1, 2, 3, 4])",                [2, 4]),
    ("as strings",           "as_strings([1, 2])",                 ["1", "2"]),
    ("words longer than 3",  "words_longer_than(['hi', 'hello'], 3)", ["hello"]),
    ("length map",           "length_map(['a', 'abc'])",           {"a": 1, "abc": 3}),
    ("invert",               "invert({'a': 1})",                   {1: "a"}),
    ("unique squares",       "unique_squares([1, -1, 2])",         {1, 4}),
    ("sum of squares",       "sum_of_squares([1, 2, 3])",          14),
    ("first negative",       "first_negative([3, -2, -5])",        -2),
    ("first negative none",  "first_negative([1, 2])",             None),
    ("flatten once",         "flatten_once([[1, 2], [3]])",        [1, 2, 3]),
]

SOLUTION = '''
def squares(nums):
    return [number * number for number in nums]


def evens(nums):
    return [number for number in nums if number % 2 == 0]


def as_strings(nums):
    return [str(number) for number in nums]


def words_longer_than(words, length):
    return [word for word in words if len(word) > length]


def length_map(words):
    return {word: len(word) for word in words}


def invert(mapping):
    return {value: key for key, value in mapping.items()}


def unique_squares(nums):
    return {number * number for number in nums}


def sum_of_squares(nums):
    return sum(number * number for number in nums)


def first_negative(nums):
    return next((number for number in nums if number < 0), None)


def flatten_once(matrix):
    return [value for row in matrix for value in row]
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 12 · comprehensions & generators", CASES, namespace)
    summary()
