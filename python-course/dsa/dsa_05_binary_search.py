"""
DSA 05 · Binary search

Binary search answers "where does this value belong?" in O(log n) by halving a
**sorted** search space. 20 guesses cover a million items. 30 cover a billion.

The loop you must be able to write from memory
----------------------------------------------
    left, right = 0, len(a) - 1
    while left <= right:
        mid = (left + right) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            left = mid + 1        # target is to the right
        else:
            right = mid - 1       # target is to the left
    return -1                      # not found

Five ways to get it wrong (learn these, they are the classic bugs)
------------------------------------------------------------------
1. `while left < right` instead of `<=`  -> misses the last element.
2. Not moving a pointer (`left = mid`)    -> infinite loop.
3. Off-by-one: `left = mid` vs `mid + 1`  -> decide the invariant, then follow it.
4. Searching unsorted data                -> the precondition is everything.
5. `mid = (left + right) / 2`             -> that is a float, not an index.

The two "boundary" searches (know both)
---------------------------------------
* `lower_bound` (a.k.a. bisect_left): the FIRST index where a[index] >= target
* `upper_bound` (a.k.a. bisect_right): the FIRST index where a[index] > target

    count of target in a sorted list = upper_bound - lower_bound
    insertion point for a new value  = lower_bound

Python already ships them: `bisect.bisect_left` / `bisect_right` / `insort`
implemented in C. Use them in real code; write the loops in interviews.

Binary search on the ANSWER (the powerful idea)
-----------------------------------------------
When you can ask a yes/no question that is monotonic — "is it possible with
capacity X?" — you can binary search on X instead of on an index. Classic
examples: ship packages in D days, split array largest sum, koko eating
bananas, minimum speed, sqrt of a number.
"""

import bisect
import time

print("=" * 60)
print("1. The canonical loop")
print("=" * 60)


def binary_search(nums, target):
    """Return the index of target, or -1. O(log n) time, O(1) space."""
    left, right = 0, len(nums) - 1
    while left <= right:
        middle = (left + right) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


data = [1, 3, 5, 7, 9, 11, 13]
print("  data:", data)
for target in [1, 7, 13, 4, 100]:
    print(f"    binary_search(data, {target:>3}) = {binary_search(data, target)}")


def binary_search_recursive(nums, target, left=0, right=None):
    """The recursive version — same complexity, more stack memory."""
    if right is None:
        right = len(nums) - 1
    if left > right:
        return -1
    middle = (left + right) // 2
    if nums[middle] == target:
        return middle
    if nums[middle] < target:
        return binary_search_recursive(nums, target, middle + 1, right)
    return binary_search_recursive(nums, target, left, middle - 1)


print("  recursive version:", binary_search_recursive(data, 9))

print("\n" + "=" * 60)
print("2. Lower bound / upper bound (the boundary searches)")
print("=" * 60)


def lower_bound(nums, target):
    """First index where nums[i] >= target (may be len(nums))."""
    left, right = 0, len(nums)          # right is EXCLUSIVE here
    while left < right:
        middle = (left + right) // 2
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def upper_bound(nums, target):
    """First index where nums[i] > target (may be len(nums))."""
    left, right = 0, len(nums)
    while left < right:
        middle = (left + right) // 2
        if nums[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left


data = [1, 2, 2, 2, 3, 5, 5, 8]
print("  data:", data)
for target in [2, 5, 7, 0, 9]:
    print(f"    target {target}: lower_bound={lower_bound(data, target)} "
          f"(bisect_left={bisect.bisect_left(data, target)})  "
          f"upper_bound={upper_bound(data, target)} "
          f"(bisect_right={bisect.bisect_right(data, target)})")

print("  count of 2s = upper - lower =", upper_bound(data, 2) - lower_bound(data, 2))

print("\n" + "=" * 60)
print("3. First and last occurrence of a value")
print("=" * 60)


def first_occurrence(nums, target):
    index = lower_bound(nums, target)
    return index if index < len(nums) and nums[index] == target else -1


def last_occurrence(nums, target):
    index = upper_bound(nums, target) - 1
    return index if index >= 0 and nums[index] == target else -1


for target in [2, 5, 8, 4]:
    print(f"  target {target}: first={first_occurrence(data, target)}, "
          f"last={last_occurrence(data, target)}")


def search_rotated(nums, target):
    """Search in a sorted-but-rotated array in O(log n).

    [4,5,6,7,0,1,2] — one half is always sorted; check which.
    """
    left, right = 0, len(nums) - 1
    while left <= right:
        middle = (left + right) // 2
        if nums[middle] == target:
            return middle
        if nums[left] <= nums[middle]:              # left half is sorted
            if nums[left] <= target < nums[middle]:
                right = middle - 1
            else:
                left = middle + 1
        else:                                       # right half is sorted
            if nums[middle] < target <= nums[right]:
                left = middle + 1
            else:
                right = middle - 1
    return -1


rotated = [4, 5, 6, 7, 0, 1, 2]
print("  rotated array:", rotated)
print("  search_rotated(0) =", search_rotated(rotated, 0),
      "| (5) =", search_rotated(rotated, 5),
      "| (3) =", search_rotated(rotated, 3))


def find_minimum_rotated(nums):
    """Smallest element of a rotated sorted array, O(log n)."""
    left, right = 0, len(nums) - 1
    while left < right:
        middle = (left + right) // 2
        if nums[middle] > nums[right]:
            left = middle + 1
        else:
            right = middle
    return nums[left]


print("  minimum of rotated:", find_minimum_rotated(rotated))

print("\n" + "=" * 60)
print("4. bisect: do not hand-roll it in production code")
print("=" * 60)
sorted_scores = [45, 52, 61, 67, 71, 78, 84, 90, 95]
print("  scores:", sorted_scores)
for score in [70, 45, 95, 100]:
    position = bisect.bisect_left(sorted_scores, score)
    print(f"    insert {score:>3} at index {position} (rank {position + 1})")
bisect.insort(sorted_scores, 70)
print("  after insort(70):", sorted_scores)

print("  version lookup (a real use): grades = [60, 70, 80, 90]")
grades = [60, 70, 80, 90]
for mark in [59, 60, 75, 91]:
    grade_index = bisect.bisect_right(grades, mark)
    print(f"    mark {mark:>3} -> grade index {grade_index}")

print("\n" + "=" * 60)
print("5. Binary search on the ANSWER (monotonic predicate)")
print("=" * 60)


def sqrt_binary(x, precision=1e-6):
    """Integer-free binary search on a real interval."""
    if x < 0:
        raise ValueError("no real square root of a negative number")
    if x < 1:
        left, right = x, 1
    else:
        left, right = 0, x
    while right - left > precision:
        middle = (left + right) / 2
        if middle * middle < x:
            left = middle
        else:
            right = middle
    return (left + right) / 2


print("  sqrt_binary(2)  =", round(sqrt_binary(2), 6), "| math.sqrt(2) =", round(2 ** 0.5, 6))
print("  sqrt_binary(49) =", round(sqrt_binary(49), 4))


def min_capacity_to_ship(weights, days):
    """Classic answer-space problem. Find the smallest daily capacity that ships
    everything within `days` days.

    The predicate "can we ship with capacity C?" is monotonic: if C works, any
    bigger capacity works too — so binary search on C.
    """
    def can_ship(capacity):
        used_days = 1
        load = 0
        for weight in weights:
            if load + weight > capacity:
                used_days += 1
                load = 0
            load += weight
        return used_days <= days

    low, high = max(weights), sum(weights)      # capacity must be at least the heaviest item
    while low < high:
        middle = (low + high) // 2
        if can_ship(middle):
            high = middle                       # works: try smaller
        else:
            low = middle + 1                    # fails: need bigger
    return low


weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for days in [5, 3, 1]:
    print(f"  weights {weights} in {days} day(s) -> min capacity {min_capacity_to_ship(weights, days)}")


def min_eating_speed(piles, hours):
    """Koko eats bananas: smallest speed that clears all piles within `hours`."""
    import math

    def hours_needed(speed):
        return sum(math.ceil(pile / speed) for pile in piles)

    low, high = 1, max(piles)
    while low < high:
        middle = (low + high) // 2
        if hours_needed(middle) <= hours:
            high = middle
        else:
            low = middle + 1
    return low


piles = [3, 6, 7, 11]
for hours in [8, 6, 4]:
    print(f"  piles {piles} in {hours} hours -> min speed {min_eating_speed(piles, hours)}")

print("\n" + "=" * 60)
print("6. Searching in a 2D sorted matrix (staircase walk)")
print("=" * 60)


def search_matrix(matrix, target):
    """Rows and columns are sorted. Start top-right: O(rows + cols)."""
    if not matrix or not matrix[0]:
        return False
    row, column = 0, len(matrix[0]) - 1
    while row < len(matrix) and column >= 0:
        value = matrix[row][column]
        if value == target:
            return True
        if value > target:
            column -= 1                 # everything below is bigger
        else:
            row += 1                    # everything left is smaller
    return False


grid = [
    [1, 4, 7, 11],
    [2, 5, 8, 12],
    [3, 6, 9, 16],
    [10, 13, 14, 17],
]
for target in [5, 17, 1, 15]:
    print(f"  search_matrix(grid, {target:>2}) = {search_matrix(grid, target)}")


def search_matrix_binary(matrix, target):
    """Treat the matrix as a flattened sorted list: O(log(rows * cols))."""
    if not matrix or not matrix[0]:
        return False
    rows, columns = len(matrix), len(matrix[0])
    low, high = 0, rows * columns - 1
    while low <= high:
        middle = (low + high) // 2
        value = matrix[middle // columns][middle % columns]
        if value == target:
            return True
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return False


print("  flattened binary search on the same grid:",
      search_matrix_binary(grid, 15), search_matrix_binary(grid, 9))

print("\n" + "=" * 60)
print("7. Why O(log n) is dramatic (measured)")
print("=" * 60)
for size in [1_000, 100_000, 10_000_000]:
    ordered = list(range(size))
    target = size - 1
    steps = 0
    left, right = 0, len(ordered) - 1
    while left <= right:
        steps += 1
        middle = (left + right) // 2
        if ordered[middle] == target:
            break
        if ordered[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    start = time.perf_counter()
    _ = target in ordered                # linear scan
    linear_ms = (time.perf_counter() - start) * 1000
    print(f"  n = {size:>10,}: binary search took {steps:>2} steps, "
          f"while `in` took {linear_ms:7.3f} ms")

print("\n" + "=" * 60)
print("8. Binary search checklist")
print("=" * 60)
print("""  1. Is the data sorted (or is the predicate monotonic)?  If no -> sort first.
  2. Decide the invariant:
        left, right = 0, n - 1   with `while left <= right`   -> inclusive bounds
        left, right = 0, n       with `while left <  right`   -> half-open bounds
  3. Move BOTH pointers every iteration (mid +/- 1).
  4. Return the boundary you actually need: index? count? insertion point?
  5. Complexity: O(log n) time, O(1) space (O(log n) stack if recursive).
  6. In real code, prefer bisect — it is C, and it is already correct.""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `count_occurrences(nums, target)` -> how many times target appears in a
#    sorted list, in O(log n) (upper_bound - lower_bound).
# 2. `find_insert_position(nums, target)` -> where to insert to keep it sorted.
# 3. `first_bad_version(n, is_bad)` -> the first bad version with the fewest
#    calls (binary search on a predicate).
# 4. `is_perfect_square(n)` -> True/False using binary search on 1..n.
# 5. `split_array_largest_sum(nums, k)` -> minimise the largest subarray sum
#    when splitting into k parts (answer-space binary search).
# 6. `kth_smallest_in_two_sorted(a, b, k)` -> O(log(min(n, m))) if you are
#    feeling brave; O(n + m) with two pointers is a fine first attempt.
# 7. `search_2d_matrix_binary` — write it from memory, then compare with the
#    staircase version's complexity.
# 8. `min_speed_for_piles(piles, hours)` — rewrite min_eating_speed without
#    looking, and state its complexity.
print()
print("Now run: python3 dsa/dsa_06_recursion.py")
