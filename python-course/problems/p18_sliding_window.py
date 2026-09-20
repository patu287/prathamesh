"""
PROBLEM p18 · Sliding window                          [Medium-Hard · windows]

A sliding window is a pair of indices that moves through the data without ever
going back, so the whole scan costs O(n) even though it looks like two loops.

    left = 0
    for right in range(n):
        add nums[right] to the window
        while the window is invalid:
            remove nums[left]; left += 1
        the window [left..right] is now valid -> record the answer

1. `max_sum_window(nums, k)` -> the largest sum of any k consecutive elements.
        max_sum_window([2, 1, 5, 1, 3, 2], 3) -> 9      # 5+1+3

2. `longest_unique_substring(text)` -> the LENGTH of the longest substring with
   no repeated characters.
        longest_unique_substring("pwwkew") -> 3     # "wke"

3. `min_size_subarray_sum(nums, target)` -> the length of the shortest
   contiguous subarray whose sum is >= target, or 0 when none exists.
   (Values are positive, which is what makes the window slide cleanly.)
        min_size_subarray_sum([2, 3, 1, 2, 4, 3], 7) -> 2   # 4+3

4. `longest_subarray_of_ones(nums, k)` -> the longest run of 1s you can make if
   you may flip at most k zeros.
        longest_subarray_of_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) -> 6

    ▶ run        : python3 problems/p18_sliding_window.py
    ▶ solution   : python3 problems/p18_sliding_window.py --solution
    ▶ topic      : dsa/dsa_02_strings.py, dsa/dsa_01_arrays.py
    ▶ complexity : O(n) time; the dict/set window uses O(k) space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def max_sum_window(nums, k):
    """k <= 0 or k > len(nums) -> None."""
    raise NotImplementedError


def longest_unique_substring(text):
    raise NotImplementedError


def min_size_subarray_sum(nums, target):
    raise NotImplementedError


def longest_subarray_of_ones(nums, k):
    raise NotImplementedError


CASES = [
    ("max window k=3",      "max_sum_window([2, 1, 5, 1, 3, 2], 3)",  9),
    ("max window k=1",      "max_sum_window([2, 1, 5], 1)",           5),
    ("max window k=len",    "max_sum_window([1, 2, 3], 3)",           6),
    ("max window too big",  "max_sum_window([1, 2], 5)",              None),
    ("max window k=0",      "max_sum_window([1, 2], 0)",              None),
    ("longest unique",      "longest_unique_substring('abcabcbb')",   3),
    ("longest unique same", "longest_unique_substring('bbbbb')",      1),
    ("longest unique pwwkew", "longest_unique_substring('pwwkew')",   3),
    ("longest unique empty", "longest_unique_substring('')",          0),
    ("min size subarray",   "min_size_subarray_sum([2, 3, 1, 2, 4, 3], 7)", 2),
    ("min size impossible", "min_size_subarray_sum([1, 1], 100)",     0),
    ("min size whole array", "min_size_subarray_sum([1, 2, 3], 6)",   3),
    ("ones with 2 flips",   "longest_subarray_of_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)", 6),
    ("ones with no zeros",  "longest_subarray_of_ones([1, 1, 1], 0)", 3),
    ("ones all zeros k=2",  "longest_subarray_of_ones([0, 0, 0], 2)", 2),
]

SOLUTION = '''
def max_sum_window(nums, k):
    if k <= 0 or k > len(nums):
        return None
    window = sum(nums[:k])
    best = window
    for index in range(k, len(nums)):
        window += nums[index] - nums[index - k]
        best = max(best, window)
    return best


def longest_unique_substring(text):
    last_seen = {}
    start = 0
    best = 0
    for index, char in enumerate(text):
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1
        last_seen[char] = index
        best = max(best, index - start + 1)
    return best


def min_size_subarray_sum(nums, target):
    left = 0
    window = 0
    best = 0
    for right, value in enumerate(nums):
        window += value
        while window >= target:
            length = right - left + 1
            best = length if best == 0 else min(best, length)
            window -= nums[left]
            left += 1
    return best


def longest_subarray_of_ones(nums, k):
    left = 0
    zeros = 0
    best = 0
    for right, value in enumerate(nums):
        if value == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p18 · sliding window", CASES, globals())
    summary()
