"""
LESSON 05 · Making decisions (if / elif / else)

# The shape

    if condition:
        do_this()            # indented = "inside the if"
    elif another_condition:
        do_that()
    else:
        do_something_else()

Rules:
* `if` needs a **colon**.
* The body must be **indented** (4 spaces is the standard). Indentation is not
  decoration in Python — it IS the structure. Mixing tabs and spaces gives you
  `TabError` or `IndentationError`; configure your editor to insert 4 spaces.
* Conditions are evaluated top to bottom; the FIRST true branch runs, the rest
  are skipped entirely.
* An `if` without a matching `True` and without `else` simply does nothing.

# Building conditions

    if score >= 90: ...
    if name == "Ravi" and age > 18: ...
    if not is_empty: ...
    if 0 <= index < len(items): ...     # chained
    if value in (1, 2, 3): ...
    if "a" in text: ...

Truthiness again: `if items:` is the Pythonic way to say "if the list is not
empty". Writing `if len(items) > 0:` works but is frowned upon.

# Nesting vs. early exit

Nested ifs get ugly fast:

    if user is not None:
        if user.is_active:
            if user.has_permission:
                do_work()

Flat, "guard clause" style is easier to read:

    if user is None:
        return
    if not user.is_active:
        return
    if not user.has_permission:
        return
    do_work()

# Ternary (conditional expression) — for simple either/or values

    label = "pass" if score >= 40 else "fail"

Use it when it fits on one line and stays readable, not for side effects.

# match / case  (Python 3.10+)

A readable multi-way branch, great for commands and "kinds of things":

    match command:
        case "add": ...
        case "remove": ...
        case "quit" | "exit": ...      # OR on one line
        case _: ...                    # default (the wildcard)

# Comparison chaining trap

    if x == 1 or 2:        # WRONG: always true (2 is truthy)
    if x == 1 or x == 2:   # right
    if x in (1, 2):        # nicer

# Indentation errors to recognise
    IndentationError: expected an indented block
    IndentationError: unindent does not match any outer indentation level
"""

print("=" * 60)
print("1. If / elif / else")
print("=" * 60)

def grade(score):
    """Return a letter grade. Note the order: strongest condition first."""
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"

for score in [95, 82, 61, 39, -5, 100, 74]:
    print(f"  score {score:>4} -> {grade(score)}")

print("\n" + "=" * 60)
print("2. Combining conditions")
print("=" * 60)

def can_watch_movie(age, has_ticket, is_with_parent):
    return has_ticket and (age >= 18 or is_with_parent)

cases = [(20, True, False), (15, True, False), (15, True, True), (30, False, False)]
for age, ticket, parent in cases:
    print(f"  age={age:>2} ticket={ticket!s:5} parent={parent!s:5} "
          f"-> can watch: {can_watch_movie(age, ticket, parent)}")

print("\n" + "=" * 60)
print("3. Truthiness in conditions")
print("=" * 60)
for value in [0, 1, "", "hi", [], [0], None, {}, set()]:
    print(f"  if {value!r:6} -> {'truthy' if value else 'falsy'}")

print("\n" + "=" * 60)
print("4. Guard clauses vs nesting (same logic, better shape)")
print("=" * 60)

def describe_score_nested(score):
    if score is not None:
        if 0 <= score <= 100:
            if score >= 90:
                return "excellent"
            else:
                return "ok"
        else:
            return "out of range"
    else:
        return "missing"

def describe_score_flat(score):
    if score is None:
        return "missing"
    if not 0 <= score <= 100:
        return "out of range"
    if score >= 90:
        return "excellent"
    return "ok"

for score in [95, 70, 150, None]:
    assert describe_score_nested(score) == describe_score_flat(score)
    print(f"  score={score!s:>5} -> {describe_score_flat(score)}")

print("\n" + "=" * 60)
print("5. Ternary expressions")
print("=" * 60)
for score in [30, 55]:
    label = "pass" if score >= 40 else "fail"
    print(f"  {score} -> {label}")
numbers = [4, 9, 2]
print("  biggest:", max(numbers), "even?" , "even" if max(numbers) % 2 == 0 else "odd")

print("\n" + "=" * 60)
print("6. match / case (Python 3.10+)")
print("=" * 60)

def handle(command):
    match command.split():
        case ["quit"]:
            return "bye 👋"
        case ["add", *items]:              # "add milk eggs" -> items = [milk, eggs]
            return f"adding {len(items)} item(s): {', '.join(items)}"
        case ["remove", item]:
            return f"removing {item}"
        case _:
            return "unknown command"

for command in ["quit", "add milk eggs", "remove bread", "dance"]:
    print(f"  {command!r:22} -> {handle(command)}")

print("\n" + "=" * 60)
print("7. A real mini-program: simple login flow")
print("=" * 60)

def login(username, password, attempts):
    if attempts >= 3:
        return "🔒 account locked"
    elif not username:
        return "🚫 enter a username"
    elif len(password) < 8:
        return "⚠️  password too short (min 8 chars)"
    elif password == username:
        return "⚠️  password must differ from username"
    else:
        return "✅ welcome back!"

for args in [("ravi", "supersecret", 0), ("ravi", "short", 0), ("", "whatever123", 1),
             ("ravi", "supersecret", 3), ("ravi", "ravi", 0)]:
    print(f"  {args} -> {login(*args)}")

print("\n" + "=" * 60)
print("8. The classic trap")
print("=" * 60)
x = 5
print("x == 1 or 2 :", "True (WRONG logic!)" if (x == 1 or 2) else "False")
print("x in (1, 2) :", x in (1, 2), " <- this is what you meant")
print("1 == 1.0   :", 1 == 1.0, " <- numbers compare by value, not type")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Write `fizzbuzz_one(n)` that returns "FizzBuzz", "Fizz", "Buzz" or the
#    number as a string, using if/elif/else. (Check 15 before 3 and 5!)
# 2. Write `triangle_type(a, b, c)` -> "equilateral" | "isosceles" |
#    "scalene" | "not a triangle" (sum of any two sides > third side).
# 3. Write `leap_year(year)` -> True/False. Rule: divisible by 4, except
#    centuries, except every 400 years.
# 4. Write `tax_bracket(income)` with at least 4 slabs and test 6 incomes.
# 5. Write `rock_paper_scissors(p1, p2)` returning "tie", "p1" or "p2", using
#    a match statement.
print()
print("Lesson 05 done — now do exercises/ex_05_conditions.py ✅")
