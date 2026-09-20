"""
DSA 01 · Arrays & two pointers

An "array" in DSA = a Python `list`: a block of slots, each reachable in O(1)
time by index. Almost every problem starts here.

Golden facts
------------
* indexing is O(1); searching an unsorted list is O(n)
* appending is O(1) amortised; inserting/removing at the FRONT is O(n)
* slices copy: `a[i:j]` costs O(j-i) time AND memory
* sorting is O(n log n) and often the fastest way to unlock a neat solution

The three techniques in this file
---------------------------------
1. **One-pass accumulation** — max, min, sum, count while you walk.
2. **Two pointers** — one left, one right, moving toward each other. O(n), O(1)
   space. Works on sorted data or when you can reason about moving a pointer.
3. **Prefix sums** — preprocess once in O(n), then answer any range-sum query
   in O(1). Turns O(n) queries into O(1) queries.

Also in here: in-place reversal, rotation, in-place removal, Kadane's max
subarray (the famous one-pass dynamic programming warm-up).
"""

print("=" * 60)
print("1. One pass: min, max, sum, average, count")
print("=" * 60)

def summarise(nums):
    """All the basics in a single O(n) pass — no built-ins, so you see the logic."""
    total = 0
    smallest = float("inf")
    largest = float("-inf")
    even_count = 0
    for value in nums:
        total += value
        if value < smallest:
            smallest = value
        if value > largest:
            largest = value
        if value % 2 == 0:
            even_count += 1
    average = total / len(nums) if nums else 0
    return {"sum": total, "min": smallest, "max": largest,
            "average": round(average, 2), "evens": even_count}


data = [4, 9, 2, 9, 7, 4, 1]
print("  data      :", data)
print("  summarise :", summarise(data))
print("  built-ins :", {"sum": sum(data), "min": min(data), "max": max(data),
                        "len": len(data)})

print("\n" + "=" * 60)
print("2. Reverse in place (two pointers, O(n) time O(1) space)")
print("=" * 60)

def reverse_in_place(items):
    left, right = 0, len(items) - 1
    while left < right:
        items[left], items[right] = items[right], items[left]
        left += 1
        right -= 1
    return items


print("  reversed:", reverse_in_place([1, 2, 3, 4, 5]))
print("  reversed:", reverse_in_place([1, 2, 3, 4]))
print("  (Python's own: a[::-1] or a.reverse() — same effect, done in C)")

print("\n" + "=" * 60)
print("3. Rotate right by k (the three-reversal trick)")
print("=" * 60)

def rotate_right(nums, k):
    """[1,2,3,4,5], k=2 -> [4,5,1,2,3]. O(n) time, O(1) extra space."""
    n = len(nums)
    if n == 0:
        return nums
    k %= n                     # k may be larger than n — wrap it
    reverse_in_place(nums)
    reverse_in_place(nums[:k])     # careful: a slice is a COPY
    # That is the classic mistake, so do it properly with a helper:
    def reverse_range(items, start, end):
        while start < end:
            items[start], items[end] = items[end], items[start]
            start += 1
            end -= 1
    reverse_range(nums, 0, k - 1)
    reverse_range(nums, k, n - 1)
    return nums


print("  [1..5] rotated by 2 :", rotate_right([1, 2, 3, 4, 5], 2))
print("  [1..5] rotated by 7 :", rotate_right([1, 2, 3, 4, 5], 7), "(7 % 5 = 2)")
print("  [1..7] rotated by 3 :", rotate_right([1, 2, 3, 4, 5, 6, 7], 3))

print("\n" + "=" * 60)
print("4. Two pointers on sorted data: pair sum")
print("=" * 60)

def pair_with_sum(sorted_nums, target):
    """Return the pair (or None). O(n) time, O(1) space."""
    left, right = 0, len(sorted_nums) - 1
    while left < right:
        total = sorted_nums[left] + sorted_nums[right]
        if total == target:
            return sorted_nums[left], sorted_nums[right]
        if total < target:
            left += 1                # too small -> need a bigger value
        else:
            right -= 1               # too big -> need a smaller value
    return None


print("  [1,3,4,6,8,11] target 10 :", pair_with_sum([1, 3, 4, 6, 8, 11], 10))
print("  [1,3,4,6,8,11] target 14 :", pair_with_sum([1, 3, 4, 6, 8, 11], 14))
print("  [1,3,4,6,8,11] target 99 :", pair_with_sum([1, 3, 4, 6, 8, 11], 99))

print("\n" + "=" * 60)
print("5. Two pointers on UNSORTED data: remove duplicates / move zeroes")
print("=" * 60)

def dedupe_sorted(nums):
    """Given a SORTED list, remove duplicates in place. Returns the new length."""
    if not nums:
        return 0
    write = 1                              # next slot to write into
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


values = [1, 1, 2, 3, 3, 3, 4]
length = dedupe_sorted(values)
print("  dedupe_sorted ->", values[:length], "| new length:", length)

def move_zeroes(nums):
    """[0,1,0,3,12] -> [1,3,12,0,0]. Stable, in place, O(n)."""
    write = 0
    for value in nums:
        if value != 0:
            nums[write] = value
            write += 1
    for index in range(write, len(nums)):
        nums[index] = 0
    return nums


print("  move_zeroes   ->", move_zeroes([0, 1, 0, 3, 12]))
print("  move_zeroes   ->", move_zeroes([0, 0, 1]))

print("\n" + "=" * 60)
print("6. Prefix sums: O(1) range-sum queries")
print("=" * 60)

def build_prefix_sums(nums):
    """prefix[i] = sum(nums[:i]) so prefix[0] = 0 and prefix[n] = total."""
    prefix = [0] * (len(nums) + 1)
    running = 0
    for index, value in enumerate(nums):
        running += value
        prefix[index + 1] = running
    return prefix


def range_sum(prefix, start, end):
    """Sum of nums[start:end] — half-open interval, like slicing."""
    return prefix[end] - prefix[start]


arr = [5, 2, 8, 1, 9, 3]
prefix = build_prefix_sums(arr)
print("  arr              :", arr)
print("  prefix sums      :", prefix)
print("  sum(2:5) = 8+1+9 :", range_sum(prefix, 2, 5))
print("  sum(0:6)         :", range_sum(prefix, 0, 6))
print("  the naive way    :", sum(arr[2:5]), " <- same, but O(n) every query")


def subarray_sum_equals(nums, target):
    """Count subarrays with sum == target using a prefix-sum hash map. O(n)."""
    counts = {0: 1}                 # a prefix sum of 0 occurred once (the empty prefix)
    running = 0
    found = 0
    for value in nums:
        running += value
        found += counts.get(running - target, 0)   # how many prefixes make the rest
        counts[running] = counts.get(running, 0) + 1
    return found


print("  subarrays summing to 7 in [1,2,3,4,5,1,1] :", subarray_sum_equals([1, 2, 3, 4, 5, 1, 1], 7))

print("\n" + "=" * 60)
print("7. Kadane's algorithm: maximum subarray sum (one pass!)")
print("=" * 60)

def max_subarray_sum(nums):
    """Handle negatives too. O(n) time, O(1) space — classic DP in disguise."""
    best_ending_here = nums[0]
    best_so_far = nums[0]
    start = end = temp_start = 0
    for index in range(1, len(nums)):
        if nums[index] > best_ending_here + nums[index]:
            best_ending_here = nums[index]       # start fresh here
            temp_start = index
        else:
            best_ending_here += nums[index]      # extend the current run
        if best_ending_here > best_so_far:
            best_so_far = best_ending_here
            start, end = temp_start, index
    return best_so_far, nums[start:end + 1]


for nums in [[-2, 1, -3, 4, -1, 2, 1, -5, 4], [1, 2, 3, 4], [-5, -2, -9], [7]]:
    best, segment = max_subarray_sum(nums)
    print(f"  {str(nums):<32} -> best {best:>3}  segment {segment}")

print("\n" + "=" * 60)
print("8. In-place removal (the two-pointer trick with a write index)")
print("=" * 60)

def remove_value(nums, target):
    """Remove every occurrence of target in place; return the new length."""
    write = 0
    for value in nums:
        if value != target:
            nums[write] = value
            write += 1
    return write


values = [3, 2, 2, 3, 4, 3, 5]
length = remove_value(values, 3)
print("  remove 3 from [3,2,2,3,4,3,5] ->", values[:length], "| new length:", length)

print("\n" + "=" * 60)
print("9. Sliding window preview (fixed size)")
print("=" * 60)

def max_sum_window(nums, k):
    """Maximum sum of any k consecutive elements. O(n), not O(n*k)."""
    if k > len(nums) or k <= 0:
        return None
    window = sum(nums[:k])                  # first window: O(k)
    best = window
    for index in range(k, len(nums)):
        window += nums[index] - nums[index - k]     # slide: add one, drop one
        best = max(best, window)
    return best


series = [2, 1, 5, 1, 3, 2]
for k in [1, 2, 3, 4]:
    print(f"  max sum of {k} consecutive in {series} = {max_sum_window(series, k)}")

print("\n" + "=" * 60)
print("10. Complexity summary of these techniques")
print("=" * 60)
print("""  one-pass accumulation ............ O(n) time,      O(1) space
  two pointers (sorted) ............ O(n) time,      O(1) space
  prefix sums ...................... O(n) build, then O(1) per query, O(n) space
  sliding window (fixed k) ......... O(n) time,      O(1) space
  Kadane's ......................... O(n) time,      O(1) space
  sort + two pointers .............. O(n log n) time
  brute force pairs ................ O(n^2)  <- usually avoidable""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `second_largest(nums)` -> the second largest distinct value, one pass.
# 2. `is_sorted(nums)` -> True/False, one pass, no sorted().
# 3. `rotate_left(nums, k)` using the reversal trick.
# 4. `pair_with_sum_unsorted(nums, target)` -> indices using a dict (O(n)).
# 5. `largest_three(nums)` -> the three biggest values, one pass, no sorting.
# 6. `equilibrium_index(nums)` -> an index where sum(left) == sum(right), using
#    prefix sums (bonus: do it with O(1) extra space).
# 7. `merge_sorted(a, b)` -> one sorted list from two sorted lists, O(n+m),
#    without sorted() (this is the merge step of merge sort — dsa_04).
# 8. `longest_zero_sum_subarray(nums)` -> length of the longest subarray with
#    sum 0 (prefix sums + dict of first-seen index).
print()
print("Now run: python3 dsa/dsa_02_strings.py")
