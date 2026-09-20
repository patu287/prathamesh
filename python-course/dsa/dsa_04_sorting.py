"""
DSA 04 · Sorting algorithms (and when you should just call .sort())

Setting the record straight first
---------------------------------
In real Python you write `a.sort(key=...)` and you are done: CPython's Timsort
is written in C, is stable, and runs at O(n log n) with a tiny constant. This
lesson is *not* "never write a sort". It is:

1. you must understand how sorting works (interviews, and knowing why some
   problems get easier once data is ordered);
2. you need to recognise the O(n log n) "divide and conquer" pattern (merge
   sort → dsa_06 recursion → dsa_12 DP);
3. sometimes you need a *specialised* sort (counting sort for small ranges is
   O(n) and beats the built-in).

The algorithms
--------------
| Algorithm      | Best     | Average  | Worst    | Space  | Stable |
|----------------|----------|----------|----------|--------|--------|
| Bubble         | O(n)     | O(n²)    | O(n²)    | O(1)   | yes    |
| Selection      | O(n²)    | O(n²)    | O(n²)    | O(1)   | no     |
| Insertion      | O(n)     | O(n²)    | O(n²)    | O(1)   | yes    |
| Merge          | O(n log n)| O(n log n)| O(n log n)| O(n) | yes    |
| Quick          | O(n log n)| O(n log n)| O(n²) ⚠  | O(log n)| no   |
| Counting       | O(n + k) | O(n + k) | O(n + k) | O(n+k) | yes    |

* **stable** = equal elements keep their relative order (matters when sorting
  by several keys, or sorting objects you already ordered by something else).
* Insertion sort is genuinely the best choice for tiny or nearly-sorted inputs;
  real libraries switch to it for small runs (Timsort does exactly this).
* Quick sort's worst case happens with already-sorted input and a bad pivot —
  fixed in practice by randomising the pivot.

Why "sort first" solves so many problems
----------------------------------------
Sorted data lets you use two pointers (O(n)), binary search (O(log n)) and
greedy reasoning ("take the smallest first"). When you are stuck on a problem,
ask: *does knowing the order make this easy?* If yes, O(n log n) sorting is a
bargain.

Counting/selection problems on small ranges
-------------------------------------------
Counting sort (and bucket sort) are O(n + k) but need a bounded key range.
The "find the k-th largest" family is better served by a heap (dsa_10) or
quickselect (below).
"""

import random
import time
import bisect

print("=" * 60)
print("1. Bubble sort — the teaching sort")
print("=" * 60)


def bubble_sort(items):
    """Repeatedly swap neighbours that are out of order. O(n^2), stable.

    The `swapped` flag makes the best case O(n) (already sorted input).
    """
    data = items[:]
    n = len(data)
    for pass_number in range(n - 1):
        swapped = False
        for i in range(n - 1 - pass_number):        # the tail is already sorted
            if data[i] > data[i + 1]:
                data[i], data[i + 1] = data[i + 1], data[i]
                swapped = True
        if not swapped:
            break                                    # nothing moved => sorted
    return data


print("  bubble_sort([5,1,4,2,8]) :", bubble_sort([5, 1, 4, 2, 8]))
print("  already sorted (fast)    :", bubble_sort([1, 2, 3, 4, 5]))

print("\n" + "=" * 60)
print("2. Selection sort — minimum swaps")
print("=" * 60)


def selection_sort(items):
    """Find the smallest, put it first, repeat. O(n^2) always, NOT stable."""
    data = items[:]
    for i in range(len(data)):
        smallest = i
        for j in range(i + 1, len(data)):
            if data[j] < data[smallest]:
                smallest = j
        data[i], data[smallest] = data[smallest], data[i]
    return data


print("  selection_sort([5,1,4,2,8]):", selection_sort([5, 1, 4, 2, 8]))

print("\n" + "=" * 60)
print("3. Insertion sort — best for small/nearly-sorted data")
print("=" * 60)


def insertion_sort(items):
    """Insert each element into the sorted part on its left. O(n^2), stable."""
    data = items[:]
    for i in range(1, len(data)):
        current = data[i]
        j = i - 1
        while j >= 0 and data[j] > current:
            data[j + 1] = data[j]           # shift right to make room
            j -= 1
        data[j + 1] = current
    return data


print("  insertion_sort([5,1,4,2,8])  :", insertion_sort([5, 1, 4, 2, 8]))
print("  nearly sorted [1,2,3,5,4,6]  :", insertion_sort([1, 2, 3, 5, 4, 6]),
      " (close to O(n))")

print("\n" + "=" * 60)
print("4. Merge sort — divide and conquer, O(n log n) guaranteed")
print("=" * 60)


def merge(left, right):
    """Merge two SORTED lists into one sorted list. O(n + m)."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:         # `<=` keeps the sort stable
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])             # whatever is left over
    result.extend(right[j:])
    return result


def merge_sort(items):
    """Split in half, sort each half, merge. O(n log n) time, O(n) space."""
    if len(items) <= 1:                 # base case
        return items[:]
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    return merge(left, right)


print("  merge([1,3,5], [2,4,6])  :", merge([1, 3, 5], [2, 4, 6]))
print("  merge_sort([5,1,4,2,8,3]):", merge_sort([5, 1, 4, 2, 8, 3]))
print("  recursion depth is O(log n):", "log2(1_000_000) ≈ 20 levels")

print("\n" + "=" * 60)
print("5. Quick sort — fast in practice, O(n^2) worst case")
print("=" * 60)


def quick_sort(items):
    """Partition around a pivot, recurse on both sides. Average O(n log n).

    This is the readable version (it builds new lists). An in-place version
    swaps within a single list to save memory. Randomising the pivot avoids
    the O(n^2) worst case on already-sorted input.
    """
    if len(items) <= 1:
        return items[:]
    pivot = random.choice(items)                 # random pivot = safer
    smaller = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]     # grouping equals handles dupes
    larger = [x for x in items if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(larger)


print("  quick_sort([5,1,4,2,8,3,3]):", quick_sort([5, 1, 4, 2, 8, 3, 3]))


def quickselect(items, k):
    """The k-th smallest element in average O(n) — no full sort needed.

    This is the same partitioning idea as quick sort, but you only recurse into
    the side that contains k.
    """
    if not items:
        return None
    pivot = random.choice(items)
    smaller = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    larger = [x for x in items if x > pivot]
    if k <= len(smaller):
        return quickselect(smaller, k)
    if k <= len(smaller) + len(equal):
        return pivot
    return quickselect(larger, k - len(smaller) - len(equal))


numbers = [7, 1, 9, 4, 4, 2, 8]
for k in range(1, len(numbers) + 1):
    print(f"  {k}-th smallest of {numbers} = {quickselect(numbers, k)}")

print("\n" + "=" * 60)
print("6. Counting sort — O(n + k) when values are small integers")
print("=" * 60)


def counting_sort(items):
    """No comparisons at all: count occurrences, then rebuild. Stable version."""
    if not items:
        return []
    offset = min(items)                     # handles negatives too
    span = max(items) - offset + 1
    counts = [0] * span
    for value in items:
        counts[value - offset] += 1
    result = []
    for index, count in enumerate(counts):
        result.extend([index + offset] * count)
    return result


print("  counting_sort([4,2,2,8,3,3,1]):", counting_sort([4, 2, 2, 8, 3, 3, 1]))
print("  handles negatives             :", counting_sort([3, -1, 0, -1, 2]))


def sort_colors(nums):
    """Dutch-national-flag: sort 0s, 1s and 2s in ONE pass, O(1) space."""
    low = mid = 0
    high = len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
    return nums


print("  sort_colors([2,0,2,1,1,0]):", sort_colors([2, 0, 2, 1, 1, 0]))

print("\n" + "=" * 60)
print("7. Python's own sort: key, stability, and speed")
print("=" * 60)
students = [
    ("Ravi", 21, 88),
    ("Priya", 22, 95),
    ("Asha", 21, 95),
    ("Dev", 20, 70),
]
print("  sorted by score desc, name asc:",
      sorted(students, key=lambda s: (-s[2], s[0])))
print("  sorted by age, then score (stable chained sort):")
by_age = sorted(students, key=lambda s: s[1])
by_age_then_score = sorted(by_age, key=lambda s: -s[2])
print("   ", by_age_then_score)
print("  sort() is stable, so the tuple key version and chained version agree:",
      sorted(students, key=lambda s: (-s[2], s[1], s[0])) == by_age_then_score)

# custom objects sort via __lt__ (lesson 14), or `key=`
from dataclasses import dataclass


@dataclass(order=True)                # order=True generates <, <=, >, >=
class Priced:
    price: float
    name: str


products = [Priced(99.5, "shoes"), Priced(25.0, "socks"), Priced(99.5, "belt")]
print("  dataclass(order=True) sort:", products)
print("  sorted by name only       :", sorted(products, key=lambda p: p.name))

print("\n" + "=" * 60)
print("8. Benchmark: O(n^2) sorts vs O(n log n) vs built-in")
print("=" * 60)
random.seed(0)


def timed(func, data, repeats=1):
    start = time.perf_counter()
    for _ in range(repeats):
        func(data)
    return (time.perf_counter() - start) * 1000


print("  n = 1,000")
dataset = [random.randint(0, 1_000_000) for _ in range(1_000)]
print(f"    bubble     : {timed(bubble_sort, dataset):9.2f} ms")
print(f"    selection  : {timed(selection_sort, dataset):9.2f} ms")
print(f"    insertion  : {timed(insertion_sort, dataset):9.2f} ms")
print(f"    merge      : {timed(merge_sort, dataset):9.2f} ms")
print(f"    quick      : {timed(quick_sort, dataset):9.2f} ms")
print(f"    built-in   : {timed(sorted, dataset):9.2f} ms   <- written in C")

print("\n  n = 5,000 (bubble/selection/insertion would take ~25x longer — skipped)")
bigger = [random.randint(0, 1_000_000) for _ in range(5_000)]
print(f"    merge      : {timed(merge_sort, bigger):9.2f} ms")
print(f"    built-in   : {timed(sorted, bigger):9.2f} ms")

print("\n  correctness check:", sorted(dataset) == merge_sort(dataset) == quick_sort(dataset))

print("\n  insertion sort on NEARLY sorted data (its best case):")
nearly = list(range(5_000))
nearly[2500], nearly[2501] = nearly[2501], nearly[2500]
print(f"    insertion  : {timed(insertion_sort, nearly):9.2f} ms  (vs ~25x more for random)")
print(f"    merge      : {timed(merge_sort, nearly):9.2f} ms")

print("\n" + "=" * 60)
print("9. Sorting-based solutions to classic problems")
print("=" * 60)


def has_duplicates_sort(nums):
    """O(n log n) via sorting vs O(n) via a set (dsa_03)."""
    ordered = sorted(nums)
    return any(ordered[i] == ordered[i + 1] for i in range(len(ordered) - 1))


def three_sum(nums):
    """All unique triplets that sum to zero. O(n^2) after sorting."""
    nums = sorted(nums)
    triples = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue                              # skip duplicate anchors
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                triples.append((nums[i], nums[left], nums[right]))
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return triples


print("  has_duplicates_sort([1,2,3,2]):", has_duplicates_sort([1, 2, 3, 2]))
print("  three_sum([-1,0,1,2,-1,-4])   :", three_sum([-1, 0, 1, 2, -1, -4]))


def merge_intervals(intervals):
    """Merge overlapping intervals. Sort by start, then sweep. O(n log n)."""
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:                 # overlaps -> extend
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(pair) for pair in merged]


print("  merge_intervals([(1,3),(2,6),(8,10),(15,18)]) ->",
      merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)]))


def kth_largest_builtin(nums, k):
    """Simplest correct answer: sort descending and index. O(n log n)."""
    return sorted(nums, reverse=True)[k - 1]


def kth_largest_heap(nums, k):
    """Better for large n and small k: keep a heap of size k. O(n log k)."""
    import heapq
    return heapq.nlargest(k, nums)[-1]


print("  kth largest (k=2) of [3,2,1,5,6,4]:",
      kth_largest_builtin([3, 2, 1, 5, 6, 4], 2),
      "| heap version:", kth_largest_heap([3, 2, 1, 5, 6, 4], 2))

print("\n" + "=" * 60)
print("10. When sorting is the answer (checklist)")
print("=" * 60)
print("""  * "find duplicates / k-th / closest pair"        -> sort, then neighbours
  * "merge overlapping ranges"                     -> sort by start
  * "group / partition by a key"                   -> sort by key
  * "two-sum on unsorted data with O(1) extra space"-> sort + two pointers
  * "the smallest/largest k things"                -> heap (dsa_10), not sort
  * "count of values in a small range"             -> counting sort (O(n+k))
  * huge n with a bounded value range              -> counting/bucket, not O(n log n)""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `is_sorted_stable(pairs)` — prove to yourself that Python's sort is stable
#    by sorting [(a,1),(b,1),(c,0)] on the second element only.
# 2. Write `insertion_sort_desc(items)` and test it.
# 3. `merge_k_sorted(lists)` -> merge several sorted lists (loop merge, then
#    compare with heapq.merge).
# 4. `sort_by_frequency(nums)` -> values ordered by count desc, value asc.
# 5. `kth_smallest_quickselect(nums, k)` — wrap the quickselect above.
# 6. `find_median(nums)` without sorting the whole list (quickselect!).
# 7. `sort_string_case_insensitive(sentence)` -> words sorted ignoring case.
# 8. `sort_numbers_as_strings(nums)` -> [10, 2, 3] sorted as text gives
#    [10, 2, 3]. Why? Write it as a comment.
print()
print("Now run: python3 dsa/dsa_05_binary_search.py")
