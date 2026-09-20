"""
LESSON 10 · Functions

A function is a named block of code you can call again and again. Functions
are how you stop copy-pasting and start building. From here on, almost every
DSA solution you write will be a function.

# Defining and calling

    def greet(name):            # `def`, name, parameters, colon
        return f"Hi {name}"     # body is indented

    message = greet("Ravi")     # call it: pass arguments, get the return value

* `name` is a **parameter** (the placeholder), `"Ravi"` is an **argument**
  (the actual value).
* `return` sends a value back to the caller and ENDS the function immediately.
* A function with no `return` returns `None`.
* Docstring: a plain string on the first line describing the function.
  Write them — `help(my_func)` shows them, and editors show them on hover.

# Why functions?

1. **Don't repeat yourself.** Write the logic once.
2. **Small pieces are testable** (that is exactly how this course grades you).
3. **Names explain intent**: `is_palindrome(s)` beats a stray while-loop.
4. Recursion (lesson dsa_06) *requires* functions.

# Arguments

    def f(a, b):                       # positional
    def f(a, b=10):                    # b is optional, default 10
    def f(*args):                      # any number of positional args -> tuple
    def f(**kwargs):                   # any number of keyword args -> dict
    def f(a, *, b):                    # b MUST be passed by keyword

    f(1, 2)          positional, order matters
    f(b=2, a=1)      keyword, order does not matter — great for readability
    f(1, b=2)        mixed: positional first, then keyword

**Default argument trap:** never use a mutable default.

    def bad(items=[]):        # the SAME list is shared across every call!
        items.append(1); return items
    bad() -> [1]      bad() -> [1, 1]     😱

    def good(items=None):
        if items is None:
            items = []
        items.append(1); return items

# Scope — where names live

Code inside a function can *read* outer variables, but assigning creates a new
local one. `global` exists; needing it usually means your design is off.

    counter = 0
    def f():
        counter = 5          # local, the outer counter is untouched
    def g():
        global counter; counter = 5   # changes the outer one (avoid)

# Returning more than one value

    def divmod_manual(a, b):
        return a // b, a % b     # returns a tuple

    quotient, remainder = divmod_manual(17, 5)

# Functions are values (this idea unlocks a lot)

    def square(x): return x * x
    func = square              # no parentheses: the function itself
    func(4)                    # 16
    apply_twice = lambda f, x: f(f(x))
    sorted(data, key=len)      # we pass `len` as a value

# Type hints (optional, but they document and enable editor autocomplete)

    def add(a: int, b: int) -> int:
        return a + b

They are NOT enforced at runtime; they are documentation your editor reads.

# Small function design rules

* One job per function. If the name needs "and", split it.
* Avoid printing inside logic functions — **return** the value and let the
  caller decide what to do. (All the graded exercises follow this rule.)
* 4–15 lines is a good size. Deep nesting is a smell: use early returns.
* Name with a verb: `compute_total`, `find_duplicate`, `is_valid`.

# The patterns you will write over and over

    def is_even(n): return n % 2 == 0
    def clamp(value, low, high): return max(low, min(value, high))
    def normalise(text): return text.strip().lower()
"""

print("=" * 60)
print("1. Basic function, docstring, return")
print("=" * 60)


def greet(name, greeting="Hello"):
    """Return a greeting for `name` (default greeting: Hello)."""
    return f"{greeting}, {name}!"


print(greet("Prathamesh"))
print(greet("Ravi", greeting="Namaste"))
print(greet(greeting="Hey", name="Priya"), " <- keyword args, any order")
print("docstring:", greet.__doc__)
print("functions without return give:", type(do_nothing() if False else None).__name__)


def do_nothing():
    """No return statement -> returns None."""
    pass


print("do_nothing() ->", do_nothing())


def early_return(score):
    """`return` exits immediately — the rest of the body is skipped."""
    if score < 0:
        return "invalid"
    return "valid"          # only reached when score >= 0


print("early_return(-5) =", early_return(-5), "| early_return(5) =", early_return(5))

print("\n" + "=" * 60)
print("2. Defaults, *args, **kwargs")
print("=" * 60)


def total(*numbers):
    """Sum any number of arguments (they arrive as a tuple)."""
    print("    args received:", numbers)
    return sum(numbers)


print("total(1, 2, 3)      =", total(1, 2, 3))
print("total()             =", total())


def describe(name, **details):
    """Keyword arguments arrive as a dict."""
    parts = [f"{key}={value}" for key, value in details.items()]
    return f"{name}: " + ", ".join(parts) if parts else name


print(describe("Ravi", age=20, city="Pune"))
print(describe("Priya"))


def unpack_demo(a, b, c):
    return a + b + c


values = [1, 2, 3]
print("* unpacking a list into args:", unpack_demo(*values))
kwargs = {"a": 1, "b": 2, "c": 3}
print("** unpacking a dict       :", unpack_demo(**kwargs))

print("\n" + "=" * 60)
print("3. The mutable default trap")
print("=" * 60)


def bad_append(item, bucket=[]):
    bucket.append(item)
    return bucket


print("bad_append('a') ->", bad_append("a"))
print("bad_append('b') ->", bad_append("b"), " <- the SAME list was reused! 😱")


def good_append(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


print("good_append('a') ->", good_append("a"))
print("good_append('b') ->", good_append("b"), " ✅ fresh list each time")

print("\n" + "=" * 60)
print("4. Scope")
print("=" * 60)
outside = "I am global"
count = 0


def read_only():
    return f"inside can READ: {outside}"


def shadow():
    outside = "I am local"          # a NEW variable, the global is untouched
    return outside


def modify_global():
    global count                    # explicit, and usually a design smell
    count += 1
    return count


print(read_only())
print("shadow() ->", shadow(), "| global still:", outside)
modify_global()
modify_global()
print("count after 2 calls:", count)

print("\n" + "=" * 60)
print("5. Multiple return values")
print("=" * 60)


def min_max_avg(numbers):
    """Return a tuple of three things."""
    if not numbers:
        return None, None, None
    return min(numbers), max(numbers), sum(numbers) / len(numbers)


low, high, average = min_max_avg([7, 2, 9, 4])
print(f"low={low} high={high} average={average:.2f}")
print("as a tuple:", min_max_avg([7, 2, 9, 4]))


def divmod_manual(a, b):
    """Python's built-in divmod already does this — reimplemented for learning."""
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a // b, a % b


print("divmod_manual(17, 5) =", divmod_manual(17, 5))

print("\n" + "=" * 60)
print("6. Functions are values")
print("=" * 60)


def square(x):
    return x * x


def cube(x):
    return x ** 3


for operation in (square, cube):
    print(f"  {operation.__name__}(3) = {operation(3)}")

print("passing len as a key:", sorted(["bbb", "a", "cc"], key=len))
print("built-ins that take functions: map, filter, sorted, max, min, any, all")
print("  max by length:", max(["a", "bbb", "cc"], key=len))
print("  list(map(square, [1,2,3])):", list(map(square, [1, 2, 3])))
print("  list(filter(lambda n: n % 2, [1,2,3,4])):", list(filter(lambda n: n % 2, [1, 2, 3, 4])))

print("\n" + "=" * 60)
print("7. Type hints (documentation your editor understands)")
print("=" * 60)


def average(marks: list[float]) -> float:
    """Type hints do not change runtime behaviour, but editors use them."""
    return sum(marks) / len(marks)


def is_adult(age: int) -> bool:
    return age >= 18


print("average([1, 2, 3]) =", average([1, 2, 3]))
print("is_adult(20) =", is_adult(20), "| is_adult(12) =", is_adult(12))
print("hints:", average.__annotations__)

print("\n" + "=" * 60)
print("8. Building a small program out of small functions")
print("=" * 60)


def is_prime(n: int) -> bool:
    """Trial division up to sqrt(n). O(sqrt(n))."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def primes_up_to(limit: int) -> list[int]:
    return [n for n in range(2, limit + 1) if is_prime(n)]


print("primes up to 50:", primes_up_to(50))
print("sum of first 10 primes:", sum(primes_up_to(29)))

print("\n" + "=" * 60)
print("9. Recursion preview (full lesson in dsa_06)")
print("=" * 60)


def factorial(n: int) -> int:
    """n! = n * (n-1)! with a base case that stops the recursion."""
    if n <= 1:                      # base case — every recursion needs one
        return 1
    return n * factorial(n - 1)     # recursive case, smaller input


def fibonacci(n: int, memo: dict | None = None) -> int:
    """Naive recursion is exponential; memoising makes it linear."""
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]


print("factorial(5) =", factorial(5), "| factorial(20) =", factorial(20))
print("fib(10) =", fibonacci(10), "| fib(50) =", fibonacci(50))

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `apply_twice(func, value)` -> func(func(value)). Test with square/cube.
# 2. `sum_all(*numbers)` and `biggest(*numbers)` using *args.
# 3. `swap(a, b)` returning (b, a) — then show a, b = swap(a, b) works.
# 4. `apply_discount(price, percent=10)` returning the new price.
# 5. `stats(numbers)` returning (count, sum, min, max, average) and print them
#    unpacked.
# 6. `is_leap(year)` and `days_in_month(year, month)` — one uses the other.
# 7. Fix this function and explain the bug in a comment:
#       def add_tag(tag, tags=[]):
#           tags.append(tag); return tags
# 8. `make_counter()` returning a function that counts up on each call.
#    (Closures! Don't worry if it takes a while — it is a nice brain-stretch.)
print()
print("Lesson 10 done — now do exercises/ex_10_functions.py ✅")
