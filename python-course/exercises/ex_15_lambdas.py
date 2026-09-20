"""
EXERCISE 15 · Lambdas, sorting & decorators

    ▶ run        : python3 exercises/ex_15_lambdas.py
    ▶ solution   : python3 exercises/ex_15_lambdas.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def sort_by_length(words):
    """Sort words by length (shortest first); ties keep alphabetical order."""
    raise NotImplementedError


def sort_by_second(pairs):
    """Sort (name, score) pairs by score descending, then name ascending."""
    raise NotImplementedError


def sort_people(people):
    """people is a list of dicts with "name" and "age".
    Sort by age ascending, then by name."""
    raise NotImplementedError


def top_n(scores, n):
    """scores is {name: score}. Return the n (name, score) tuples with the
    highest scores, sorted by score descending then name ascending.
    """
    raise NotImplementedError


def apply_to_all(func, values):
    """Return [func(value) for value in values] (a lambda-friendly map)."""
    raise NotImplementedError


def make_adder(amount):
    """Return a function that adds `amount` to its argument (a closure)."""
    raise NotImplementedError


def memoize(func):
    """Return a wrapper that caches results of `func` by its arguments.

    memoize(slow)(5) must call slow only the first time for the argument 5.
    (Hint: a dict in the closure. functools.wraps is nice but optional.)
    """
    raise NotImplementedError


def repeat_call(func, times):
    """Call func(i) for i in range(times) and return the LAST result.
    repeat_call(make_adder(1), 3) calls func(0), func(1), func(2) -> 3
    """
    raise NotImplementedError


def memoization_effect():
    """Provided helper: how many times is the underlying function really called
    when the memoized version is called three times with the same argument?"""
    calls = []

    def slow(value):
        calls.append(value)
        return value * 2

    fast = memoize(slow)
    fast(3)
    fast(3)
    fast(3)
    return len(calls)


CASES = [
    ("sort by length",     "sort_by_length(['banana', 'fig', 'kiwi'])", ["fig", "kiwi", "banana"]),
    ("sort by length ties", "sort_by_length(['bb', 'aa'])",             ["aa", "bb"]),
    ("sort by second",     "sort_by_second([('ravi', 88), ('priya', 95), ('asha', 88)])",
                           [("priya", 95), ("asha", 88), ("ravi", 88)]),
    ("sort people",        "sort_people([{'name': 'b', 'age': 30}, {'name': 'a', 'age': 20}])",
                           [{"name": "a", "age": 20}, {"name": "b", "age": 30}]),
    ("sort people tie",    "sort_people([{'name': 'zoe', 'age': 20}, {'name': 'amy', 'age': 20}])",
                           [{"name": "amy", "age": 20}, {"name": "zoe", "age": 20}]),
    ("top n",              "top_n({'a': 10, 'b': 30, 'c': 20}, 2)",     [("b", 30), ("c", 20)]),
    ("top n tie",          "top_n({'zed': 5, 'amy': 5}, 1)",            [("amy", 5)]),
    ("apply to all",       "apply_to_all(lambda x: x + 1, [1, 2])",     [2, 3]),
    ("apply str.upper",    "apply_to_all(str.upper, ['a', 'b'])",       ["A", "B"]),
    ("make adder",         "make_adder(5)(10)",                         15),
    ("make adder zero",    "make_adder(0)(7)",                          7),
    ("memoize returns value", "memoize(lambda n: n * 2)(21)",           42),
    ("memoize caches",     "memoization_effect()",                      1),
    ("repeat call",        "repeat_call(make_adder(1), 3)",              3),
]

SOLUTION = '''
from functools import wraps


def sort_by_length(words):
    return sorted(words, key=lambda word: (len(word), word))


def sort_by_second(pairs):
    return sorted(pairs, key=lambda pair: (-pair[1], pair[0]))


def sort_people(people):
    return sorted(people, key=lambda person: (person["age"], person["name"]))


def top_n(scores, n):
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))[:n]


def apply_to_all(func, values):
    return [func(value) for value in values]


def make_adder(amount):
    def add(value):
        return value + amount
    return add


def memoize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


def repeat_call(func, times):
    result = None
    for index in range(times):
        result = func(index)
    return result
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 15 · lambdas, sorting & decorators", CASES, namespace)
    summary()
