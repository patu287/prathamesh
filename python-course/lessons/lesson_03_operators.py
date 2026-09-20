"""
LESSON 03 · Numbers & operators

# Arithmetic

| Operator | Name               | Example     | Result | Note |
|----------|--------------------|-------------|--------|------|
| `+`      | add                | `7 + 2`     | `9`    | on strings: glue |
| `-`      | subtract           | `7 - 2`     | `5`    | |
| `*`      | multiply           | `7 * 2`     | `14`   | on strings: repeat |
| `/`      | divide             | `7 / 2`     | `3.5`  | **always** gives a float |
| `//`     | floor divide       | `7 // 2`    | `3`    | drops the fraction |
| `%`      | modulo (remainder) | `7 % 2`     | `1`    | the star of DSA |
| `**`     | power              | `2 ** 10`   | `1024` | also `pow(2, 10)` |

Careful with negatives: `//` rounds *down* (toward minus infinity) and `%`
follows the sign of the **divisor**:

    -7 // 2  -> -4      (not -3!)
    -7 % 2   -> 1
    7 % -2   -> -1

# Why `%` matters so much

* even/odd: `n % 2 == 0`
* every k-th element: `i % k == 0`
* wrap around an array: `(i + 1) % len(arr)`
* digit extraction: `n % 10` gives the last digit

# Comparison operators

`==` equal · `!=` not equal · `<` `<=` `>` `>=`
They produce `True` or `False`. **`==` compares, `=` assigns.** Mixing them up
is the classic beginner bug.

Chained comparison (very Pythonic):

    0 <= score <= 100      # True/False, works like math

# Logical operators

`and` (both true) · `or` (at least one true) · `not` (flip)

    age >= 18 and has_id
    name == "a" or name == "b"

`and`/`or` return one of their *operands*, not necessarily True/False:

    5 or 3       -> 5        (first truthy value)
    0 or 3       -> 3
    "a" and "b"  -> "b"      (last value if all truthy)

This "short-circuit" behaviour enables idioms like:

    name = user_input or "guest"     # default value if input is empty

# Truthiness

Everything has a truth value. Falsy values (everything else is truthy):

    False, None, 0, 0.0, "", [], {}, set(), ()

So `if my_list:` means "if the list is not empty".

# Augmented assignment

    total += 5      # total = total + 5
    total -= 2 ,  *= 3 ,  /= 4 ,  //= 2 ,  %= 3 ,  **= 2
Python has no `x++` / `x--`. Use `x += 1`.

# Floats are approximate (important!)

    0.1 + 0.2 == 0.3      -> False   (it is 0.30000000000000004)
    round(0.1 + 0.2, 2)   -> 0.3

Real numbers simply cannot be stored exactly in binary. For money use
`round()` or `decimal.Decimal`; for comparisons of floats use a tolerance:

    abs(a - b) < 1e-9

# Integer division: Python ints never overflow
`10 ** 100` works out of the box (other languages overflow at 2^63).
"""

print("=" * 60)
print("1. Arithmetic")
print("=" * 60)
print("7 + 2   =", 7 + 2)
print("7 - 2   =", 7 - 2)
print("7 * 2   =", 7 * 2)
print("7 / 2   =", 7 / 2, "        <- always float")
print("7 // 2  =", 7 // 2, "         <- floor")
print("7 % 2   =", 7 % 2, "         <- remainder")
print("2 ** 10 =", 2 ** 10)
print("divmod(17, 5) =", divmod(17, 5), "  <- (quotient, remainder) in one call")

print()
print("-7 // 2 =", -7 // 2, "| -7 % 2 =", -7 % 2, "| 7 % -2 =", 7 % -2,
      "  <- floor division goes DOWN")

print("\n" + "=" * 60)
print("2. Comparisons")
print("=" * 60)
marks = 78
print("marks == 78 :", marks == 78)
print("marks != 78 :", marks != 78)
print("60 <= marks <= 100 :", 60 <= marks <= 100, "  <- chained, reads like math")

print("\n" + "=" * 60)
print("3. Logical operators and truthiness")
print("=" * 60)
has_ticket = True
age = 20
print("can enter:", age >= 18 and has_ticket)
print("not age >= 18:", not age >= 18, " (parsed as not (age >= 18))")
print("5 or 3 ->", 5 or 3, "| 0 or 3 ->", 0 or 3, "| 'a' and 'b' ->", "a" and "b")
empty_input = ""
print("empty_input or 'guest' ->", empty_input or "guest")

falsy = [False, None, 0, 0.0, "", [], {}, set(), ()]
for value in falsy:
    print(f"   bool({value!r}) = {bool(value)}")

print("\n" + "=" * 60)
print("4. Augmented assignment")
print("=" * 60)
score = 0
score += 10        # score = score + 10
score *= 2         # 20
score -= 5         # 15
score //= 2        # 7
score %= 4         # 3
score **= 3        # 27
print("after the chain:", score)

print("\n" + "=" * 60)
print("5. Nice built-ins for numbers")
print("=" * 60)
values = [-3, 7, 2, 9, -1, 4]
print("abs(-42)      =", abs(-42))
print("round(3.14159, 3) =", round(3.14159, 3))
print("min(values)   =", min(values), "| max(values) =", max(values))
print("sum(values)   =", sum(values))
print("pow(3, 4, 5)  =", pow(3, 4, 5), " = 3**4 % 5  (fast modular power for DSA)")
print("sorted(values, reverse=True) =", sorted(values, reverse=True))

print("\n" + "=" * 60)
print("6. Float precision — know this trap")
print("=" * 60)
print("0.1 + 0.2          =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3   =", 0.1 + 0.2 == 0.3)
print("round(0.1+0.2, 10) == 0.3 ->", round(0.1 + 0.2, 10) == 0.3)
print("abs(x - 0.3) < 1e-9 ->", abs((0.1 + 0.2) - 0.3) < 1e-9)
print("Huge ints are exact:", 2 ** 100)

print("\n" + "=" * 60)
print("7. Real use: extracting digits with % and //")
print("=" * 60)
number = 4729
print("number      :", number)
print("last digit  :", number % 10)          # 9
print("drop last   :", number // 10)         # 472
digits = []
n = number
while n > 0:
    digits.append(n % 10)                   # take the last digit
    n //= 10                                # remove it
print("digit sum   :", sum(digits), "| digits reversed:", digits)

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Given total_seconds = 3725, print it as "1 hour(s) 2 minute(s) 5 second(s)"
#    using // and %  (no loops needed).
# 2. Is 123456789 divisible by 9? Answer with a True/False print of `%`.
# 3. Take a 4-digit number and print its digit sum (do it without a loop first,
#    then with the while-loop pattern above).
# 4. Print the area of a circle with radius 2.5, rounded to 2 decimals.
# 5. Predict before running: `True + True`, `True * 10`, `int(True)`, `-7 % 3`.
#    (Booleans are secretly integers: True == 1, False == 0.)
print()
print("Lesson 03 done — now do exercises/ex_03_operators.py ✅")
