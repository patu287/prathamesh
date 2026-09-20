"""
EXERCISE 01 · Hello, Python (print, comments, errors)

    ▶ run        : python3 exercises/ex_01_basics.py
    ▶ solution   : python3 exercises/ex_01_basics.py --solution
    (the reference solution source is at the bottom of this file — try first!)

Rules: replace every `raise NotImplementedError` with working code.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def greet(name):
    """Return the text "Hello, <name>!".

    greet("Ravi") -> "Hello, Ravi!"
    """
    raise NotImplementedError


def rectangle_area(width, height):
    """Return the area of a rectangle (width * height)."""
    raise NotImplementedError


def to_minutes(hours, minutes):
    """Convert to a total number of minutes.

    to_minutes(1, 30) -> 90
    """
    raise NotImplementedError


def repeat_word(word, times):
    """Return the word repeated `times` times, with no spaces.

    repeat_word("ab", 3) -> "ababab"
    """
    raise NotImplementedError


def banner(text, width=10):
    """Return the text padded with "*" on the right until it is `width` wide.

    banner("Hi", 5) -> "Hi***"
    (hint: text + "*" * (width - len(text)))
    """
    raise NotImplementedError


CASES = [
    ("greet a name",              "greet('Ravi')",              "Hello, Ravi!"),
    ("greet an empty name",       "greet('')",                  "Hello, !"),
    ("rectangle area",            "rectangle_area(3, 4)",       12),
    ("rectangle area is a float", "rectangle_area(2.5, 2)",     5.0),
    ("1h30 in minutes",           "to_minutes(1, 30)",          90),
    ("0h5 in minutes",            "to_minutes(0, 5)",           5),
    ("repeat a word",             "repeat_word('ab', 3)",       "ababab"),
    ("repeat zero times",         "repeat_word('ab', 0)",       ""),
    ("banner",                    "banner('Hi', 5)",            "Hi***"),
    ("banner exact width",        "banner('abc', 3)",           "abc"),
]

SOLUTION = '''
def greet(name):
    return f"Hello, {name}!"


def rectangle_area(width, height):
    return width * height


def to_minutes(hours, minutes):
    return hours * 60 + minutes


def repeat_word(word, times):
    return word * times


def banner(text, width=10):
    return text + "*" * (width - len(text))
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 01 · hello, python", CASES, namespace)
    summary()
