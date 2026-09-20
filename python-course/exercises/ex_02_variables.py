"""
EXERCISE 02 · Variables, types & f-strings

    ▶ run        : python3 exercises/ex_02_variables.py
    ▶ solution   : python3 exercises/ex_02_variables.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def celsius_to_fahrenheit(celsius):
    """F = C * 9 / 5 + 32.  celsius_to_fahrenheit(100) -> 212.0"""
    raise NotImplementedError


def split_bill(total, people, tip_percent=10):
    """Return each person's share (float) including the tip.

    split_bill(1100, 4) -> 302.5      # 1100 + 10% = 1210, / 4
    """
    raise NotImplementedError


def seconds_to_clock(total_seconds):
    """Return "H:MM:SS" (no zero padding on hours).

    seconds_to_clock(3725) -> "1:02:05"
    (hint: f-strings can pad: f"{seconds:02d}")
    """
    raise NotImplementedError


def type_name(value):
    """Return the name of the value's type as a string.

    type_name(5) -> "int"  |  type_name("hi") -> "str"
    """
    raise NotImplementedError


def describe_person(name, age, city="Pune"):
    """Return "<name> (age <age>) from <city>".
    describe_person("Ravi", 21) -> "Ravi (age 21) from Pune"
    """
    raise NotImplementedError


CASES = [
    ("water boils",         "celsius_to_fahrenheit(100)",       212.0),
    ("freezing point",      "celsius_to_fahrenheit(0)",         32.0),
    ("37 degrees",          "celsius_to_fahrenheit(37)",        98.6),
    ("split a bill",        "split_bill(1100, 4)",              302.5),
    ("no tip",              "split_bill(1000, 4, 0)",           250.0),
    ("clock format",        "seconds_to_clock(3725)",           "1:02:05"),
    ("clock under a minute", "seconds_to_clock(9)",             "0:00:09"),
    ("type of int",         "type_name(5)",                     "int"),
    ("type of str",         "type_name('hi')",                  "str"),
    ("type of bool",        "type_name(True)",                  "bool"),
    ("describe",            "describe_person('Ravi', 21)",      "Ravi (age 21) from Pune"),
    ("describe with city",  "describe_person('Asha', 30, 'Delhi')", "Asha (age 30) from Delhi"),
]

SOLUTION = '''
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def split_bill(total, people, tip_percent=10):
    total_with_tip = total * (1 + tip_percent / 100)
    return total_with_tip / people


def seconds_to_clock(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def type_name(value):
    return type(value).__name__


def describe_person(name, age, city="Pune"):
    return f"{name} (age {age}) from {city}"
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 02 · variables & types", CASES, namespace)
    summary()
