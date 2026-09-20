"""
LESSON 15 · Lambdas, sorting tricks & decorators

This is the "intermediate" shelf: small tools that make the difference between
code that works and code that reads well.

# 1. Lambda — an anonymous one-expression function

    square = lambda x: x * x          # same as: def square(x): return x * x
    (lambda a, b: a + b)(2, 3)        # 5 — called immediately

A lambda can only contain ONE expression (no statements, no assignment, no
print). So why use it? As a throwaway argument:

    sorted(words, key=lambda w: len(w))
    max(people, key=lambda p: p["age"])
    filter(lambda n: n % 2 == 0, nums)

Style rule: **if you want to name it, use `def`.** Lambdas are for passing
quick behaviour to another function.

Where a built-in already exists, prefer it — `key=len` beats
`key=lambda w: len(w)`, and `operator.itemgetter("age")` beats
`key=lambda p: p["age"]` (it is also faster).

# 2. Sorting like a professional

    key= is a function applied to each item; sorting then compares the RESULTS.

    sorted(words, key=len)
    sorted(words, key=str.lower)
    sorted(people, key=lambda p: p["age"])
    sorted(people, key=lambda p: (p["age"], p["name"]))        # tie-break
    sorted(scores.items(), key=lambda kv: kv[1], reverse=True) # by value

Negative keys sort descending per-field without `reverse=True`:

    sorted(people, key=lambda p: (-p["age"], p["name"]))   # age desc, name asc

Multi-key with mixed directions is exactly why this trick exists: `reverse=True`
flips *everything*, negative numbers flip only one field.

**Timsort is stable**: items that compare equal keep their original order.

Sorting a dict by value, top-k:

    Counter(text.split()).most_common(3)
    dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

Sorting objects by attribute:

    sorted(students, key=lambda s: s.average, reverse=True)
    from operator import attrgetter, itemgetter
    sorted(students, key=attrgetter("average"))
    sorted(rows, key=itemgetter(1))         # by second column

    # cmp_to_key — when you must have a comparison function (rare in Python)
    from functools import cmp_to_key
    sorted(nums, key=cmp_to_key(lambda a, b: b - a))

# 3. map / filter / zip / any / all / sum with a key

    list(map(str, [1, 2]))                     # ['1', '2']
    list(map(pow, [2, 3], [3, 2]))             # [8, 9]  two iterables
    list(filter(None, [0, 1, "", "x"]))        # [1, 'x']  (drops falsy)
    any(word.startswith("py") for word in words)
    all(len(pw) >= 8 for pw in passwords)
    max(students, key=lambda s: s.average)
    min(inventory, key=inventory.get)          # key by dict value

Comprehensions usually replace map/filter for readability; keep `map`/`filter`
for the cases above where no extra function is needed.

# 4. Decorators — functions that wrap functions

    def logged(func):
        def wrapper(*args, **kwargs):
            print(f"calling {func.__name__}")
            result = func(*args, **kwargs)
            print(f"{func.__name__} returned {result}")
            return result
        return wrapper

    @logged                    # this is just: add = logged(add)
    def add(a, b):
        return a + b

Useful decorators from the standard library:

    @functools.lru_cache        memoise (exponential -> linear, one line)
    @functools.cache            same, unbounded (3.9+)
    @property                   (lesson 14)
    @staticmethod / @classmethod (lesson 14)
    @dataclasses.dataclass      (lesson 14)
    @contextlib.contextmanager  write your own `with` blocks

Always wrap the inner function with `functools.wraps(func)` so the name and
docstring survive.

Why they are worth knowing: timing, caching, retrying, logging, permission
checks. You will meet them constantly in real libraries (Flask routes, Django
views, pytest fixtures).

# 5. Closures — functions that remember

    def make_multiplier(factor):
        def multiply(n):
            return n * factor        # `factor` is remembered
        return multiply

    double = make_multiplier(2)
    double(5)                        # 10

The inner function keeps a reference to the enclosing scope's variables. That
is how decorators work under the hood.

# 6. A memo helper you can reuse in DSA

    def memoize(func):
        cache = {}
        @wraps(func)
        def wrapper(*args):
            if args not in cache:
                cache[args] = func(*args)
            return cache[args]
        return wrapper

This is exactly what `functools.lru_cache` does, which is why in real code we
just write `@lru_cache`.
"""

import time
from collections import Counter
from functools import cache, cmp_to_key, lru_cache, reduce, wraps
from operator import attrgetter, itemgetter

print("=" * 60)
print("1. Lambdas")
print("=" * 60)
square = lambda x: x * x
add = lambda a, b: a + b
print("  square(6)          :", square(6))
print("  add(2, 3)          :", add(2, 3))
print("  immediately called :", (lambda x: x.upper())("hello"))
print("  in a dict          :", {"double": lambda n: n * 2, "triple": lambda n: n * 3}["triple"](5))
print("  default arg        :", (lambda x, y=10: x + y)(5))

print("\n" + "=" * 60)
print("2. Sorting with key= (the most valuable skill here)")
print("=" * 60)
words = ["banana", "Apple", "cherry", "fig", "Date"]
print("  plain sort        :", sorted(words), " (uppercase first, ASCII order)")
print("  case-insensitive  :", sorted(words, key=str.lower))
print("  by length         :", sorted(words, key=len))
print("  length then alpha :", sorted(words, key=lambda w: (len(w), w.lower())))
print("  reverse length    :", sorted(words, key=lambda w: -len(w)))

people = [
    {"name": "Ravi", "age": 21, "score": 88},
    {"name": "Priya", "age": 22, "score": 95},
    {"name": "Asha", "age": 21, "score": 95},
    {"name": "Dev", "age": 23, "score": 70},
]
print("\n  by age            :", [p["name"] for p in sorted(people, key=lambda p: p["age"])])
print("  score desc, name asc:",
      [p["name"] for p in sorted(people, key=lambda p: (-p["score"], p["name"]))])
print("  itemgetter('age') :", [p["name"] for p in sorted(people, key=itemgetter("age", "name"))])

scores = {"ravi": 88, "priya": 95, "asha": 72}
print("\n  dict by value     :", sorted(scores.items(), key=lambda kv: -kv[1]))
print("  top scorer        :", max(scores, key=scores.get))
print("  sorted keys       :", sorted(scores))
print("  sorted values     :", sorted(scores.values()))

print("\n  stability: equal keys keep their original order")
pairs = [("b", 1), ("a", 1), ("c", 0)]
print("   sorted by 2nd only:", sorted(pairs, key=itemgetter(1)))

print("\n" + "=" * 60)
print("3. map / filter / any / all / max with key")
print("=" * 60)
print("  map(str, [1,2,3])        :", list(map(str, [1, 2, 3])))
print("  map(pow, [2,3], [3,2])   :", list(map(pow, [2, 3], [3, 2])))
print("  filter(odd, 0..9)        :", list(filter(lambda n: n % 2, range(10))))
print("  filter(None, mixed)      :", list(filter(None, [0, 1, "", "x", None, []])))
print("  any startswith('p')      :", any(w.startswith("p") for w in words))
print("  all len <= 6             :", all(len(w) <= 6 for w in words))
print("  max by score             :", max(people, key=lambda p: p["score"])["name"])
print("  min by score             :", min(people, key=lambda p: p["score"])["name"])
print("  reduce to total score    :", reduce(lambda total, p: total + p["score"], people, 0))
print("  Zip into dict            :", dict(zip(["a", "b"], [1, 2])))

print("\n" + "=" * 60)
print("4. Your first decorator")
print("=" * 60)


def logged(func):
    """Print before/after every call. functools.wraps keeps the metadata."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"    -> calling {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"    <- {func.__name__} returned {result!r}")
        return result

    return wrapper


@logged
def add_student(name, marks=0):
    """Add a student and return their record."""
    return {"name": name, "marks": marks}


add_student("Prathamesh", 88)
print("  metadata survived :", add_student.__name__, "|", add_student.__doc__)


def timed(func):
    """Measure how long the function takes. This is how real profilers start."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"    {func.__name__} took {elapsed:.2f} ms")
        return result

    return wrapper


@timed
def slow_sum(n):
    return sum(range(n))


slow_sum(2_000_000)
slow_sum(10)


def repeat(times):
    """A decorator WITH arguments: repeat(3) must return a decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def greet(name):
    return f"Hi {name}"


print("  @repeat(3):", greet("Ravi"), "(ran 3 times)")

print("\n" + "=" * 60)
print("5. Memoisation: lru_cache vs hand-rolled vs none")
print("=" * 60)


def fib_naive(n):
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


def memoize(func):
    """Hand-rolled version, so you know what lru_cache does for you."""
    store = {}

    @wraps(func)
    def wrapper(*args):
        if args not in store:
            store[args] = func(*args)
        return store[args]

    return wrapper


@memoize
def fib_mine(n):
    return n if n < 2 else fib_mine(n - 1) + fib_mine(n - 2)


for label, func in [("naive", fib_naive), ("lru_cache", fib_cached), ("hand-rolled", fib_mine)]:
    start = time.perf_counter()
    value = func(30)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  {label:<12} fib(30) = {value:<10} in {elapsed:8.2f} ms")
print("  cache_info:", fib_cached.cache_info())

print("\n" + "=" * 60)
print("6. Closures")
print("=" * 60)


def make_multiplier(factor):
    """Return a function that remembers `factor`."""
    def multiply(n):
        return n * factor
    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)
print("  double(5) =", double(5), "| triple(5) =", triple(5))


def make_counter(start=0):
    """State that survives between calls, without a global variable."""
    count = start

    def next_value():
        nonlocal count          # rebind the enclosing variable, not a new local
        count += 1
        return count

    return next_value


counter = make_counter(10)
print("  counter():", counter(), counter(), counter())

print("\n" + "=" * 60)
print("7. Putting it together: rank a leaderboard")
print("=" * 60)
raw_scores = "ravi:88 priya:95 asha:72 dev:95 meera:61"
scores = {name: int(value) for name, value in (pair.split(":") for pair in raw_scores.split())}
print("  scores     :", scores)
ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
print("  ranked     :", ranked)
for rank, (name, score) in enumerate(ranked, start=1):
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "  ")
    print(f"   {medal} {rank}. {name:<8} {score}")
print("  average    :", round(sum(scores.values()) / len(scores), 2))
print("  count of 95s:", Counter(scores.values())[95])

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Sort ["python", "C", "javascript", "go"] by length, then alphabetically.
# 2. Sort a list of (name, score) tuples by score descending, name ascending.
# 3. Given students as dicts, print the top 3 by an "average" field.
# 4. Write `@validate_positive` that raises ValueError if any numeric argument
#    is <= 0, otherwise calls the function normally.
# 5. Write `@count_calls` that counts how many times a function has been called
#    and exposes it as `func.calls`.
# 6. Use lru_cache on a recursive coin-change solver and compare timings with
#    the naive version for amount=30.
# 7. Write `make_accumulator()` returning a function that adds to a running
#    total and returns it (closure with `nonlocal`).
# 8. Sort word frequencies by (count desc, word asc) in one `sorted()` call.
print()
print("Lesson 15 done — now do exercises/ex_15_lambdas.py ✅")
