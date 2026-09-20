"""
LESSON 08 · Tuples & sets

# TUPLES — like lists, but immutable (cannot be changed)

    point = (3, 4)
    red, green, blue = (255, 128, 0)      # unpacking
    first = point[0]                       # indexing/slicing works
    single = (5,)                          # <- the comma makes the tuple!
    not_a_tuple = (5)                      # this is just the int 5
    empty = ()

    t = (1, 2, 3)
    t[0] = 9        -> TypeError: 'tuple' object does not support item assignment

Why use a tuple instead of a list?

1. **Safety** — coordinates, RGB colours, DB rows, dates: things that
   shouldn't change.
2. **Hashable** — a tuple can be a dict key or a set member; a list cannot.
       {(0, 0): "start", (1, 2): "goal"}       # grid coordinates -> value
3. **Speed/memory** — smaller and slightly faster than a list.
4. **Multiple return values** — `return x, y` actually returns a tuple.

Useful bits:
    len(t), t.count(x), t.index(x), min(t), max(t), sum(t)
    a, b = b, a               # swap uses tuple packing/unpacking
    x, *rest = (1, 2, 3)      # x = 1, rest = [2, 3]
    tuple([1, 2]) -> (1, 2)   # convert list -> tuple
    sorted(t) -> list

`namedtuple` / `dataclass` (lesson 14) give tuples names when that helps.

# SETS — unordered collection of UNIQUE values

    s = {1, 2, 3}
    empty = set()             # NOT {} — that is an empty dict!
    s.add(4)
    s.discard(1)              # remove if present (no error if missing)
    s.remove(1)               # raises KeyError if missing
    3 in s                    # O(1) average — this is the point of sets

Sets are built on a hash table, so membership testing, adding and removing are
O(1) average, versus O(n) for a list. When a problem asks "have I seen this
before?" or "how many distinct?", reach for a set.

Math operations:

    a | b   union              all elements of both
    a & b   intersection       in both
    a - b   difference         in a but not b
    a ^ b   symmetric diff     in exactly one
    a <= b  subset             a.issubset(b)
    a < b   proper subset

    a.union(b) / a.intersection(b) / a.difference(b)

Iteration order is insertion order in practice (CPython), but you must NOT
rely on it — sets are conceptually unordered. Need sorted output?
`sorted(my_set)`.

# Python's built-in set-comprehension

    {n % 5 for n in range(20)}

# Members must be hashable
Integers, floats, strings, booleans, None, tuples (of hashables) are hashable.
Lists, dicts and sets are NOT: `{[1, 2]}` -> TypeError: unhashable type: 'list'.
Fix: convert to a tuple `{(1, 2)}`.

# Quick decision guide

Need to keep order + duplicates?          -> list
Need an immutable record / dict key?      -> tuple
Need fast membership / uniqueness?        -> set
Need key -> value lookup?                 -> dict (lesson 09)
"""

import time

print("=" * 60)
print("1. Tuples: create, unpack, protect")
print("=" * 60)
point = (3, 4)
print("point      =", point, "| type:", type(point).__name__)
x, y = point
print("unpacked   : x =", x, "y =", y)
print("point[0]   =", point[0], "| point[-1] =", point[-1])
print("slice      =", point[:1])
print("single     :", (5,), "-> type", type((5,)).__name__, "| (5) -> type", type((5)).__name__)
try:
    point[0] = 9
except TypeError as exc:
    print("t[0] = 9  ->", type(exc).__name__, "-", exc)

def min_max(items):
    """Return two values at once — really one tuple."""
    return min(items), max(items)

low, high = min_max([4, 1, 9])
print("multiple return values:", low, high, "| as tuple:", min_max([4, 1, 9]))

first, *rest = (10, 20, 30, 40)
print("star unpacking:", first, rest)

print("\n" + "=" * 60)
print("2. Tuples as dict keys — grid coordinates")
print("=" * 60)
maze = {
    (0, 0): "start",
    (0, 3): "door",
    (2, 2): "treasure",
}
print("maze[(2, 2)] =", maze[(2, 2)])
for position, label in maze.items():
    print(f"  {label:<8} at {position}")

print("\n" + "=" * 60)
print("3. Sets: uniqueness and O(1) membership")
print("=" * 60)
nums = [1, 2, 2, 3, 3, 3, 4]
unique = set(nums)
print("list            :", nums)
print("set(list)       :", unique, "| distinct count:", len(unique))
print("back to list    :", sorted(unique))
print("2 in {1,2,3}    :", 2 in {1, 2, 3})

seen = set()
duplicates = set()
for n in nums:
    if n in seen:                 # O(1) lookup
        duplicates.add(n)
    seen.add(n)
print("duplicates      :", duplicates)
print("seen in order of first appearance:", list(dict.fromkeys(nums)))

print("\n" + "=" * 60)
print("4. Set algebra")
print("=" * 60)
python_devs = {"ravi", "priya", "asha"}
js_devs = {"priya", "dev", "asha"}
print("both     (union |)       :", sorted(python_devs | js_devs))
print("both langs (intersection):", sorted(python_devs & js_devs))
print("python only (difference) :", sorted(python_devs - js_devs))
print("exactly one (sym diff)   :", sorted(python_devs ^ js_devs))
print("subset check             :", {"ravi"} <= python_devs)

print("\n" + "=" * 60)
print("5. Set operations used to solve real problems fast")
print("=" * 60)

def has_duplicate(items):
    """O(n) time, O(n) space — the set does all the work."""
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False

def common_elements(a, b):
    return sorted(set(a) & set(b))

def missing_number(numbers, n):
    """1..n with one number missing — set difference."""
    return (set(range(1, n + 1)) - set(numbers)).pop()

print("has_duplicate([1,2,3])   :", has_duplicate([1, 2, 3]))
print("has_duplicate([1,2,2])   :", has_duplicate([1, 2, 2]))
print("common([1,2,3],[2,3,4])  :", common_elements([1, 2, 3], [2, 3, 4]))
print("missing from 1..5        :", missing_number([1, 2, 4, 5], 5))

print("\n" + "=" * 60)
print("6. Why sets are fast (measured)")
print("=" * 60)
n = 200_000
as_list = list(range(n))
as_set = set(as_list)
start = time.perf_counter()
_ = (n - 1) in as_list
list_ms = (time.perf_counter() - start) * 1000
start = time.perf_counter()
_ = (n - 1) in as_set
set_ms = (time.perf_counter() - start) * 1000
print(f"  list membership: {list_ms:.4f} ms (O(n) — checks every element)")
print(f"  set membership : {set_ms:.4f} ms (O(1) — hashes straight to it)")

print("\n" + "=" * 60)
print("7. frozenset — an immutable set (can be a dict key)")
print("=" * 60)
fs = frozenset([1, 2, 3])
print("frozenset:", fs, "| usable as a key:", {frozenset([1, 2]): "pair"})

print("\n" + "=" * 60)
print("8. Convert between the containers")
print("=" * 60)
source = [3, 1, 3, 2]
print("list -> set   :", set(source))
print("set -> list   :", list({1, 2, 3}))
print("list -> tuple :", tuple(source))
print("tuple -> list :", list((1, 2)))
print("list -> dict  :", dict.fromkeys(source, 0), " (keys with a default value)")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. From [1, 2, 2, 3, 4, 4, 4] produce the sorted unique values and the
#    duplicates, using sets.
# 2. Write `are_anagrams(a, b)` -> True/False using sorted() or Counter.
# 3. Given two lists of names, print: who is in both, who is only in the first,
#    and whether the first is a subset of the second.
# 4. Given marks = [(ravi, 88), (priya, 95), (ravi, 70)], sum the marks per
#    student using a dict. (Preview of lesson 09.)
# 5. Write `longest_unique_substring_length(s)`: the length of the longest
#    run of characters with no repeats. [Sliding window + set — the classic.]
# 6. Explain in a comment why `{(1, 2)}` works but `{[1, 2]}` raises TypeError.
print()
print("Lesson 08 done — now do exercises/ex_08_tuples_sets.py ✅")
