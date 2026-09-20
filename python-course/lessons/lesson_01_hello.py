"""
LESSON 01 · Hello, Python

# What is Python?

Python is a programming language you write in plain text files. You tell the
computer what to do, line by line, top to bottom. That's it. There is no magic.

# Running a program

Three ways, all of them useful:

1. Save a file `hello.py` and run it from the terminal:

       python3 hello.py

2. Use the interactive shell (REPL) — type `python3` with no file, then type
   code directly. Great for quick experiments. Exit with `exit()`.

3. In this course: press Run in the playground.

# print()

`print()` shows something on the screen. Whatever you put between the
parentheses gets displayed.

    print("Hello, world")     -> Hello, world
    print(2 + 2)              -> 4

Text must be inside quotes (`"like this"` or `'like this'`). Numbers don't.
`print` can take many values separated by commas; Python inserts a space.

# Comments

Lines starting with `#` are ignored by Python. They are for humans — you.
Comments are how you leave notes for your future self. Write them.

# Errors are your friends

You *will* see red text like:

    Traceback (most recent call last):
      File "hello.py", line 3, in <module>
        print("hi"
              ^^^^^^
    SyntaxError: '(' was never closed

Read a traceback from the BOTTOM up:

* the last line = the type of error and a description -> `SyntaxError`
* the line above = the exact code Python choked on, with a `^^^` pointer
* the lines above that = where it happened (file + line number)

Nobody memorises error names. You read them, you google them, you fix them
and you move on. 90% of programming is reading error messages carefully.

# Your turn (before scrolling down, predict the output)

1. What does `print("2" + "3")` print?
2. What does `print(2 + 3)` print?
3. What happens with `print("2" + 3)`?
"""

# ---------------------------------------------------------------------------
# 1. Your very first line of Python
# ---------------------------------------------------------------------------
print("Hello, Prathamesh!")          # anything after # is a comment
print("You are now a programmer.")   # (well... in training 🙂)

# ---------------------------------------------------------------------------
# 2. print() can take several things at once — it puts a space between them
# ---------------------------------------------------------------------------
print("Python", "is", "fun")

# ---------------------------------------------------------------------------
# 3. Numbers vs text (called "strings")
# ---------------------------------------------------------------------------
print(2 + 3)        # 5   -> these are numbers, so Python adds them
print("2" + "3")    # 23  -> these are text, so Python glues them together
print("2" * 3)      # 222 -> text times a number repeats the text
# print("2" + 3)    # <- uncomment this line, run it, and READ the error!

# ---------------------------------------------------------------------------
# 4. print has superpowers you will use forever
# ---------------------------------------------------------------------------
print("a", "b", "c", sep="-")        # sep = what goes *between* values
print("no newline...", end="")       # end = what goes *after* (default "\n")
print("and I'm on the same line")

# ---------------------------------------------------------------------------
# 5. print always gives you back the special value None
#    (None means "no value" — Python will print it for you here)
# ---------------------------------------------------------------------------
print("the result of print(...) is:", print("   (inner print)"))

# ---------------------------------------------------------------------------
# 6. A tiny program that actually does something
# ---------------------------------------------------------------------------
name = "Prathamesh"                  # a variable: a labelled box holding a value
goal = "solve basic DSA"
print()
print("=" * 40)
print(f"{name} wants to learn Python and {goal}.")
print(f"Today: {len(goal)} characters of ambition. 🚀")
print("=" * 40)

# f-strings (the f before the quote) let you drop variables straight into text
# with {curly braces}. We will use them constantly — see lesson 02.

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES — try each in the playground, one at a time
# ---------------------------------------------------------------------------
# 1. Print your name, then your city, on two separate lines.
# 2. Print a 5x5 square of stars using only print + multiplication:
#        *****
#        *****
#        ...
# 3. Print this exact box (hint: use sep, or build it with "*" * n):
#        +--------+
#        | Python |
#        +--------+
# 4. Break it on purpose: add a line with a missing closing quote, run it, and
#    find the line number in the traceback. Then fix it.
# 5. Print:  Python says "hi"        <- you need to escape the inner quotes.
#    (Hint: use single quotes around the whole thing.)
print()
print("Lesson 01 done — now do exercises/ex_01_basics.py ✅")
