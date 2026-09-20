"""
EXERCISE 09 · Dictionaries (the most useful exercise in this file set)

    ▶ run        : python3 exercises/ex_09_dicts.py
    ▶ solution   : python3 exercises/ex_09_dicts.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def word_count(text):
    """Return {word: count} for the lowercase words in the text.
    word_count("the cat the") -> {"the": 2, "cat": 1}
    """
    raise NotImplementedError


def invert_dict(mapping):
    """Swap keys and values.  invert_dict({"a": 1, "b": 2}) -> {1: "a", 2: "b"}"""
    raise NotImplementedError


def merge_counts(first, second):
    """Add two count dictionaries together (missing keys count as 0)."""
    raise NotImplementedError


def top_scorer(scores):
    """Return the NAME with the highest score. Ties: the alphabetically first.
    top_scorer({"ravi": 88, "priya": 95}) -> "priya"
    """
    raise NotImplementedError


def group_by_length(words):
    """Return {length: [words]}.
    group_by_length(["hi", "hello", "ok"]) -> {2: ["hi", "ok"], 5: ["hello"]}
    """
    raise NotImplementedError


def most_frequent(items):
    """The most frequent value. Ties: the one that appears first."""
    raise NotImplementedError


def two_sum(nums, target):
    """Return the indices (i, j) with i < j of the two values summing to target,
    in O(n) using a dictionary.  two_sum([2, 7, 11, 15], 9) -> (0, 1)
    Return None when there is no such pair.
    """
    raise NotImplementedError


CASES = [
    ("word count",        "word_count('the cat the')",            {"the": 2, "cat": 1}),
    ("word count case",   "word_count('Dog dog DOG')",            {"dog": 3}),
    ("word count empty",  "word_count('')",                       {}),
    ("invert dict",       "invert_dict({'a': 1, 'b': 2})",        {1: "a", 2: "b"}),
    ("merge counts",      "merge_counts({'a': 1, 'b': 2}, {'b': 3, 'c': 1})",
                          {"a": 1, "b": 5, "c": 1}),
    ("top scorer",        "top_scorer({'ravi': 88, 'priya': 95})", "priya"),
    ("top scorer tie",    "top_scorer({'zara': 95, 'asha': 95})",  "asha"),
    ("group by length",   "group_by_length(['hi', 'hello', 'ok'])", {2: ["hi", "ok"], 5: ["hello"]}),
    ("most frequent",     "most_frequent([3, 1, 3, 2])",          3),
    ("most frequent tie", "most_frequent([1, 1, 2, 2])",          1),
    ("two sum",           "two_sum([2, 7, 11, 15], 9)",           (0, 1)),
    ("two sum later pair", "two_sum([1, 3, 4, 6], 10)",           (2, 3)),
    ("two sum none",      "two_sum([1, 2], 100)",                 None),
    ("two sum duplicates", "two_sum([3, 3], 6)",                  (0, 1)),
]

SOLUTION = '''
from collections import Counter, defaultdict


def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def invert_dict(mapping):
    return {value: key for key, value in mapping.items()}


def merge_counts(first, second):
    merged = dict(first)
    for key, value in second.items():
        merged[key] = merged.get(key, 0) + value
    return merged


def top_scorer(scores):
    best = max(scores.values())
    return min(name for name, score in scores.items() if score == best)


def group_by_length(words):
    groups = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)
    return dict(groups)


def most_frequent(items):
    counts = Counter(items)
    best = max(counts.values())
    for item in items:
        if counts[item] == best:
            return item
    return None


def two_sum(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return (seen[complement], index)
        seen[value] = index
    return None
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 09 · dictionaries", CASES, namespace)
    summary()
