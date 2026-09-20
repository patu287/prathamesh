"""
LESSON 12 · Comprehensions, generators & itertools

This is the lesson that makes your Python look like Python. Everything here is
still readable code — it is not "clever", it is idiomatic.

# 1. List comprehension — build a list in one expression

    [EXPRESSION for ITEM in ITERABLE if CONDITION]

    squares = [n * n for n in range(6)]              # [0, 1, 4, 9, 16, 25]
    evens   = [n for n in nums if n % 2 == 0]
    labels  = ["even" if n % 2 == 0 else "odd" for n in nums]
    pairs   = [(a, b) for a in [1, 2] for b in "xy"]

Equivalent loop:

    squares = []
    for n in range(6):
        squares.append(n * n)

The comprehension is faster (no repeated method lookup on `append`), shorter,
and — once you are used to it — easier to read. Rule of thumb: if it needs
more than ~2 lines or nesting levels, use a normal loop.

# 2. Dict and set comprehensions

    {n: n * n for n in range(4)}            # {0: 0, 1: 1, 2: 4, 3: 9}
    {len(word) for word in words}           # set: unique lengths
    {word: len(word) for word in words if len(word) > 3}
    {v: k for k, v in d.items()}            # invert a mapping

# 3. Generator expression — like a comprehension but LAZY

    (n * n for n in range(10**9))    # parentheses, not brackets

It computes one value at a time and never stores the whole sequence, so you
can process data that does not fit in memory. Perfect as a function argument:

    sum(n * n for n in range(1_000_000))     # no giant list built
    any(n % 7 == 0 for n in nums)            # stops at the first hit
    all(x > 0 for x in nums)                 # stops at the first failure
    max(len(w) for w in words)
    ",".join(str(n) for n in numbers)

This is the idiom for "sum / any / all over something computed on the fly".

# 4. Generators with yield

    def countdown(n):
        while n > 0:
            yield n          # pause here and hand back a value
            n -= 1

    for value in countdown(3):     # 3, 2, 1
        print(value)

A function containing `yield` returns a generator: calling it runs *nothing*
until you iterate. State is remembered between yields. Great for:
* streaming a huge file line by line,
* infinite sequences (`itertools.count()`),
* pipelines:  read -> filter -> transform -> write.

`next(gen, default)` pulls one item; `list(gen)` drains it (once!).

# 5. itertools — the standard library's DSA toolbox

    import itertools as it

    it.count(10, 2)             10, 12, 14, ... (infinite)
    it.cycle("AB")              A, B, A, B, ...
    it.repeat("x", 3)           x, x, x
    it.accumulate([1,2,3,4])    1, 3, 6, 10        <- prefix sums! (dsa_01)
    it.chain([1,2],[3,4])       1, 2, 3, 4         <- concatenate lazily
    it.islice(gen, 5)           first 5 of anything
    it.groupby(sorted_data)     grouping (needs sorted input)
    it.product("ab", [1,2])     cartesian product (nested loops)
    it.combinations("abc", 2)   choose 2 -> ab, ac, bc
    it.permutations("abc", 2)   arrangements
    it.pairwise([1,2,3])        1-2, 2-3
    it.zip_longest(a, b, fillvalue=0)

`accumulate` and `groupby` in particular show up in real coding problems.

# 6. The `enumerate` / `zip` / `reversed` / `sorted` family

All of them are lazy views or iterators, and all work on any iterable:

    for i, ch in enumerate("abc", start=1): ...
    for name, score in zip(names, scores): ...
    for item in reversed(items): ...
    dict(sorted(counts.items(), key=lambda kv: -kv[1]))

# 7. When NOT to use a comprehension

    # Unreadable / side effects:
    [print(x) for x in items]            # ✋ it is a loop, write a loop

    # Too much logic:
    [f(x) for x in items if cond(x) and other(x) or special(x)]   # ✋ write a function

    # You only need a total:
    [n for n in nums if n % 2][0]        # ✋ use next(n for n in nums if n % 2) or a loop

Style rule: comprehensions are for *building a container*, not for doing work.

# 8. Memory demo

    sys.getsizeof([n for n in range(1_000_000)])   # ~8 MB list of ints
    sys.getsizeof(n for n in range(1_000_000))     # ~200 bytes generator
"""

import itertools as it
import sys
import time

print("=" * 60)
print("1. List comprehensions")
print("=" * 60)
print("squares        :", [n * n for n in range(8)])
print("evens          :", [n for n in range(20) if n % 2 == 0])
print("divisible 3 or 5:", [n for n in range(30) if n % 3 == 0 or n % 5 == 0])
print("labels         :", ["even" if n % 2 == 0 else "odd" for n in range(6)])
print("nested loops   :", [(a, b) for a in [1, 2] for b in "xy"])
matrix = [[1, 2, 3], [4, 5, 6]]
print("flatten        :", [x for row in matrix for x in row])
print("transpose      :", [[row[i] for row in matrix] for i in range(3)])
print("strings        :", [word[::-1] for word in ["abc", "hi"]])
print("with index     :", [f"{i}:{ch}" for i, ch in enumerate("abc")])

print("\n  the same loop written both ways:")
squares_loop = []
for n in range(5):
    squares_loop.append(n * n)
print("    loop         :", squares_loop)
print("    comprehension:", [n * n for n in range(5)])

print("\n" + "=" * 60)
print("2. Dict & set comprehensions")
print("=" * 60)
print("dict    :", {n: n ** 3 for n in range(4)})
words = ["hi", "hello", "hey", "world", "code"]
print("set     :", sorted({len(w) for w in words}))
print("filtered:", {w: len(w) for w in words if len(w) > 3})
print("inverted:", {len(w): w for w in words})
print("counts  :", {ch: "mississippi".count(ch) for ch in sorted(set("mississippi"))})
csv = "ravi:88,priya:95,asha:72"
print("parse   :", {name: int(score) for name, score in (item.split(":") for item in csv.split(","))})

print("\n" + "=" * 60)
print("3. Generator expressions (lazy)")
print("=" * 60)
squares_gen = (n * n for n in range(5))
print("generator object:", squares_gen)
print("list(gen)       :", list(squares_gen))
print("drained again   :", list(squares_gen), " <- generators are one-shot!")

print("sum of squares 1..1000      :", sum(n * n for n in range(1, 1001)))
print("any even number in [1,3,5,8] :", any(n % 2 == 0 for n in [1, 3, 5, 8]))
print("all positive in [1,3,5]      :", all(n > 0 for n in [1, 3, 5]))
print("max word length              :", max(len(w) for w in words))
print("joined                       :", ",".join(str(n) for n in range(5)))

print("\n  memory: list vs generator, 1 million values")
list_version = [n for n in range(1_000_000)]
gen_version = (n for n in range(1_000_000))
print(f"    list      : {sys.getsizeof(list_version):>9,} bytes")
print(f"    generator : {sys.getsizeof(gen_version):>9,} bytes")

print("\n" + "=" * 60)
print("4. Generators with yield")
print("=" * 60)


def countdown(n):
    """Yield n, n-1, ... 1 — nothing runs until you iterate."""
    print("    (countdown started)")
    while n > 0:
        yield n
        n -= 1


print("  calling countdown(3) does not print or compute yet:")
gen = countdown(3)
print("  next(gen) ->", next(gen))
print("  next(gen) ->", next(gen))
print("  next(gen) ->", next(gen))
print("  exhausted ->", next(gen, "GeneratorExhausted"))


def read_scores(lines):
    """Parse a stream of lines lazily."""
    for line in lines:
        name, score = line.split(",")
        yield name.strip(), int(score)


raw = ["ravi,88", "priya,95", "asha,72"]
for name, score in read_scores(raw):
    print(f"    {name} -> {score}")
print("  top scorer:", max(read_scores(raw), key=lambda pair: pair[1]))


def fib_stream():
    """An INFINITE generator. Only safe because consumers take what they need."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


print("  first 10 fibonacci:", list(it.islice(fib_stream(), 10)))

print("\n" + "=" * 60)
print("5. itertools — professional tools")
print("=" * 60)
print("accumulate (prefix sums):", list(it.accumulate([1, 2, 3, 4, 5])))
print("accumulate with max     :", list(it.accumulate([3, 1, 4, 1, 5], max)))
print("chain                   :", list(it.chain([1, 2], [3], "ab")))
print("islice from infinite    :", list(it.islice(it.count(10, 5), 4)), " (10, 15, 20, 25)")
print("cycle                   :", list(it.islice(it.cycle("AB"), 5)))
print("product                 :", list(it.product([1, 2], "ab")))
print("combinations('abc', 2)  :", list(it.combinations("abc", 2)))
print("permutations('abc', 2)  :", list(it.permutations("abc", 2)))
print("pairwise                :", list(it.pairwise([1, 2, 3, 4])))

# groupby needs the data sorted by the grouping key
people = [("Ravi", 20), ("Priya", 22), ("Asha", 20), ("Dev", 22)]
by_age = it.groupby(sorted(people, key=lambda pair: pair[1]), key=lambda pair: pair[1])
print("groupby                 :", {age: [name for name, _ in group] for age, group in by_age})

words_letters = ["apple", "avocado", "banana", "berry", "cherry"]
grouped = it.groupby(sorted(words_letters), key=lambda w: w[0])
print("groupby first letter    :", {key: list(group) for key, group in grouped})

print("\n" + "=" * 60)
print("6. A real pipeline: filter -> transform -> aggregate")
print("=" * 60)
readings = [12.5, 3.0, 44.1, 7.8, 19.2, 0.5, 33.3]
high = [round(value, 1) for value in readings if value > 10]
print("  readings above 10      :", high)
print("  their average          :", round(sum(high) / len(high), 2))
print("  cleaned + squared      :", [round(value ** 2, 2) for value in readings if value > 1])
print("  index-value pairs > 20 :", [(i, v) for i, v in enumerate(readings) if v > 20])

print("\n" + "=" * 60)
print("7. Performance: comprehension vs loop vs map")
print("=" * 60)
n = 300_000
start = time.perf_counter()
acc = []
for i in range(n):
    acc.append(i * i)
loop_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
comp = [i * i for i in range(n)]
comp_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
mapped = list(map(lambda i: i * i, range(n)))
map_ms = (time.perf_counter() - start) * 1000

print(f"  for + append : {loop_ms:6.1f} ms")
print(f"  comprehension: {comp_ms:6.1f} ms  ({loop_ms / comp_ms:.2f}x faster)")
print(f"  map(lambda)  : {map_ms:6.1f} ms")

print("\n" + "=" * 60)
print("8. Readable vs clever (write the first one)")
print("=" * 60)
nums = [1, 2, 3, 4, 5, 6]
# ✋ hard to read at a glance
clever = [n ** 2 if n % 2 == 0 else n ** 3 for n in nums if n != 3 and not (n == 5 and n > 4)]
# ✅ split the intent
def transform(n):
    if n % 2 == 0:
        return n ** 2
    return n ** 3


readable = [transform(n) for n in nums if n not in (3, 5)]
print("  clever  :", clever)
print("  readable:", readable)

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. One line: a list of all squares under 100 that are odd.
# 2. One line: a dict mapping word -> word reversed for ["abc", "hi"].
# 3. One line: the sum of all even numbers from 1 to 1000 (generator inside sum).
# 4. One line: a list of (index, char) for the uppercase letters of a string.
# 5. Write a generator `take_every(iterable, k)` yielding every k-th item.
# 6. Write a generator `batches(iterable, size)` that groups items into lists of
#    `size` — this is the real "process data in chunks" pattern.
# 7. Use itertools.accumulate to produce running totals of a list of marks.
# 8. Use itertools.combinations to print all 2-element pairs from [1, 2, 3, 4]
#    that sum to 5.
# 9. Rewrite this loop as a comprehension and say which you prefer, in a comment:
#       result = []
#       for word in words:
#           if len(word) > 3:
#               result.append(word.upper())
print()
print("Lesson 12 done — now do exercises/ex_12_comprehensions.py ✅")
