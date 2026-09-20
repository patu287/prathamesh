"""
EXERCISE 04 · Strings

    ▶ run        : python3 exercises/ex_04_strings.py
    ▶ solution   : python3 exercises/ex_04_strings.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def reverse_string(text):
    """Return the text backwards.  reverse_string("abc") -> "cba" """
    raise NotImplementedError


def is_palindrome(text):
    """True when the text reads the same forwards and backwards.
    Ignore case, spaces and punctuation: "A man, a plan, a canal: Panama" -> True
    """
    raise NotImplementedError


def count_vowels(text):
    """Count the vowels a, e, i, o, u (case-insensitive)."""
    raise NotImplementedError


def capitalize_words(sentence):
    """Capitalise the first letter of every word.
    capitalize_words("hello big world") -> "Hello Big World"
    """
    raise NotImplementedError


def remove_spaces(text):
    """Return the text with every space removed."""
    raise NotImplementedError


def initials(full_name):
    """Return the uppercase initials of each word joined by dots (no trailing dot).
    initials("prathamesh kumar sharma") -> "P.K.S"
    """
    raise NotImplementedError


def swap_case(text):
    """Uppercase letters become lowercase and vice versa."""
    raise NotImplementedError


CASES = [
    ("reverse",              "reverse_string('abc')",                "cba"),
    ("reverse empty",        "reverse_string('')",                   ""),
    ("palindrome word",      "is_palindrome('racecar')",             True),
    ("palindrome sentence",  "is_palindrome('A man, a plan, a canal: Panama')", True),
    ("not a palindrome",     "is_palindrome('hello')",               False),
    ("empty is a palindrome", "is_palindrome('')",                   True),
    ("count vowels",         "count_vowels('Programming')",          3),
    ("count vowels none",    "count_vowels('xyz')",                  0),
    ("capitalize words",     "capitalize_words('hello big world')",  "Hello Big World"),
    ("remove spaces",        "remove_spaces('a b  c')",              "abc"),
    ("initials",             "initials('prathamesh kumar sharma')",  "P.K.S"),
    ("single-word initials", "initials('ravi')",                     "R"),
    ("swap case",            "swap_case('AbC')",                     "aBc"),
]

SOLUTION = '''
def reverse_string(text):
    return text[::-1]


def is_palindrome(text):
    cleaned = "".join(char.lower() for char in text if char.isalnum())
    return cleaned == cleaned[::-1]


def count_vowels(text):
    return sum(1 for char in text.lower() if char in "aeiou")


def capitalize_words(sentence):
    return " ".join(word.capitalize() for word in sentence.split())


def remove_spaces(text):
    return text.replace(" ", "")


def initials(full_name):
    return ".".join(word[0].upper() for word in full_name.split())


def swap_case(text):
    return text.swapcase()
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 04 · strings", CASES, namespace)
    summary()
