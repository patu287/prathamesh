"""
PROBLEM p06 · Anagrams & character counts               [Easy-Medium · hashing]

1. `is_anagram(a, b)` -> True when the two strings use exactly the same letters
   with the same counts, ignoring case and spaces.
        is_anagram("Dormitory", "dirty room") -> True
        is_anagram("hello", "world")          -> False
   Aim for O(n) with a character count (Counter), not O(n log n) with sorting.

2. `group_anagrams(words)` -> groups of words that are anagrams of each other.
   Return a list of lists; the words inside each group keep their input order,
   and the groups are ordered by their first word's position in the input.
        group_anagrams(["eat", "tea", "tan", "ate"])
        -> [["eat", "tea", "ate"], ["tan"]]

3. `common_characters(words)` -> the characters present in EVERY word
   (sorted, no duplicates).

    ▶ run        : python3 problems/p06_anagrams.py
    ▶ solution   : python3 problems/p06_anagrams.py --solution
    ▶ topic      : dsa/dsa_02_strings.py, dsa/dsa_03_hashmaps.py
    ▶ complexity : O(n) for is_anagram, O(n * k) for the grouping
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def is_anagram(a, b):
    """Case-insensitive, ignores spaces and punctuation."""
    raise NotImplementedError


def group_anagrams(words):
    """Groups ordered by where the first member appeared."""
    raise NotImplementedError


def common_characters(words):
    """Sorted list of characters shared by every word. Empty list -> []."""
    raise NotImplementedError


CASES = [
    ("anagram simple",     "is_anagram('listen', 'silent')",        True),
    ("anagram with case",  "is_anagram('Dormitory', 'dirty room')", True),
    ("not an anagram",     "is_anagram('hello', 'world')",          False),
    ("anagram empty",      "is_anagram('', '')",                    True),
    ("different lengths",  "is_anagram('abc', 'ab')",               False),
    ("group anagrams",     "group_anagrams(['eat', 'tea', 'tan', 'ate'])",
                           [["eat", "tea", "ate"], ["tan"]]),
    ("group anagrams 2",   "group_anagrams(['ab', 'ba', 'abc'])",   [["ab", "ba"], ["abc"]]),
    ("group empty",        "group_anagrams([])",                    []),
    ("common characters",  "common_characters(['bella', 'label', 'roller'])", ["e", "l"]),
    ("common none",        "common_characters(['abc', 'def'])",     []),
]

SOLUTION = '''
from collections import Counter, defaultdict


def is_anagram(a, b):
    clean = lambda text: Counter(char.lower() for char in text if char.isalnum())
    return clean(a) == clean(b)


def group_anagrams(words):
    groups = defaultdict(list)
    order = []
    for word in words:
        key = "".join(sorted(word.lower()))
        if key not in groups:
            order.append(key)
        groups[key].append(word)
    return [groups[key] for key in order]


def common_characters(words):
    if not words:
        return []
    shared = set(words[0].lower())
    for word in words[1:]:
        shared &= set(word.lower())
    return sorted(shared)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p06 · anagrams", CASES, globals())
    summary()
