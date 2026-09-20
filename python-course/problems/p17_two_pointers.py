"""
PROBLEM p17 · Two pointers on sorted data            [Medium · two pointers]

Two indices walking toward each other turn an O(n^2) pair search into O(n).
The precondition is usually "the data is sorted".

1. `pair_with_sum(sorted_nums, target)` -> the pair of VALUES that sums to the
   target, or None. (You already did the hash-map version in p03 — this is the
   O(1) extra space version.)
        pair_with_sum([1, 3, 4, 6], 10) -> (4, 6)

2. `count_pairs_with_sum(sorted_nums, target)` -> how many index pairs (i < j)
   sum to the target. [1, 1, 1] with target 2 has 3 pairs.

3. `two_sum_closest(sorted_nums, target)` -> the pair whose sum is closest to
   the target (if two are equally close, take the smaller sum).
        two_sum_closest([1, 3, 4, 6], 8) -> (1, 6)      # sum 7, distance 1

4. `remove_duplicates_in_place(nums)` -> given a SORTED list, remove the
   duplicates IN PLACE and return the new length. The first `length` items must
   hold the distinct values in order.
        nums = [1, 1, 2, 3, 3] -> returns 3, nums[:3] == [1, 2, 3]

5. `is_palindrome_two_pointer(text)` -> True/False using two indices (ignore
   case and non-alphanumeric characters).

    ▶ run        : python3 problems/p17_two_pointers.py
    ▶ solution   : python3 problems/p17_two_pointers.py --solution
    ▶ topic      : dsa/dsa_01_arrays.py
    ▶ complexity : O(n) time, O(1) extra space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def in_place_result(nums):
    """Provided helper: run remove_duplicates_in_place and return the kept prefix."""
    length = remove_duplicates_in_place(nums)
    return nums[:length]


def pair_with_sum(sorted_nums, target):
    raise NotImplementedError


def count_pairs_with_sum(sorted_nums, target):
    raise NotImplementedError


def two_sum_closest(sorted_nums, target):
    """Return the pair of values with the sum closest to the target."""
    raise NotImplementedError


def remove_duplicates_in_place(nums):
    """Return the new length; nums must be modified in place."""
    raise NotImplementedError


def is_palindrome_two_pointer(text):
    raise NotImplementedError


CASES = [
    ("pair found (any valid pair)",
     "(lambda pair: pair is not None and sum(pair) == 10)"
     "(pair_with_sum([1, 3, 4, 6, 8, 11], 10))",                          True),
    ("pair later",            "pair_with_sum([1, 3, 4, 6], 10)",         (4, 6)),
    ("pair none",             "pair_with_sum([1, 2], 100)",              None),
    ("pair in one element",   "pair_with_sum([5], 10)",                  None),
    ("count pairs",           "count_pairs_with_sum([1, 1, 1], 2)",      3),
    ("count pairs none",      "count_pairs_with_sum([1, 2, 3], 100)",    0),
    ("count pairs mixed",     "count_pairs_with_sum([1, 2, 3, 4, 5], 5)", 2),
    ("closest",               "two_sum_closest([1, 3, 4, 6], 8)",        (1, 6)),
    ("closest exact",         "two_sum_closest([1, 3, 4, 6], 10)",       (4, 6)),
    ("remove duplicates",     "in_place_result([1, 1, 2, 3, 3])",        [1, 2, 3]),
    ("remove no duplicates",  "in_place_result([1, 2, 3])",              [1, 2, 3]),
    ("remove all equal",      "in_place_result([2, 2, 2])",              [2]),
    ("palindrome",            "is_palindrome_two_pointer('A man, a plan, a canal: Panama')", True),
    ("not palindrome",        "is_palindrome_two_pointer('hello')",      False),
]

SOLUTION = '''
def pair_with_sum(sorted_nums, target):
    left, right = 0, len(sorted_nums) - 1
    while left < right:
        total = sorted_nums[left] + sorted_nums[right]
        if total == target:
            return (sorted_nums[left], sorted_nums[right])
        if total < target:
            left += 1
        else:
            right -= 1
    return None


def count_pairs_with_sum(sorted_nums, target):
    left, right = 0, len(sorted_nums) - 1
    pairs = 0
    while left < right:
        total = sorted_nums[left] + sorted_nums[right]
        if total == target:
            if sorted_nums[left] == sorted_nums[right]:
                span = right - left + 1
                pairs += span * (span - 1) // 2
                break
            left_count = 1
            while left + 1 < right and sorted_nums[left + 1] == sorted_nums[left]:
                left_count += 1
                left += 1
            right_count = 1
            while right - 1 > left and sorted_nums[right - 1] == sorted_nums[right]:
                right_count += 1
                right -= 1
            pairs += left_count * right_count
            left += 1
            right -= 1
        elif total < target:
            left += 1
        else:
            right -= 1
    return pairs


def two_sum_closest(sorted_nums, target):
    left, right = 0, len(sorted_nums) - 1
    best_pair = None
    best_distance = None
    while left < right:
        total = sorted_nums[left] + sorted_nums[right]
        distance = abs(total - target)
        if best_distance is None or distance < best_distance or (
                distance == best_distance and total < sum(best_pair)):
            best_distance = distance
            best_pair = (sorted_nums[left], sorted_nums[right])
        if total < target:
            left += 1
        else:
            right -= 1
    return best_pair


def remove_duplicates_in_place(nums):
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


def is_palindrome_two_pointer(text):
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
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p17 · two pointers", CASES, globals())
    summary()
