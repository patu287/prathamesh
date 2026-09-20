"""
PROBLEM p16 · Permutations                          [Medium-Hard · backtracking]

A permutation is an arrangement of all the elements; there are n! of them.
This is the other half of the backtracking toolkit (subsets = take/skip,
permutations = choose one of the remaining items).

1. `permutations_of(items)` -> every ordering, as a list of lists (any order).
        len(permutations_of([1, 2, 3])) -> 6

2. `permutations_of_string(text)` -> every distinct arrangement of the letters,
   sorted, WITHOUT duplicates.
        permutations_of_string("aab") -> ["aab", "aba", "baa"]

3. `next_permutation(nums)` -> the next arrangement in lexicographic order,
   in place, using the standard algorithm:
        next_permutation([1, 2, 3]) -> [1, 3, 2]
        next_permutation([3, 2, 1]) -> [1, 2, 3]     # wraps around
   Algorithm: find the rightmost i with nums[i] < nums[i+1]; if none, reverse
   everything and stop. Otherwise find the rightmost j > i with nums[j] > nums[i],
   swap them, then reverse nums[i+1:].

4. `count_permutations(items)` -> len(items)! computed (for n <= 20).

    ▶ run        : python3 problems/p16_permutations.py
    ▶ solution   : python3 problems/p16_permutations.py --solution
    ▶ topic      : dsa/dsa_06_recursion.py
    ▶ complexity : O(n! * n) to generate them all; next_permutation is O(n)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def permutations_of(items):
    """All n! orderings as a list of lists (any order)."""
    raise NotImplementedError


def permutations_of_string(text):
    """Sorted distinct arrangements of the letters."""
    raise NotImplementedError


def next_permutation(nums):
    """Modify nums in place and return it (wrapping around at the end)."""
    raise NotImplementedError


def count_permutations(items):
    """len(items)! computed with a loop (no recursion needed)."""
    raise NotImplementedError


CASES = [
    ("permutations count",   "len(permutations_of([1, 2, 3]))",       6),
    ("permutations content", "sorted(map(tuple, permutations_of([1, 2])))",
     [(1, 2), (2, 1)]),
    ("permutations of one",  "sorted(map(tuple, permutations_of([7])))", [(7,)]),
    ("permutations of none", "sorted(map(tuple, permutations_of([])))", [()]),
    ("string permutations",  "permutations_of_string('aab')",         ["aab", "aba", "baa"]),
    ("string all distinct",  "len(permutations_of_string('abc'))",    6),
    ("next permutation",     "next_permutation([1, 2, 3])",           [1, 3, 2]),
    ("next permutation wrap", "next_permutation([3, 2, 1])",          [1, 2, 3]),
    ("next permutation with dupes", "next_permutation([1, 1, 5])",    [1, 5, 1]),
    ("count permutations",   "count_permutations(list(range(5)))",    120),
    ("count permutations 0", "count_permutations([])",                1),
]

SOLUTION = '''
def permutations_of(items):
    result = []

    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])
            return
        for index in range(len(remaining)):
            current.append(remaining[index])
            backtrack(current, remaining[:index] + remaining[index + 1:])
            current.pop()

    backtrack([], list(items))
    return result


def permutations_of_string(text):
    return sorted({"".join(permutation) for permutation in permutations_of(list(text))})


def next_permutation(nums):
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i < 0:
        nums.reverse()
        return nums
    j = len(nums) - 1
    while nums[j] <= nums[i]:
        j -= 1
    nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])
    return nums


def count_permutations(items):
    total = 1
    for number in range(2, len(items) + 1):
        total *= number
    return total
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p16 · permutations", CASES, globals())
    summary()
