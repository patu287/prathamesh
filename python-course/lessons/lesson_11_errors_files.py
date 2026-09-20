"""
LESSON 11 · Errors, exceptions & files

# Two kinds of problems

1. **Syntax errors** — Python cannot even parse the file. The program never
   starts. Fix the typo.
       print("hi"     -> SyntaxError: '(' was never closed

2. **Exceptions** — the program starts, then hits something it cannot do.
       int("abc")            -> ValueError
       [1, 2][10]            -> IndexError
       {"a": 1}["b"]         -> KeyError
       None + 1              -> TypeError
       10 / 0                -> ZeroDivisionError
       open("nope.txt")      -> FileNotFoundError
       nums.remove(9)        -> ValueError: list.remove(x): x not in list

An unhandled exception prints a traceback and stops the program. Read the LAST
line first (error type + message), then find the first line of *your* code in
the traceback — that is where to look.

# try / except

    try:
        risky = int(user_input)
    except ValueError:
        print("That's not a number")
    except (ZeroDivisionError, OverflowError) as exc:     # several at once
        print("math problem:", exc)
    except Exception as exc:                              # catch-all (last resort)
        print("unexpected:", type(exc).__name__, exc)
    else:
        print("ran with no exception")                    # optional
    finally:
        print("always runs — good place to close things")

Rules of thumb:
* Catch the *specific* exception you can actually handle.
* Never write a bare `except:` that swallows everything and hides bugs.
* Only catch what you can recover from; otherwise let it crash loudly.
* `except Exception` catches normal errors but not `KeyboardInterrupt`/`SystemExit`.

# Raising your own errors

    def set_age(age):
        if not isinstance(age, int):
            raise TypeError("age must be an int")
        if age < 0:
            raise ValueError("age cannot be negative")
        return age

Raise early with a clear message — you will thank yourself later.

# Custom exception classes (lesson 14 shows classes properly)

    class NotEnoughBalance(Exception):
        # a short docstring explaining WHEN it is raised
        "Raised when a withdrawal exceeds the balance."

    raise NotEnoughBalance("balance too low")

# assert — for internal checks, not user input

    assert len(items) > 0, "items cannot be empty"

Assertions can be disabled with `python -O`, so never use them for validation.

# EAFP vs LBYL — the Python style

    LBYL (look before you leap):        EAFP (easier to ask forgiveness):
        if key in d:                        try:
            value = d[key]                      value = d[key]
        else:                               except KeyError:
            value = None                        value = None

Python code usually prefers EAFP — but for dicts, `.get()` beats both.

# Files

    f = open("notes.txt", "w")     # modes: "r" read, "w" overwrite, "a" append,
    f.write("hi\n")                #        "x" create-if-absent, "rb"/"wb" binary
    f.close()

Always prefer `with` — it closes the file even if an exception happens:

    with open("notes.txt", "w", encoding="utf-8") as f:
        f.write("hello\n")

    with open("notes.txt", encoding="utf-8") as f:
        for line in f:                     # one line at a time (memory friendly)
            print(line.rstrip())

    with open("notes.txt", encoding="utf-8") as f:
        content = f.read()                 # whole file as one string
        f.seek(0)
        lines = f.readlines()              # list of lines (keeps "\n")

Handy: `pathlib.Path` (modern, no manual paths)

    from pathlib import Path
    path = Path("data/notes.txt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("hi\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    path.exists(), path.suffix, path.stem, path.name

Text encoding: pass `encoding="utf-8"` explicitly. Without it you inherit your
OS locale and produce mojibake on someone else's machine.

# Working with JSON (structured data files)

    import json
    data = {"name": "Ravi", "scores": [88, 92]}
    json.dumps(data, indent=2)             # dict -> JSON string
    json.loads('{"a": 1}')                 # JSON string -> dict
    json.dump(data, f, indent=2)           # write straight to a file
    json.load(f)                           # read straight from a file

# Reading input that might be garbage (very DSA-relevant)

    def safe_int(text, default=0):
        try:
            return int(text)
        except (TypeError, ValueError):
            return default
"""

import json
import pathlib
import tempfile

print("=" * 60)
print("1. Reading exceptions instead of fearing them")
print("=" * 60)
examples = [
    ("int('abc')", lambda: int("abc")),
    ("[1,2][10]", lambda: [1, 2][10]),
    ("{'a': 1}['b']", lambda: {"a": 1}["b"]),
    ("1 / 0", lambda: 1 / 0),
    ("None + 1", lambda: None + 1),
    ("int(None)", lambda: int(None)),
]
for label, thunk in examples:
    try:
        thunk()
    except Exception as exc:                          # noqa: BLE001 - demo
        print(f"  {label:18} -> {type(exc).__name__}: {exc}")

print("\n" + "=" * 60)
print("2. try / except / else / finally")
print("=" * 60)


def parse_age(text):
    """Return an int age, or explain what went wrong."""
    try:
        age = int(text)
    except ValueError:
        return f"{text!r} is not a whole number"
    except TypeError:
        return f"{text!r} has the wrong type"
    else:
        if age < 0:
            return "age cannot be negative"
        return age


for value in ["21", "abc", None, "-5", "3.5"]:
    print(f"  parse_age({value!r:8}) -> {parse_age(value)}")


def demonstrate_finally():
    try:
        return "from try"
    finally:
        print("    finally still runs before the function really returns")


print(" ", demonstrate_finally())

print("\n" + "=" * 60)
print("3. Raising your own errors (and validating input)")
print("=" * 60)


def set_quantity(quantity):
    """Validate inputs loudly and early."""
    if not isinstance(quantity, int):
        raise TypeError(f"quantity must be an int, got {type(quantity).__name__}")
    if quantity < 1:
        raise ValueError(f"quantity must be >= 1, got {quantity}")
    return quantity


for candidate in [3, 0, "three"]:
    try:
        print(f"  set_quantity({candidate!r}) ->", set_quantity(candidate))
    except (TypeError, ValueError) as exc:
        print(f"  set_quantity({candidate!r}) -> {type(exc).__name__}: {exc}")


class NotEnoughBalance(Exception):
    """Custom exception: too much money requested."""


class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise NotEnoughBalance(f"balance {self.balance} < requested {amount}")
        self.balance -= amount
        return self.balance


account = BankAccount(100)
print("  withdraw(30) ->", account.withdraw(30))
try:
    account.withdraw(1000)
except NotEnoughBalance as exc:
    print("  withdraw(1000) ->", type(exc).__name__, "-", exc)

print("\n" + "=" * 60)
print("4. Safe conversion helpers (used in real DSA input parsing)")
print("=" * 60)


def safe_int(text, default=0):
    """Never crash on bad input."""
    try:
        return int(text)
    except (TypeError, ValueError):
        return default


def safe_divide(a, b):
    """Return None instead of exploding."""
    try:
        return a / b
    except ZeroDivisionError:
        return None
    except TypeError:
        return None


print("  safe_int('42') =", safe_int("42"), "| safe_int('x', -1) =", safe_int("x", -1))
print("  safe_divide(10, 3) =", round(safe_divide(10, 3), 3), "| safe_divide(1, 0) =", safe_divide(1, 0))

print("\n" + "=" * 60)
print("5. assert — internal sanity checks")
print("=" * 60)


def average(nums):
    assert nums, "average() needs at least one number"
    return sum(nums) / len(nums)


print("  average([1, 2, 3]) =", average([1, 2, 3]))
try:
    average([])
except AssertionError as exc:
    print("  average([]) -> AssertionError:", exc)

print("\n" + "=" * 60)
print("6. Files: write, append, read")
print("=" * 60)
workdir = pathlib.Path(tempfile.gettempdir()) / "python_course_files_demo"
workdir.mkdir(parents=True, exist_ok=True)
path = workdir / "notes.txt"

with open(path, "w", encoding="utf-8") as f:      # "w" erases existing content
    f.write("line one\n")
    f.write("line two\n")
print("  wrote:", path)

with open(path, "a", encoding="utf-8") as f:      # "a" appends
    f.write("line three (appended)\n")

with open(path, encoding="utf-8") as f:           # "r" is the default mode
    content = f.read()
print("  read() gives the whole file:")
for line in content.splitlines():
    print("   |", line)

with open(path, encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]     # streaming, line by line
print("  streaming lines:", lines)
print("  number of lines:", len(lines))

print("\n" + "=" * 60)
print("7. pathlib: the modern, cross-platform way")
print("=" * 60)
p = pathlib.Path(workdir) / "scores.csv"
p.write_text("ravi,88\npriya,95\n", encoding="utf-8")
print("  name/suffix/stem/parent:", p.name, p.suffix, p.stem, p.parent.name)
print("  exists():", p.exists(), "| size:", p.stat().st_size, "bytes")
print("  read back:", repr(p.read_text(encoding="utf-8")))

print("\n" + "=" * 60)
print("8. Parsing structured text into Python")
print("=" * 60)
rows = []
for line in p.read_text(encoding="utf-8").splitlines():
    name, score = line.split(",")
    rows.append({"name": name, "score": int(score)})
print("  parsed:", rows)
print("  best  :", max(rows, key=lambda row: row["score"]))
print("  mean  :", sum(row["score"] for row in rows) / len(rows))

print("\n" + "=" * 60)
print("9. JSON: dict <-> text")
print("=" * 60)
data = {"learner": "Prathamesh", "topics": ["loops", "dicts"], "progress": 0.5}
as_text = json.dumps(data, indent=2)
print(as_text)
json_path = workdir / "progress.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
with open(json_path, encoding="utf-8") as f:
    loaded = json.load(f)
print("  round-tripped:", loaded == data, "->", loaded["topics"])

# clean up the demo files
for leftover in workdir.glob("*"):
    leftover.unlink()
workdir.rmdir()
print("\n  (demo files cleaned up)")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Write `divide(a, b)` that returns the result or the string "undefined"
#    when b is 0, using try/except.
# 2. Write `parse_int_list(text)` -> [int] for "1, 2, x, 4", skipping bad items.
# 3. Write a function that raises ValueError with a helpful message when given
#    an empty string, and prove it works with try/except.
# 4. Write a file `todo.txt` with three tasks; then read it back and print each
#    task as "1. task" using enumerate.
# 5. Save a list of dicts to JSON, reload it, and print the total of a numeric
#    field.
# 6. Write `safe_get(d, key, default=None)` without using `.get()` (try/except).
# 7. Write `is_numberish(text)` -> True for "42", "3.14", "-7", False for
#    "abc", "", "4a" (use float() inside try/except).
print()
print("Lesson 11 done — now do exercises/ex_11_errors_files.py ✅")
