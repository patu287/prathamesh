"""
LESSON 16 · Big-O & writing fast Python

Big-O is how we talk about how code slows down as the input grows. You do not
need the maths to be useful — you need to *recognise shapes* and fix the bad
ones. This is the last lesson before the DSA topics, and it is the one that
makes the DSA topics make sense.

# 1. The idea

We count the number of basic operations as a function of n = input size, then
throw away constants and small terms.

    O(1)        constant  — same cost no matter how big n is
    O(log n)    halving   — binary search, balanced tree walk
    O(n)        linear    — one pass over the data
    O(n log n)  sorting   — the best possible for comparison-based sorting
    O(n²)       quadratic — nested loops over the same data
    O(2ⁿ)       exponential — every subset (naive recursion)
    O(n!)       factorial — every permutation (brute-force TSP)

Growth at n = 1000:

    O(1)         1 operation
    O(log n)     ~10
    O(n)         1,000
    O(n log n)   ~10,000
    O(n²)        1,000,000          <- 1 million: still OK
    O(2ⁿ)        10^301            <- the universe ends first

Rule of thumb for interviews (Python does ~10⁷–10⁸ simple operations/second):

    n ≤ 20        exponential / factorial is acceptable
    n ≤ 500       O(n²) or O(n³) is fine
    n ≤ 10⁶       you need O(n) or O(n log n)
    n ≥ 10⁸       O(n) only, and with small constants

So: **look at n first, then pick the algorithm.** A "correct" O(n²) solution on
n = 10⁵ is a wrong answer because it will time out.

# 2. Reading code and naming its cost

    for x in items:                     # n iterations -> O(n)
        print(x)

    for x in items:                     # n * n -> O(n²)
        for y in items:
            print(x, y)

    for x in items:                     # n + n -> O(n)
        ...
    for y in items:
        ...

    # If the loop variable is halved/doubled, it is logarithmic:
    while n > 1:                        # O(log n)
        n //= 2

    # Loop over a *shrinking* range:  n + (n-1) + ... + 1 = n(n+1)/2 -> O(n²)

    for i in range(len(a)):             # → use a set and this becomes O(n)
        if target in a[i:]:             # `in` on a list is O(n)!

How to analyse a block:
1. Count the work per element.
2. Multiply by how many times it happens (loops multiply).
3. Add sequential blocks and keep only the biggest term.
4. Ignore constant factors: O(2n) = O(n), O(n/2) = O(n).

# 3. Amortised cost (why `list.append` is "free")

Occasionally an append needs to grow the array (copy n elements). Doubling the
capacity means it happens rarely enough that the *average* per append is O(1).
That is "amortised O(1)". Same story for dict inserts.

`list.insert(0, x)` and `list.pop(0)`, on the other hand, are O(n) **every**
time because everything shifts. Use `collections.deque` or two pointers.

# 4. Cost table for Python operations (average case)

| Operation                         | Cost       |
|-----------------------------------|------------|
| `a[i]`, `a[i] = x`                | O(1)       |
| `a.append(x)`, `a.pop()`          | O(1)*      |
| `a.insert(0, x)`, `a.pop(0)`      | O(n)       |
| `x in a` (list)                   | O(n)       |
| `a[i:j]` (slice/copy)             | O(j - i)   |
| `sorted(a)`, `a.sort()`           | O(n log n) |
| `min(a)`, `max(a)`, `sum(a)`      | O(n)       |
| `len(a)`                          | O(1)       |
| `d[k]`, `d[k] = v`, `k in d`      | O(1)*      |
| `del d[k]`                        | O(1)*      |
| `s in d.values()`                 | O(n)       |
| `x in s` (set)                    | O(1)*      |
| `s.add(x)`, `s.discard(x)`        | O(1)*      |
| `heappush` / `heappop`            | O(log n)   |
| `heap[0]` (peek)                  | O(1)       |
| `bisect_left` on sorted list      | O(log n)   |
| `deque.append/popleft`            | O(1)       |
| string `+` in a loop              | O(n²) ⚠    |
| `"".join(parts)`                  | O(total)   |

\* average; worst case O(n) for hash collisions.

# 5. Space complexity

We also count extra memory used:

    a = [0] * n                     O(n)
    a = input[:]                    O(n)  (a copy!)
    counts = Counter(items)         O(k)  (k = distinct items)
    recursion depth d               O(d)  (the call stack costs memory too!)
    generator instead of a list     O(1)  ← lesson 12

Recursion depth matters: `sys.getrecursionlimit()` defaults to ~1000. Recursive
DFS on a path graph of 10⁵ nodes will crash with RecursionError — rewrite it
iteratively with an explicit stack (dsa_11).

# 6. The five fixes that solve most "too slow" problems

1. **Nested loops over the same data → use a dict/set** (O(n²) → O(n)). This is
   *the* most common interview optimisation.
2. **Repeated membership tests on a list → build a set once.**
3. **Repeated min/max/sum inside a loop → accumulate as you go.**
4. **Sorting inside a loop → sort once, then scan** (O(n² log n) → O(n log n)).
5. **String concatenation in a loop → collect parts and `"".join(parts)`.**
   (CPython optimises some `+=` on strings, but do not rely on it.)

# 7. Measuring, not guessing

    time.perf_counter()          # wall clock, nanoseconds resolution
    python3 -m timeit "code"     # micro-benchmarks, repeatable
    python3 -m cProfile -s cumtime script.py     # where the time actually goes

Always measure before optimising. Guesses about performance are usually wrong.
"""

import random
import sys
import time
from collections import Counter, deque


def benchmark(label, func, *args):
    """Run func once and report the time."""
    start = time.perf_counter()
    result = func(*args)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  {label:<38} {elapsed:9.3f} ms")
    return result


print("=" * 60)
print("1. Seeing the growth rates")
print("=" * 60)
print("  n      O(1)  O(log n)   O(n)      O(n log n)     O(n^2)")
for n in [10, 100, 1_000, 10_000]:
    import math
    print(f"  {n:<6} {1:<5} {math.log2(n):<9.1f} {n:<9,} {n * math.log2(n):<13,.0f} {n ** 2:,.0f}")

print("\n" + "=" * 60)
print("2. Measuring real functions (n = 20,000)")
print("=" * 60)
n = 20_000
data = list(range(n))
random.seed(0)
random.shuffle(data)
target = n - 1
sorted_data = sorted(data)

# O(1) — indexing and appending
benchmark("a[i]  (O(1))", lambda: data[n // 2])
# O(log n) — bisect
import bisect
benchmark("bisect_left on sorted (O(log n))", lambda: bisect.bisect_left(sorted_data, target))
# O(n) — one pass
benchmark("sum(data) (O(n))", lambda: sum(data))
# O(n) — set membership
benchmark("target in set(data) (O(1))", lambda: target in set(data))
# O(n) — list membership (worst case)
benchmark("target in data (O(n))", lambda: target in data)
# O(n log n) — sorting
benchmark("sorted(data) (O(n log n))", lambda: sorted(data))
# O(n^2) — nested loops (scaled down so it terminates!)
m = 1_500
benchmark(f"nested loops, n={m} (O(n^2))",
          lambda: sum(1 for i in range(m) for j in range(m) if i < j))

print("\n" + "=" * 60)
print("3. The nested-loop trap and its fix")
print("=" * 60)


def has_pair_slow(nums, target):
    """O(n^2): for each element, walk the rest."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False


def has_pair_fast(nums, target):
    """O(n): remember what we have seen."""
    seen = set()
    for value in nums:
        if target - value in seen:        # O(1) lookup
            return True
        seen.add(value)
    return False


for size in [200, 400, 800, 1600]:
    sample = random.sample(range(size * 10), size)
    start = time.perf_counter()
    has_pair_slow(sample, -1)             # -1 never occurs -> worst case
    slow_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    has_pair_fast(sample, -1)
    fast_ms = (time.perf_counter() - start) * 1000
    print(f"  n={size:>5}:  O(n^2) {slow_ms:8.3f} ms   O(n) {fast_ms:7.3f} ms   "
          f"({slow_ms / max(fast_ms, 1e-6):5.0f}x faster)")

print("\n" + "=" * 60)
print("4. Other classic traps")
print("=" * 60)


def concat_with_plus(parts):
    """O(n^2): every += copies the whole string."""
    text = ""
    for part in parts:
        text += part
    return text


def concat_with_join(parts):
    """O(n): one allocation."""
    return "".join(parts)


chunks = ["x" * 100] * 20_000
benchmark("string += in a loop", concat_with_plus, chunks)
benchmark('"".join(parts)', concat_with_join, chunks)


def membership_in_list(items, queries):
    return sum(1 for q in queries if q in items)          # O(len(items)) each


def membership_in_set(items, queries):
    as_set = set(items)                                   # one O(n) build
    return sum(1 for q in queries if q in as_set)         # O(1) each


items = list(range(20_000))
queries = list(range(19_000, 20_000))
benchmark("membership in list", membership_in_list, items, queries)
benchmark("membership in set", membership_in_set, items, queries)


def pop_front_list(items):
    """O(n^2): each pop(0) shifts the whole list."""
    work = list(items)
    total = 0
    while work:
        total += work.pop(0)
    return total


def pop_front_deque(items):
    """O(n): deque.popleft is O(1)."""
    work = deque(items)
    total = 0
    while work:
        total += work.popleft()
    return total


small = list(range(20_000))
benchmark("list.pop(0) in a loop", pop_front_list, small)
benchmark("deque.popleft in a loop", pop_front_deque, small)


def sum_inside_loop(nums):
    """O(n^2): recomputing sum() every iteration."""
    total = 0
    for i in range(len(nums)):
        total += sum(nums[:i + 1])
    return total


def running_total(nums):
    """O(n): accumulate as you go."""
    total = 0
    running = 0
    for value in nums:
        running += value
        total += running
    return total


sample = list(range(4_000))
benchmark("sum(slice) inside a loop", sum_inside_loop, sample)
benchmark("running total", running_total, sample)

print("\n" + "=" * 60)
print("5. Space complexity & recursion limits")
print("=" * 60)
big_list = [0] * 1_000_000
big_gen = (0 for _ in range(1_000_000))
print(f"  list of 1e6 ints : {sys.getsizeof(big_list):>10,} bytes")
print(f"  generator        : {sys.getsizeof(big_gen):>10,} bytes")
print(f"  recursion limit  : {sys.getrecursionlimit()}")


def deep_recursion(n):
    """Each call uses stack space: O(n) memory even though the work is O(1)."""
    if n == 0:
        return 0
    return 1 + deep_recursion(n - 1)


print("  deep_recursion(900) works:", deep_recursion(900))
try:
    deep_recursion(2000)
except RecursionError as exc:
    print("  deep_recursion(2000) ->", type(exc).__name__, "- rewrite it iteratively!")

print("\n" + "=" * 60)
print("6. Amortised O(1): append vs insert(0)")
print("=" * 60)
count = 50_000
benchmark("append to the end", lambda: [x for x in range(count)].append(1) or "done")
start = time.perf_counter()
work = []
for x in range(count):
    work.append(x)                     # O(1) amortised
print(f"  {count:,} appends                 {(time.perf_counter() - start) * 1000:9.3f} ms")
start = time.perf_counter()
work = []
for x in range(count):
    work.insert(0, x)                  # O(n) each -> O(n^2) total
print(f"  {count:,} insert(0, x)            {(time.perf_counter() - start) * 1000:9.3f} ms  <- avoid!")

print("\n" + "=" * 60)
print("7. A worked optimisation: find duplicates")
print("=" * 60)


def duplicates_slow(items):
    """O(n^2): compare every pair."""
    result = []
    for i, value in enumerate(items):
        if value in items[:i] and value not in result:
            result.append(value)
    return result


def duplicates_fast(items):
    """O(n): Counter does one pass."""
    return [value for value, count in Counter(items).items() if count > 1]


values = [random.randint(0, 500) for _ in range(5_000)]
benchmark("duplicates: pairwise", duplicates_slow, values)
benchmark("duplicates: Counter", duplicates_fast, values)
print("  same answer:", sorted(duplicates_slow(values)) == sorted(duplicates_fast(values)))

print("\n" + "=" * 60)
print("8. Your decision checklist (use this on every problem)")
print("=" * 60)
print("""  1. What is n? How large can it get?
  2. What is the brute-force complexity? Does it fit the budget?
  3. What data structure removes the inner loop?
        "have I seen this before?"        -> set / dict
        "the next biggest/smallest"       -> heap
        "sorted, and I search a lot"      -> sort once + bisect
        "first/last in, first out"        -> stack (list) / deque
        "give me sums of ranges"          -> prefix sums
  4. State the time and space complexity of your final answer — out loud.""")
print()
print("Lesson 16 done — now do exercises/ex_16_big_o.py ✅ and start dsa_01 ✅")
