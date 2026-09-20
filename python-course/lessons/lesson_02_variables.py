"""
LESSON 02 · Variables, types & input

# Variables

A variable is a labelled box that holds a value.

    age = 21          # "age" now holds the number 21
    name = "Priya"    # "name" now holds the text Priya

`=` is **assignment**: right side is computed, then stored in the name on the
left. Read it as "gets". `age = age + 1` means "age gets age + 1".

Rules for names: letters, digits, underscore; cannot start with a digit;
cannot be a keyword (`if`, `for`, `class`, ...). Python style is
`snake_case` for variables and `UPPER_CASE` for constants.
`total_price` is good. `totalPrice`, `TotalPrice` are legal but un-Pythonic.

# The core types

| Type    | Meaning                | Examples                     |
|---------|------------------------|------------------------------|
| `int`   | whole numbers          | `0`, `7`, `-3`, `10**50`     |
| `float` | decimal numbers        | `3.14`, `-0.5`, `2.0`        |
| `str`   | text                   | `"hi"`, `'hi'`, `"2"`        |
| `bool`  | truth values           | `True`, `False`              |
| `None`  | "nothing / no value"   | `None`                       |

Python is **dynamically typed**: the type belongs to the *value*, not to the
variable. The same variable can hold a number now and text later. (That is
legal, not always wise.)

Check any value's type with `type(x)`.

# Converting between types (very important!)

    int("42")     -> 42          # text -> number
    str(42)       -> "42"        # number -> text
    float(3)      -> 3.0
    int(3.9)      -> 3           # truncates toward zero, it does NOT round
    round(3.9)    -> 4
    int("hi")     -> ValueError: invalid literal for int() with base 10: 'hi'

# input() always gives you text

    age = input("Age? ")     # if the user types 20, age is the STRING "20"
    age = int(input("Age? "))  # convert immediately -> int
    age = float(input("Pace? "))  # for decimals use float

Rule: `input()` returns `str`, always, no exceptions. Remember that and you
will avoid the most common beginner bug.

# f-strings — your main way to build text

    name, age = "Ravi", 20
    print(f"{name} is {age} years old")     # Ravi is 20 years old

Inside the `{}` you can put any expression, and format values:

    f"{3.14159:.2f}"   -> 3.14      (2 decimals)
    f"{42:5d}"         -> "   42"   (width 5)
    f"{0.25:.0%}"      -> 25%
    f"{name!r}"        -> 'Ravi'    (developer-friendly repr)
"""

# ---------------------------------------------------------------------------
# A helper that behaves like input() but falls back to a default value when
# this file is run without a keyboard attached (e.g. the playground / a test).
# Don't worry about the try/except yet — lesson 11 explains it.
# ---------------------------------------------------------------------------
def ask(prompt, default):
    try:
        answer = input(prompt).strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        return default


# ---------------------------------------------------------------------------
# 1. Variables: assignment is right-to-left
# ---------------------------------------------------------------------------
x = 10
y = x + 5          # y gets 15
x = x * 2          # x gets its own old value times 2  -> 20
print("x =", x, "| y =", y)

# swap two variables — the Pythonic one-liner (no temp variable needed!)
a, b = 1, 2
a, b = b, a
print("after swap: a =", a, "b =", b)

# multiple assignment
width, height = 3, 4
print("area:", width * height)

# ---------------------------------------------------------------------------
# 2. Types — every value has one
# ---------------------------------------------------------------------------
print()
age = 21
price = 199.5
name = "Prathamesh"
is_learning = True
nothing = None

for value in (age, price, name, is_learning, nothing):
    print(f"{value!r:>14}  ->  {type(value).__name__}")

# careful: "21" (text) and 21 (number) are completely different values
print()
print("21 + 1 =", 21 + 1)         # 22
print('"21" + "1" =', "21" + "1")  # 211  (gluing text)
# print("21" + 1)                 # TypeError: can only concatenate str (not "int") to str

# ---------------------------------------------------------------------------
# 3. Conversion
# ---------------------------------------------------------------------------
print()
print('int("42")   =', int("42"))
print("str(42)      =", repr(str(42)))
print("float(7)     =", float(7))
print("int(3.99)    =", int(3.99), "  <-- truncates, does not round")
print('int("101", 2) =', int("101", 2), "  <-- base 2: text -> binary number")

# ---------------------------------------------------------------------------
# 4. Getting text from the user  (input() always returns a string)
# ---------------------------------------------------------------------------
print()
user_name = ask("What's your name? ", "Prathamesh")
user_age = ask("How old are you? ", "21")
# user_age is TEXT. Converting is what makes arithmetic possible:
try:
    age_number = int(user_age)
    years_to_30 = 30 - age_number
    print(f"Hi {user_name}! In {years_to_30} years you'll be 30.")
except ValueError:
    print(f"Hi {user_name}! {user_age!r} is not a number, so I can't do math with it.")

# ---------------------------------------------------------------------------
# 5. f-strings: the formatting toolbox
# ---------------------------------------------------------------------------
print()
pi = 3.14159265
marks = 87
total = 100
print(f"pi to 2 decimals : {pi:.2f}")
print(f"pi to 4 decimals : {pi:.4f}")
print(f"score            : {marks}/{total} = {marks / total:.1%}")
print(f"padded number    : |{42:6d}|{42:06d}|")
print(f"aligned text     : |{name:<12}|{name:>12}|{name:^12}|")
print(f"big numbers      : {1234567890:,}")
print(f"expression inside: {2 ** 10} and {len(user_name)} letters in your name")

# ---------------------------------------------------------------------------
# 6. Naming things well (this skill matters more than you think)
# ---------------------------------------------------------------------------
print()
# BAD:  d = 5; t = d * 0.18
# GOOD:
price_before_tax = 500
tax_rate = 0.18
tax_amount = price_before_tax * tax_rate      # 90.0
price_with_tax = price_before_tax + tax_amount
print(f"₹{price_before_tax} + ₹{tax_amount:.2f} tax = ₹{price_with_tax:.2f}")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Ask the user for two numbers and print their sum, difference, product
#    and quotient. (Remember: convert with int() or float()!)
# 2. Ask for a temperature in Celsius and print it in Fahrenheit:
#        F = C * 9 / 5 + 32
# 3. Ask for a name and a birth year, then print:
#        "Prathamesh is about 24 years old in 2026"
#    using an f-string and integer arithmetic.
# 4. Print the number 7 three ways: as text, as an int, and as a float.
#    Show each one's type() next to it.
# 5. Predict then check: what is `bool(0)`, `bool("0")`, `bool("")`?
#    (Write the answers as comments before you run it.)
print()
print("Lesson 02 done — now do exercises/ex_02_variables.py ✅")
