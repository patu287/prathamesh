"""
DSA 10 · Heaps & priority queues

A heap is a binary tree stored in a flat list where every parent is <= its
children (min-heap). It gives you:

    peek the smallest ....... O(1)
    push (insert) ........... O(log n)
    pop the smallest ........ O(log n)
    build from n items ...... O(n)   (heapify)

It does NOT keep the whole list sorted — only enough order to answer
"what is the smallest right now?". That laziness is exactly why it beats
sorting when you only need the extremes.

Python's heap in one line
-------------------------
    import heapq
    h = []
    heapq.heappush(h, 5)          # also: heapq.heapify(list) to build from a list
    heapq.heappop(h)              # smallest
    h[0]                          # peek (no pop)

Traps:
* `heapq` is a MIN-heap only. For a max-heap, push NEGATED values.
* It operates on a plain list — do not use list methods like `sort()` on it.
* Tuples compare element by element, so `(priority, item)` works as long as
  the items are comparable. If they are not, add a counter to break ties:
  `(priority, counter, item)`.
* If you want a custom "smallest first" rule, push tuples with a key first.

When a heap is the right tool
-----------------------------
* "the smallest/largest k elements" (better than sorting when k << n)
* "the next item to process is the smallest/largest" (schedulers, Dijkstra)
* streaming data: you cannot sort what you have not seen yet
* merging k sorted lists
* running median of a stream (two heaps)
* top-k frequent elements, task scheduling, meeting rooms

Alternative: `sorted(items)[:k]` is fine for small inputs, and
`heapq.nsmallest(k, items)` / `nlargest(k, items)` are implemented for you.
"""

import heapq
import random
import time
from collections import Counter


def show(heap):
    """Print a heap as both a list and its sorted order (for teaching)."""
    return f"list={heap} sorted={sorted(heap)}"


print("=" * 60)
print("1. The heapq API")
print("=" * 60)
heap = []
for value in [5, 1, 9, 3, 7]:
    heapq.heappush(heap, value)
    print(f"  push({value}) -> {show(heap)}")
print("  peek (heap[0]):", heap[0], " (the smallest, O(1))")
print("  popped in order:")
while heap:
    print("   ", heapq.heappop(heap), end="")
print()

print("\n  building from a list is O(n), not O(n log n):")
raw = [9, 4, 7, 1, 8, 2]
heapq.heapify(raw)
print("   ", raw, " <- now a valid heap (note: not sorted!)")

print("\n" + "=" * 60)
print("2. Max-heap by negating values")
print("=" * 60)
max_heap = []
for value in [5, 1, 9, 3]:
    heapq.heappush(max_heap, -value)
print("  internal list (negated):", max_heap)
print("  popping gives them largest-first:")
while max_heap:
    print("   ", -heapq.heappop(max_heap), end="")
print()

print("\n" + "=" * 60)
print("3. k smallest / k largest")
print("=" * 60)
random.seed(0)
numbers = [random.randint(0, 1000) for _ in range(20)]
print("  data        :", numbers)
print("  nsmallest(3):", heapq.nsmallest(3, numbers))
print("  nlargest(3) :", heapq.nlargest(3, numbers))
print("  sorted[:3]  :", sorted(numbers)[:3], " (same answer, but O(n log n))")


def kth_smallest(nums, k):
    """Min-heap version: pop k times. O(n + k log n)."""
    heap = nums[:]
    heapq.heapify(heap)
    for _ in range(k - 1):
        heapq.heappop(heap)
    return heap[0]


def kth_largest(nums, k):
    """Keep a heap of the k largest: O(n log k) — the right answer for streams."""
    return heapq.nlargest(k, nums)[-1]


print("  3rd smallest:", kth_smallest(numbers, 3), "| 3rd largest:", kth_largest(numbers, 3))

print("\n  Why n log k beats n log n when k is small:")
big = [random.randint(0, 10_000_000) for _ in range(1_000_000)]

def timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    return result, (time.perf_counter() - start) * 1000

_, sort_ms = timed(lambda: sorted(big)[:10])
_, heap_ms = timed(lambda: heapq.nsmallest(10, big))
print(f"    sorted(big)[:10]      : {sort_ms:8.2f} ms")
print(f"    heapq.nsmallest(10,..): {heap_ms:8.2f} ms   <- about {sort_ms / heap_ms:.0f}x faster")

print("\n" + "=" * 60)
print("4. Heapsort (sorting via a heap, in place)")
print("=" * 60)


def heapsort(items):
    """O(n log n) time, O(1) extra space — no comparisons via list.sort()."""
    heap = items[:]
    heapq.heapify(heap)                       # O(n)
    return [heapq.heappop(heap) for _ in range(len(heap))]   # n pops of O(log n)


sample = [random.randint(0, 100) for _ in range(12)]
print("  original :", sample)
print("  heapsort :", heapsort(sample))
print("  correct  :", heapsort(sample) == sorted(sample))

print("\n" + "=" * 60)
print("5. Merging k sorted lists")
print("=" * 60)


def merge_k_sorted(lists):
    """Push the first element of each list, pop the smallest, push its successor."""
    heap = []
    for list_index, items in enumerate(lists):
        if items:
            heapq.heappush(heap, (items[0], list_index, 0))     # (value, which list, index)
    result = []
    while heap:
        value, list_index, element_index = heapq.heappop(heap)
        result.append(value)
        if element_index + 1 < len(lists[list_index]):
            next_value = lists[list_index][element_index + 1]
            heapq.heappush(heap, (next_value, list_index, element_index + 1))
    return result


for lists in ([[1, 4, 7], [2, 5, 8], [3, 6, 9]], [[], [1], [0, 2]]):
    merged = merge_k_sorted(lists)
    expected = sorted(value for group in lists for value in group)
    print(f"  merge {str(lists):<30} -> {merged}  correct={merged == expected}")
print("  Complexity: O(N log k) where N = total items, k = number of lists.")

print("\n" + "=" * 60)
print("6. Top-k frequent elements (Counter + heap)")
print("=" * 60)


def top_k_frequent(items, k):
    """O(n log k) with a heap, or O(n) with most_common's internal counting."""
    counts = Counter(items)
    return heapq.nlargest(k, counts.items(), key=lambda pair: pair[1])


text = "the quick brown fox jumps over the lazy dog the fox the dog"
words = text.split()
print("  word counts :", dict(Counter(words).most_common(4)))
print("  top 3        :", top_k_frequent(words, 3))
print("  Counter's own:", Counter(words).most_common(3), " <- simplest")

numbers = [1, 1, 1, 2, 2, 3, 3, 3, 3, 4]
print("  top 2 in numbers:", top_k_frequent(numbers, 2))


def k_closest_points(points, k):
    """The k points nearest the origin — a heap over computed distances."""
    heap = [(x * x + y * y, (x, y)) for x, y in points]
    return [point for _, point in heapq.nsmallest(k, heap)]


points = [(1, 3), (-2, 2), (5, 8), (0, 1), (3, 3)]
print("  3 closest points to the origin:", k_closest_points(points, 3))

print("\n" + "=" * 60)
print("7. Running median with two heaps (a beautiful pattern)")
print("=" * 60)


class MedianFinder:
    """Keep the lower half in a max-heap and the upper half in a min-heap.

    The two heaps stay balanced within one element, so the median is always
    available at a heap top. O(log n) to add, O(1) to query.
    """

    def __init__(self):
        self.lower = []      # max-heap (negated): the smaller half
        self.upper = []      # min-heap: the bigger half

    def add(self, value):
        heapq.heappush(self.lower, -value)
        # make sure everything in lower <= everything in upper
        if self.lower and self.upper and -self.lower[0] > self.upper[0]:
            heapq.heappush(self.upper, -heapq.heappop(self.lower))
        # keep the sizes within one
        if len(self.lower) > len(self.upper) + 1:
            heapq.heappush(self.upper, -heapq.heappop(self.lower))
        elif len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))

    def median(self):
        if not self.lower and not self.upper:
            return None
        if len(self.lower) == len(self.upper):
            return (-self.lower[0] + self.upper[0]) / 2
        return float(-self.lower[0])


finder = MedianFinder()
stream = [5, 15, 1, 3, 8, 7, 9, 10, 6, 11, 4]
print("  stream     :", stream)
running = []
for value in stream:
    finder.add(value)
    running.append(finder.median())
print("  medians    :", running)
print("  after all  :", finder.median(), "| sorted middle:",
      sorted(stream)[len(stream) // 2] if len(stream) % 2 else
      (sorted(stream)[len(stream) // 2 - 1] + sorted(stream)[len(stream) // 2]) / 2)

print("\n" + "=" * 60)
print("8. Scheduling with a priority queue")
print("=" * 60)


def schedule_tasks(tasks):
    """tasks = [(name, priority)]; smaller priority runs first."""
    heap = [(priority, index, name) for index, (name, priority) in enumerate(tasks)]
    heapq.heapify(heap)
    order = []
    while heap:
        priority, _, name = heapq.heappop(heap)
        order.append((name, priority))
    return order


tasks = [("backup", 5), ("send email", 1), ("render video", 4), ("fix bug", 0), ("chat", 3)]
print("  task queue (priority order):")
for name, priority in schedule_tasks(tasks):
    print(f"    [P{priority}] {name}")


def minimum_meeting_rooms(intervals):
    """How many rooms do we need? Sort by start, keep a min-heap of end times."""
    if not intervals:
        return 0
    intervals = sorted(intervals)
    rooms = []                            # end times of ongoing meetings
    for start, end in intervals:
        if rooms and rooms[0] <= start:
            heapq.heappop(rooms)          # a room freed up
        heapq.heappush(rooms, end)
    return len(rooms), intervals


for meetings in ([(0, 30), (5, 10), (15, 20)], [(7, 10), (2, 4)]):
    count, sorted_intervals = minimum_meeting_rooms(meetings)
    print(f"  meetings {sorted_intervals} -> {count} room(s)")


def last_stone_weight(stones):
    """Smash the two heaviest together until one remains (a max-heap problem)."""
    heap = [-stone for stone in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        first = -heapq.heappop(heap)
        second = -heapq.heappop(heap)
        if first != second:
            heapq.heappush(heap, -(first - second))
    return -heap[0] if heap else 0


print("  last stone weight for [2,7,4,1,8,1]:", last_stone_weight([2, 7, 4, 1, 8, 1]))

print("\n" + "=" * 60)
print("9. Custom ordering (tuples, dataclasses, tie-breakers)")
print("=" * 60)


class Patient:
    """Heaps compare by < so a dataclass with order=True works directly."""

    def __init__(self, name, severity):
        self.name = name
        self.severity = severity          # smaller = more urgent

    def __lt__(self, other):              # heapq only needs __lt__
        return self.severity < other.severity

    def __repr__(self):
        return f"{self.name}(sev={self.severity})"


patients = [Patient("Ravi", 3), Patient("Priya", 1), Patient("Asha", 2)]
heap = patients[:]
heapq.heapify(heap)
print("  treated in order:", [heapq.heappop(heap).name for _ in range(len(heap))])

# tie-breaking with a counter when the payload is not comparable
counter = 0


def push_tiebroken(heap, priority, payload):
    global counter
    counter += 1
    heapq.heappush(heap, (priority, counter, payload))


heap = []
for priority, payload in [(1, {"task": "a"}), (1, {"task": "b"}), (0, {"task": "c"})]:
    push_tiebroken(heap, priority, payload)
order = []
while heap:
    priority, _, payload = heapq.heappop(heap)
    order.append((priority, payload["task"]))
print("  tie-broken pop order:", order,
      " (equal priorities come out in insertion order, thanks to the counter)")

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  peek min ..................... O(1)
  push / pop ................... O(log n)
  heapify a list of n .......... O(n)      (not O(n log n)!)
  n pops of a heap ............. O(n log n)  == heapsort
  nsmallest / nlargest(k) ...... O(n log k)
  building a heap from a stream  O(n log n)
  memory ....................... O(n) — it IS a list
  ⚠  searching a heap for an arbitrary value is O(n): heaps are not maps.""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `kth_largest_stream(nums, k)` — design a class that supports add() and
#    returns the k-th largest at any time using a heap of size k.
# 2. `merge_k_sorted` — rewrite it from memory in about 10 lines.
# 3. `top_k_frequent(words, k)` — handle ties alphabetically.
# 4. `MedianFinder` — extend it with a `remove(value)` method (hard: heaps do
#    not support deletion; try lazy deletion with a Counter of removed values).
# 5. `reorganize_string(s)` — rearrange so no two adjacent characters are equal
#    (max-heap by remaining count).
# 6. `task_scheduler(tasks, cooldown)` — minimum time with a cooldown between
#    identical tasks (heap + queue).
# 7. `minimum_meeting_rooms` — write it again without looking, and state the
#    complexity in terms of the number of meetings n.
# 8. `find_k_pairs_smallest(nums1, nums2, k)` — use a heap of index pairs.
print()
print("Now run: python3 dsa/dsa_11_graphs.py")
