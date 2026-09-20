"""
PROBLEM p12 · Stacks: brackets & path cleaning          [Medium · stacks]

A stack is "the most recent thing first". Any problem about matching, nesting
or pairs is a stack problem.

1. `is_balanced(text)` -> True when every bracket is closed in the right order.
        is_balanced("([{}])") -> True
        is_balanced("(]")     -> False
        is_balanced("")       -> True
   Ignore characters that are not brackets.

2. `min_removals(text)` -> the smallest number of bracket characters to delete
   to make the string balanced.
        min_removals("(()))(") -> 2

3. `simplify_path(path)` -> clean up a Unix path: "." means here, ".." goes up,
   repeated slashes collapse.
        simplify_path("/a/./b/../../c/") -> "/c"
        simplify_path("/../")            -> "/"

4. `remove_adjacent_duplicates(text)` -> repeatedly delete adjacent equal
   letters until there are none left (a stack does this in one pass).
        remove_adjacent_duplicates("abbaca") -> "ca"

    ▶ run        : python3 problems/p12_stacks.py
    ▶ solution   : python3 problems/p12_stacks.py --solution
    ▶ topic      : dsa/dsa_07_stacks_queues.py
    ▶ complexity : O(n) time, O(n) space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def is_balanced(text):
    raise NotImplementedError


def min_removals(text):
    raise NotImplementedError


def simplify_path(path):
    raise NotImplementedError


def remove_adjacent_duplicates(text):
    raise NotImplementedError


CASES = [
    ("balanced simple",     "is_balanced('()')",                     True),
    ("balanced nested",     "is_balanced('([{}])')",                 True),
    ("unbalanced order",    "is_balanced('(]')",                     False),
    ("unbalanced extra",    "is_balanced('(()')",                    False),
    ("unbalanced closing",  "is_balanced(')(')",                     False),
    ("ignores other chars", "is_balanced('a(b[c]{d})e')",            True),
    ("empty is balanced",   "is_balanced('')",                       True),
    ("min removals",        "min_removals('(()))(')",                2),
    ("min removals ok",     "min_removals('()')",                    0),
    ("min removals all bad", "min_removals(')))')",                  3),
    ("simplify path",       "simplify_path('/a/./b/../../c/')",      "/c"),
    ("simplify root",       "simplify_path('/../')",                 "/"),
    ("simplify repeated",   "simplify_path('/home//user/')",         "/home/user"),
    ("remove adjacent",     "remove_adjacent_duplicates('abbaca')",  "ca"),
    ("remove adjacent none", "remove_adjacent_duplicates('abc')",    "abc"),
]

SOLUTION = '''
PAIRS = {")": "(", "]": "[", "}": "{"}


def is_balanced(text):
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in PAIRS:
            if not stack or stack.pop() != PAIRS[char]:
                return False
    return not stack


def min_removals(text):
    stack = []
    removals = 0
    for char in text:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if stack:
                stack.pop()
            else:
                removals += 1
    return removals + len(stack)


def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)


def remove_adjacent_duplicates(text):
    stack = []
    for char in text:
        if stack and stack[-1] == char:
            stack.pop()
        else:
            stack.append(char)
    return "".join(stack)
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p12 · stacks", CASES, globals())
    summary()
