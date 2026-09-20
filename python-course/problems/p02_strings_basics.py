"""
PROBLEM p02 · Strings: reverse, palindrome, words     [Easy · strings, two pointers]

1. `reverse_string(text)` -> the text backwards.
        reverse_string("hello") -> "olleh"
2. `is_palindrome(text)` -> True when it reads the same both ways, ignoring
   case and non-alphanumeric characters.
        is_palindrome("A man, a plan, a canal: Panama") -> True
        is_palindrome("hello") -> False
   Do it with two pointers (one index from each end) — that is the O(1) space
   version an interviewer wants to see.
3. `reverse_words(sentence)` -> the words in reverse order, single spaces.
        reverse_words("  the sky is blue ") -> "blue is sky the"
4. `count_words(sentence)` -> {word: count} with lowercase words.

    ▶ run        : python3 problems/p02_strings_basics.py
    ▶ solution   : python3 problems/p02_strings_basics.py --solution
    ▶ topic      : dsa/dsa_02_strings.py
    ▶ complexity : O(n) each (two pointers for the palindrome: O(1) extra space)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def reverse_string(text):
    raise NotImplementedError


def is_palindrome(text):
    """Two-pointer version: no cleaned-up copy of the whole string."""
    raise NotImplementedError


def reverse_words(sentence):
    raise NotImplementedError


def count_words(sentence):
    raise NotImplementedError


CASES = [
    ("reverse",             "reverse_string('hello')",              "olleh"),
    ("reverse empty",       "reverse_string('')",                   ""),
    ("palindrome word",     "is_palindrome('racecar')",             True),
    ("palindrome sentence", "is_palindrome('A man, a plan, a canal: Panama')", True),
    ("palindrome number-ish", "is_palindrome('12321')",             True),
    ("not a palindrome",    "is_palindrome('hello')",               False),
    ("empty is palindrome", "is_palindrome('')",                    True),
    ("reverse words",       "reverse_words('  the sky is blue ')",  "blue is sky the"),
    ("reverse one word",    "reverse_words('hi')",                  "hi"),
    ("count words",         "count_words('the cat the')",           {"the": 2, "cat": 1}),
]

SOLUTION = '''
from collections import Counter


def reverse_string(text):
    return text[::-1]


def is_palindrome(text):
    left, right = 0, len(text) - 1
    while left < right:
        if not text[left].isalnum():
            left += 1
        elif not text[right].isalnum():
            right -= 1
        elif text[left].lower() != text[right].lower():
            return False
        else:
            left += 1
            right -= 1
    return True


def reverse_words(sentence):
    return " ".join(sentence.split()[::-1])


def count_words(sentence):
    return dict(Counter(sentence.lower().split()))
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p02 · strings basics", CASES, globals())
    summary()
