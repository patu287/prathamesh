"""
EXERCISE 11 · Errors, exceptions & files

    ▶ run        : python3 exercises/ex_11_errors_files.py
    ▶ solution   : python3 exercises/ex_11_errors_files.py --solution
"""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def error_name(thunk):
    """Provided helper: call thunk() and report which exception it raised.

    error_name(lambda: int("x")) -> "ValueError"
    error_name(lambda: 1 + 1)    -> "none"
    """
    try:
        thunk()
    except Exception as exc:                       # noqa: BLE001 - on purpose
        return type(exc).__name__
    return "none"


def file_round_trip(path):
    """Provided helper: write three lines, then read the numbers back."""
    write_lines(path, ["10", "x", "30"])
    return read_numbers(path)


def safe_int(text, default=0):
    """Convert text to an int; return `default` when it cannot be converted.
    Works for "abc", None, "3.5" (int("3.5") fails -> default).
    """
    raise NotImplementedError


def divide(a, b):
    """Return a / b. Let Python raise ZeroDivisionError for b == 0 and
    TypeError for bad types — just do the division.
    """
    raise NotImplementedError


def parse_int_list(text):
    """Parse "1, 2, x, 4" into [1, 2, 4], silently skipping invalid pieces."""
    raise NotImplementedError


def require_positive(number):
    """Return the number when it is > 0.
    Raise TypeError when it is not a number, ValueError("must be positive") otherwise.
    """
    raise NotImplementedError


def write_lines(path, lines):
    """Write each item of `lines` on its own line (encoding="utf-8").
    Return the number of lines written.
    """
    raise NotImplementedError


def read_numbers(path):
    """Read a file with one number per line; return the list of ints,
    skipping lines that are not valid integers.
    """
    raise NotImplementedError


CASES = [
    ("safe_int ok",            "safe_int('42')",                       42),
    ("safe_int bad",           "safe_int('abc')",                      0),
    ("safe_int custom default", "safe_int('abc', -1)",                 -1),
    ("safe_int None",          "safe_int(None)",                       0),
    ("safe_int float text",    "safe_int('3.5')",                      0),
    ("divide works",           "divide(10, 4)",                        2.5),
    ("divide by zero",         "error_name(lambda: divide(1, 0))",     "ZeroDivisionError"),
    ("divide bad types",       "error_name(lambda: divide('a', 2))",   "TypeError"),
    ("parse int list",         "parse_int_list('1, 2, x, 4')",         [1, 2, 4]),
    ("parse int list all bad", "parse_int_list('a, b')",               []),
    ("require positive ok",    "require_positive(5)",                  5),
    ("require positive raises", "error_name(lambda: require_positive(0))", "ValueError"),
    ("require positive type",  "error_name(lambda: require_positive('x'))", "TypeError"),
    ("write + read file",
     "file_round_trip(tempfile.mktemp(suffix='.txt'))",                [10, 30]),
    ("write_lines count",
     "write_lines(tempfile.mktemp(suffix='.txt'), ['a', 'b'])",        2),
]

SOLUTION = '''
def safe_int(text, default=0):
    try:
        return int(text)
    except (TypeError, ValueError):
        return default


def divide(a, b):
    return a / b


def parse_int_list(text):
    numbers = []
    for piece in text.split(","):
        try:
            numbers.append(int(piece.strip()))
        except ValueError:
            continue
    return numbers


def require_positive(number):
    if not isinstance(number, (int, float)) or isinstance(number, bool):
        raise TypeError("number must be an int or float")
    if number <= 0:
        raise ValueError("must be positive")
    return number


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\\n")
    return len(lines)


def read_numbers(path):
    numbers = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                numbers.append(int(line.strip()))
            except ValueError:
                continue
    return numbers
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 11 · errors & files", CASES, namespace)
    summary()
