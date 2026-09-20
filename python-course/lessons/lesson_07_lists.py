"""
LESSON 07 · Lists — the most important data structure

A list is an ordered, mutable collection: `[10, 20, 30]`.
"Mutable" means you can change it after creating it. 90% of DSA uses a list,
an array, or something built on top of one.

# Creating

    nums  = [3, 1, 4, 1, 5]
    empty = []
    mixed = [1, "two", 3.0, True, None]     # allowed, rarely wise
    nested = [[1, 2], [3, 4]]              # a matrix (2D list)
    grid = [[0] * 3 for _ in range(2)]     # 2 rows x 3 cols of zeros

# Indexing & slicing — exactly like strings

    nums[0] nums[-1] nums[2:4] nums[::-1]
    nums[99] -> IndexError

# Mutating

    nums[0] = 99              # replace
    nums[1:3] = [7, 7, 7]     # slice assignment can change the length
    del nums[0]               # delete by index
    nums.append(6)            # add one at the END        O(1)
    nums.insert(0, 0)         # insert at position        O(n) — shifts everything
    nums.extend([7, 8])       # add many at the end
    nums.pop()                # remove & return last      O(1)
    nums.pop(0)               # remove & return index 0   O(n)
    nums.remove(4)            # remove first 4 by VALUE   O(n)
    nums.clear()              # empty it
    nums += [1]               # same as extend
    nums *= 2                 # repeat

# Reading

    len(nums) sum(nums) min(nums) max(nums) sorted(nums)
    nums.index(value)     # first position, ValueError if missing
    nums.count(value)     # how many
    5 in nums             # membership test  O(n)
    nums.copy()  == nums[:]

# Sorting

    nums.sort()                       # in place, returns None (!)
    nums.sort(reverse=True)
    sorted(nums)                      # returns a NEW list, leaves original alone
    words.sort(key=len)               # by length
    words.sort(key=str.lower)         # case-insensitive
    words.sort(key=lambda w: (-len(w), w))   # multiple criteria (lesson 15)

`sorted()`/`.sort()` use Timsort: O(n log n), stable (equal items keep their
relative order). Sorting is so fast that "sort first, then scan" solves a
surprising number of problems.

# Comprehensions — the Python signature move

    squares = [n * n for n in range(6)]              # [0, 1, 4, 9, 16, 25]
    evens   = [n for n in nums if n % 2 == 0]
    labels  = ["even" if n % 2 == 0 else "odd" for n in nums]
    flat    = [x for row in matrix for x in row]     # flatten 2D -> 1D

Read them as: "collect EXPRESSION for each ITEM in SOURCE if CONDITION".

# Copying: the classic bug

    a = [1, 2, 3]
    b = a               # NOT a copy! b is another name for the same list
    b.append(4)
    print(a)            # [1, 2, 3, 4]  <- surprise!

    c = a[:]            # shallow copy: new outer list
    d = list(a)
    e = a.copy()
    import copy ; f = copy.deepcopy(a)   # for nested lists

# Big-O cheat sheet (n = len)

    index / append / pop()        O(1)
    insert(0, x) / pop(0)         O(n)
    search (x in list)            O(n)
    sort                          O(n log n)
    slice a[i:j]                  O(j - i)

Choosing a list when you need fast membership tests is a common beginner
performance bug -> use a set (lesson 08).

# Two-pointer pattern (your first real DSA technique)

    left, right = 0, len(a) - 1
    while left < right:
        ... ; left += 1 ; right -= 1

# Prefix sums (your second) — answer "sum of a[i:j]" in O(1)

    prefix[0] = 0 ; prefix[k+1] = prefix[k] + a[k]
    sum(a[i:j]) = prefix[j] - prefix[i]
"""

print("=" * 60)
print("1. Create, index, slice")
print("=" * 60)
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print("nums        =", nums)
print("len         =", len(nums))
print("nums[0]     =", nums[0], "| nums[-1] =", nums[-1])
print("nums[2:5]   =", nums[2:5], "| nums[:3] =", nums[:3], "| nums[5:] =", nums[5:])
print("nums[::-1]  =", nums[::-1])
print("nums[::2]   =", nums[::2])

print("\n" + "=" * 60)
print("2. Mutating")
print("=" * 60)
letters = ["a", "b", "c"]
letters.append("d")
print("append    ->", letters)
letters.insert(0, "z")
print("insert(0) ->", letters)
letters[1] = "B"
print("assign    ->", letters)
letters.remove("B")
print("remove    ->", letters)
popped = letters.pop()
print("pop()     ->", letters, "| popped:", popped)
letters.extend(["x", "y"])
print("extend    ->", letters)
letters[1:3] = ["q"]
print("slice set ->", letters)
del letters[0]
print("del       ->", letters)

print("\n" + "=" * 60)
print("3. Reading & aggregate functions")
print("=" * 60)
print("sum/min/max :", sum(nums), min(nums), max(nums))
print("sorted      :", sorted(nums))
print("reverse sort:", sorted(nums, reverse=True))
print("index of 9  :", nums.index(9))
print("count of 1  :", nums.count(1))
print("5 in nums   :", 5 in nums, "| 100 in nums:", 100 in nums)
print("average     :", sum(nums) / len(nums))

print("\n" + "=" * 60)
print("4. sort() vs sorted()  (mutates vs returns new)")
print("=" * 60)
original = [3, 1, 2]
copy_for_sort = original.copy()
print("sorted(original)      =", sorted(original), "| original untouched:", original)
returned = copy_for_sort.sort()          # returns None!
print("list.sort() returns   =", returned, "| but the list is now:", copy_for_sort)
print("sort(reverse=True)    =", sorted(original, reverse=True))
words = ["banana", "apple", "Cherry", "fig"]
print("by length             :", sorted(words, key=len))
print("case-insensitive      :", sorted(words, key=str.lower))

print("\n" + "=" * 60)
print("5. List comprehensions")
print("=" * 60)
print("squares        :", [n * n for n in range(8)])
print("evens          :", [n for n in nums if n % 2 == 0])
print("even -> 'even' :", ["even" if n % 2 == 0 else "odd" for n in nums[:4]])
words = ["hi", "hello", "hey", "world"]
print("starts with h  :", [w.upper() for w in words if w.startswith("h")])
matrix = [[1, 2, 3], [4, 5, 6]]
print("flattened      :", [x for row in matrix for x in row])
print("transposed     :", [[row[i] for row in matrix] for i in range(3)])

print("\n" + "=" * 60)
print("6. The aliasing trap")
print("=" * 60)
a = [1, 2, 3]
b = a                    # same object, two names
b.append(4)
print("b = a; b.append(4) -> a is now", a, " (same list!)")
c = a[:]                 # real copy
c.append(5)
print("c = a[:]; c.append(5) -> a stays", a)
print("a is b:", a is b, "| a == c:", a == c, "| a is c:", a is c)
grid_bug = [[0] * 3] * 2      # BAD: both rows are the SAME list
grid_bug[0][0] = 9
print("[[0]*3]*2 then set [0][0]=9 ->", grid_bug, " (both rows changed!)")
grid_ok = [[0] * 3 for _ in range(2)]
grid_ok[0][0] = 9
print("comprehension version       ->", grid_ok, " (correct)")

print("\n" + "=" * 60)
print("7. Two pointers: reverse in place + pair search on sorted data")
print("=" * 60)

def reverse_in_place(items):
    left, right = 0, len(items) - 1
    while left < right:
        items[left], items[right] = items[right], items[left]
        left += 1
        right -= 1
    return items

print("reversed in place:", reverse_in_place([1, 2, 3, 4, 5]))

def has_pair_sum(sorted_items, target):
    """Two-pointer pair search: O(n) time, O(1) space. Needs sorted input."""
    left, right = 0, len(sorted_items) - 1
    while left < right:
        current = sorted_items[left] + sorted_items[right]
        if current == target:
            return (sorted_items[left], sorted_items[right])
        if current < target:
            left += 1               # need a bigger sum -> move left up
        else:
            right -= 1              # need a smaller sum -> move right down
    return None

data = [1, 3, 4, 6, 8, 11]
for target in [10, 14, 100]:
    print(f"  pair summing to {target:>3}:", has_pair_sum(data, target))

print("\n" + "=" * 60)
print("8. Prefix sums: range-sum queries in O(1)")
print("=" * 60)

def build_prefix(items):
    """prefix[i] = sum of items[:i].  prefix[0] is always 0."""
    prefix = [0] * (len(items) + 1)
    for i, value in enumerate(items):
        prefix[i + 1] = prefix[i] + value
    return prefix

def range_sum(prefix, i, j):
    """Sum of items[i:j] — half-open [i, j)."""
    return prefix[j] - prefix[i]

arr = [5, 2, 8, 1, 9, 3]
prefix = build_prefix(arr)
print("arr    =", arr)
print("prefix =", prefix)
print("sum[1:4] (2+8+1) =", range_sum(prefix, 1, 4))
print("sum[0:6]         =", range_sum(prefix, 0, 6))

print("\n" + "=" * 60)
print("9. Efficiency demo: list vs set membership")
print("=" * 60)
import time
big_list = list(range(200_000))
big_set = set(big_list)
start = time.perf_counter()
_ = 199_999 in big_list
list_time = time.perf_counter() - start
start = time.perf_counter()
_ = 199_999 in big_set
set_time = time.perf_counter() - start
print(f"  `in` a list: {list_time * 1000:.3f} ms")
print(f"  `in` a set : {set_time * 1000:.3f} ms   <- {list_time / max(set_time, 1e-9):.0f}x faster")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. From [4, 9, 2, 9, 7, 4, 9], print: sum, max, the number of 9s, and the
#    list sorted descending. Then remove duplicates while keeping order.
# 2. Reverse a list WITHOUT [::-1] and without reverse() (two pointers).
# 3. Rotate a list right by k:  [1,2,3,4,5], k=2 -> [4,5,1,2,3].
# 4. Move all zeros to the end, keeping the order of the non-zeros.
#    [0,1,0,3,12] -> [1,3,12,0,0]
# 5. Given marks = [45, 67, 89, 32, 91], print each mark with "pass"/"fail"
#    next to it (pass >= 40) using a loop, then again using a comprehension.
# 6. Build a 3x3 multiplication table as a nested list, then print it neatly.
# 7. Find the second largest value in a list with a single loop (no sorting).
print()
print("Lesson 07 done — now do exercises/ex_07_lists.py ✅")
