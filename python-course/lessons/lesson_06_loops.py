"""
LESSON 06 · Loops

Loops are how you do the same thing to many items — the heart of every DSA
solution. If you only master one lesson, make it this one (and lesson 07).

# `for` — "for each item in a collection"

    for item in collection:
        do_something(item)

Python's for loop is a **for-each**: you don't manage an index, you iterate
over the values directly. That is why Python code is short and readable.

    for ch in "abc":        -> a, b, c
    for n in [10, 20]:      -> 10, 20
    for key in {"a": 1}:    -> a   (keys)
    for n in range(5):      -> 0,1,2,3,4

# range(start, stop, step) — stop is EXCLUDED

    range(5)        -> 0 1 2 3 4
    range(2, 6)     -> 2 3 4 5
    range(0, 10, 2) -> 0 2 4 6 8
    range(5, 0, -1) -> 5 4 3 2 1      (count down to 1)
    range(0)        -> empty (loop body never runs — always check this!)

`range` is lazy: it does not build a list. Convert when you need to see it:
`list(range(3)) -> [0, 1, 2]`. Memory-friendly for `range(10**9)`.

# When you actually need the index: enumerate

    for i, value in enumerate(items):
        print(i, value)

    for i, value in enumerate(items, start=1):   # 1-based numbering
Use `enumerate`, not `for i in range(len(items))`, unless you genuinely need
to jump around inside the loop.

# Walking two collections together: zip

    for name, score in zip(names, scores): ...
    zip stops at the shortest input. Pair with `zip(*matrix)` to transpose.

# `while` — "repeat as long as this is true"

    while condition:
        ...

Use it when you don't know how many repetitions you need. Always make sure
something inside the loop moves toward the end, otherwise you get an infinite
loop (Ctrl+C kills a runaway program).

    n = 5
    while n > 0:
        print(n); n -= 1        # n must shrink!

    while True:                 # intentional infinite loop
        line = input()
        if line == "quit":
            break               # exit from inside

# break / continue / else

* `break`    -> leave the loop immediately
* `continue` -> skip the rest of this iteration, go to the next one
* `for ... else:` -> the `else` runs only if the loop ended WITHOUT break.
  Great for "search, and if you never found it..." logic.

    for n in numbers:
        if n == target:
            print("found")
            break
    else:
        print("not found")      # only when the loop was never broken

# Nested loops

    for row in range(3):
        for col in range(3):
            ...        # runs 9 times total (3 * 3)

Cost multiplies: nested loops over n items = O(n²). If you feel tempted to
write two nested loops, first ask: could a dict/set make this a single loop?
(That idea alone unlocks most easy/medium interview problems.)

# Traps

1. Modifying a list while looping over it:
       for x in nums:
           if x % 2 == 0:
               nums.remove(x)     # skips items / wrong results!
   Loop over a copy — `for x in nums[:]:` — or better, build a new list.
2. `for i in range(len(nums))` and then using `nums[i]` everywhere: use
   `enumerate`, or iterate values directly.
3. Off-by-one: `range(1, n)` visits n-1 numbers, not n.
"""

print("=" * 60)
print("1. for over different collections")
print("=" * 60)
print("string :", end=" ")
for ch in "Python":
    print(ch, end=" ")
print()

print("list   :", end=" ")
for n in [10, 20, 30]:
    print(n, end=" ")
print()

print("range  :", end=" ")
for n in range(5):
    print(n, end=" ")
print()

print("dict   :", end=" ")
for key in {"a": 1, "b": 2}:
    print(key, end=" ")
print("  <- keys only")

print("\n" + "=" * 60)
print("2. range() forms")
print("=" * 60)
print("list(range(5))        =", list(range(5)))
print("list(range(2, 6))     =", list(range(2, 6)))
print("list(range(0, 10, 2)) =", list(range(0, 10, 2)))
print("list(range(5, 0, -1)) =", list(range(5, 0, -1)))
print("sum(range(101))       =", sum(range(101)))

print("\n" + "=" * 60)
print("3. enumerate and zip")
print("=" * 60)
tasks = ["wash dishes", "study python", "sleep"]
for number, task in enumerate(tasks, start=1):
    print(f"  {number}. {task}")

names = ["Ravi", "Priya", "Asha"]
scores = [88, 95, 72]
for name, score in zip(names, scores):
    print(f"  {name:<6} scored {score}")

print("  zip stops at the shortest:", list(zip([1, 2, 3], "ab")))

print("\n" + "=" * 60)
print("4. while")
print("=" * 60)
n = 5
print("  countdown:", end=" ")
while n > 0:
    print(n, end=" ")
    n -= 1                      # without this line: infinite loop!
print("liftoff 🚀")

# simulate a menu without real input
commands = ["add", "add", "list", "quit", "add"]
queue = commands[:]
count = 0
while queue:
    command = queue.pop(0)
    if command == "quit":
        print("  quit received, stopping")
        break
    if command == "add":
        count += 1
        continue                # skip the print below
    print(f"  listing {count} item(s)")

print("\n" + "=" * 60)
print("5. for / else — 'search and report'")
print("=" * 60)
def find_index(items, target):
    for index, value in enumerate(items):
        if value == target:
            print(f"  found {target} at index {index}")
            break
    else:
        print(f"  {target} is not in the list")

find_index(["a", "b", "c"], "b")
find_index(["a", "b", "c"], "z")

print("\n" + "=" * 60)
print("6. Nested loops and their cost")
print("=" * 60)
counter = 0
for row in range(3):
    for col in range(3):
        counter += 1
print("  3x3 nested loop ran", counter, "times")

# times-table triangle
for i in range(1, 5):
    print("  " + " ".join(f"{i * j:>3}" for j in range(1, 6)))

print("\n" + "=" * 60)
print("7. Classic loop patterns you will reuse forever")
print("=" * 60)

# a) running total / accumulator
total = 0
for n in [3, 5, 7, 9]:
    total += n
print("  sum accumulator        :", total)

# b) max/min by hand (understand it once, then use max()/min())
best = float("-inf")
for n in [3, 9, 4]:
    if n > best:
        best = n
print("  manual max             :", best)

# c) counting matches
count = 0
for n in [1, 2, 3, 4, 5, 6]:
    if n % 2 == 0:
        count += 1
print("  even numbers           :", count)

# d) "is there any" / "are all"
nums = [4, 8, 15]
print("  any odd?               :", any(n % 2 for n in nums))
print("  all even?              :", all(n % 2 == 0 for n in nums))

# e) search for a pair (and why nested loops are suspect)
target = 11
pairs = []
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            pairs.append((nums[i], nums[j]))
print("  pairs summing to 11    :", pairs, " (O(n²) — dsa_03 fixes this with a dict)")

# f) building output incrementally
stars = ""
for i in range(1, 6):
    stars += "*"                # fine for small n; join() is better for big n
    print("  " + stars)

# g) the number pyramid
for i in range(1, 6):
    print("  " + " " * (5 - i) + "* " * i)

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Print the multiplication table of 7 from 1 to 10.
# 2. Sum all numbers from 1 to 100 that are divisible by 3 or 5.
# 3. Count vowels AND consonants in "The quick brown fox jumps over the lazy dog".
# 4. Print the first 10 Fibonacci numbers with a while loop (a, b = b, a + b).
# 5. Ask the user for numbers until they type "done", then print the average.
#    (Use a while True loop with break. In the playground use a fixed list.)
# 6. Given a list of words, print only the ones longer than 4 letters and
#    count them.
# 7. FizzBuzz 1..30 with a for loop and if/elif/else (the interview warm-up).
# 8. Reverse a number with a while loop: 4729 -> 9274 (use % and //).
print()
print("Lesson 06 done — now do exercises/ex_06_loops.py ✅")
