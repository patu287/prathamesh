"""
LESSON 13 · Modules, the standard library, pip & virtual environments

You will almost never write everything yourself. Python ships with a huge
standard library ("batteries included") and the wider ecosystem is one
`pip install` away. Knowing *which* tool to reach for is a superpower.

# 1. import — four ways

    import math                 # module.attr    -> math.sqrt(16)
    import math as m            # rename         -> m.sqrt(16)
    from math import sqrt, pi   # the names directly -> sqrt(16)
    from math import sqrt as s  # rename one

Prefer `import math` / `import math as m` in real code: `math.sqrt(16)` tells
the reader where `sqrt` came from. `from x import *` is banned for good reason.

# 2. Standard-library modules you will actually use

math                sqrt, floor, ceil, factorial, gcd, log, pi, inf
random              random(), randint(a, b), choice, shuffle, sample, seed
statistics          mean, median, mode, stdev
collections         Counter, defaultdict, deque, OrderedDict, namedtuple
heapq               heappush, heappop, heapify  (priority queues — dsa_10)
bisect              bisect_left, bisect_right, insort  (binary search — dsa_05)
itertools           covered in lesson 12
functools           lru_cache, reduce, partial, cmp_to_key
operator            add, mul, itemgetter, attrgetter (fast key functions)
string              ascii_lowercase, digits, punctuation
datetime            date, datetime, timedelta
pathlib             modern file paths (lesson 11)
json / csv          structured data
re                  regular expressions
os / sys            environment, argv, exit, path
time / datetime     timing; time.perf_counter() is the accurate one
math.gcd            useful in number theory problems

Quick sanity check on the whole list: `import sys; sys.modules` after importing.

# 3. Your own modules — a file is a module

Create `helpers.py`:

    def double(n):
        return n * 2

Then in another file in the SAME directory:

    import helpers
    helpers.double(4)

    from helpers import double
    double(4)

The `if __name__ == "__main__":` guard:

    # helpers.py
    def double(n): return n * 2

    if __name__ == "__main__":
        print(double(3))        # only runs when you execute this file directly,
                                # NOT when another file imports it

Packages are just folders of modules with an `__init__.py`:

    myproject/
        __init__.py
        utils.py
        models.py         ->  from myproject.utils import helper

This course uses exactly that trick: `tools/` is a package, so exercise files
can do `from tools.harness import run_cases`.

# 4. sys.path — how Python finds imports

Python looks in: the script's directory, then PYTHONPATH, then installed
packages. That is why a file next to yours imports fine, but a file two
folders up may need `sys.path.insert(0, ...)`.

# 5. Virtual environments — one venv per project

    python3 -m venv .venv              # create it once
    source .venv/bin/activate          # Linux/macOS
    .venv\\Scripts\\activate             # Windows
    python -m pip install requests     # install into THAT venv only
    pip freeze > requirements.txt      # record exact versions
    pip install -r requirements.txt    # reproduce elsewhere
    deactivate

Why bother? Different projects need different (sometimes conflicting)
versions. A venv keeps them apart and keeps your system Python clean.
Rule: **every project gets its own venv**, and `.venv/` goes in `.gitignore`.

# 6. pip essentials

    python -m pip install <package>       # prefer "python -m pip" (which python!)
    python -m pip list                    # what is installed
    python -m pip show <package>
    python -m pip install --upgrade <pkg>
    python -m pip uninstall <pkg>

Packages worth knowing later: numpy (fast arrays), pandas (dataframes),
requests (HTTP), pytest (testing), flask/fastapi (web), rich (pretty output).

# 7. Running and structuring a project

    python3 script.py arg1 arg2         # sys.argv = ['script.py', 'arg1', 'arg2']
    python3 -m mypackage.module         # run a module inside a package
    python3 -i script.py                # drop into a REPL afterwards
    python3 -m pdb script.py            # the built-in debugger
    python3 -c "print(2**10)"           # run a one-liner

The layout that scales:

    project/
        README.md
        requirements.txt
        pyproject.toml        (modern packaging config)
        src/mypackage/__init__.py, module.py
        tests/test_module.py
"""

import bisect
import heapq
import math
import os
import random
import statistics
import string
import sys
from collections import Counter, defaultdict, deque
from functools import lru_cache, reduce

print("=" * 60)
print("1. import styles")
print("=" * 60)
print("import math                     -> math.sqrt(16) =", math.sqrt(16))
print("from math import pi, gcd        -> pi =", round(math.pi, 5), "gcd(12, 18) =", math.gcd(12, 18))
print("math.inf / -math.inf            ->", math.inf, -math.inf)
print("math.floor / ceil / factorial   ->", math.floor(3.7), math.ceil(3.2), math.factorial(6))

print("\n" + "=" * 60)
print("2. random (seed it to reproduce results)")
print("=" * 60)
random.seed(42)                     # same seed -> same numbers, every run
print("  random()         :", round(random.random(), 4))
print("  randint(1, 6)    :", random.randint(1, 6))
print("  choice(letters)  :", random.choice(string.ascii_uppercase))
print("  sample(range, 3) :", random.sample(range(1, 50), 3))
deck = list(range(1, 11))
random.shuffle(deck)
print("  shuffled deck    :", deck)

print("\n" + "=" * 60)
print("3. statistics")
print("=" * 60)
marks = [88, 92, 79, 95, 70, 88]
print("  mean  :", statistics.mean(marks))
print("  median:", statistics.median(marks))
print("  mode  :", statistics.mode(marks), " (most common)")
print("  stdev :", round(statistics.stdev(marks), 2))

print("\n" + "=" * 60)
print("4. collections: deque (fast at both ends)")
print("=" * 60)
queue = deque([1, 2, 3])
queue.append(4)          # O(1)  (a list also does this)
queue.appendleft(0)      # O(1)  (a list would be O(n)!)
print("  deque            :", queue)
print("  popleft / pop    :", queue.popleft(), queue.pop(), "->", queue)
print("  rotate(1)        :", (queue.rotate(1), queue)[1])
print("  maxlen demo      :", deque([1, 2, 3, 4], maxlen=3), " (keeps the last 3)")

print("\n  A deque is the correct tool for BFS queues and sliding windows.")

print("\n" + "=" * 60)
print("5. heapq — a priority queue in O(log n)")
print("=" * 60)
heap = []
for value in [5, 1, 9, 3]:
    heapq.heappush(heap, value)
print("  heap       :", heap, " (a list, but ordered by the heap rule)")
print("  peek min   :", heap[0])
while heap:
    print("  heappop    :", heapq.heappop(heap), end="")
print()
nums = [4, 1, 7, 3, 8, 2]
print("  3 smallest :", heapq.nsmallest(3, nums))
print("  2 largest  :", heapq.nlargest(2, nums))
print("  heapify    :", (lambda h: (heapq.heapify(h), h)[1])([9, 4, 7, 1]))

print("\n" + "=" * 60)
print("6. bisect — binary search for free")
print("=" * 60)
sorted_nums = [1, 3, 5, 7, 9, 11]
print("  list                 :", sorted_nums)
print("  bisect_left(7)       :", bisect.bisect_left(sorted_nums, 7), " <- index of first >= 7")
print("  bisect_right(7)      :", bisect.bisect_right(sorted_nums, 7), " <- first > 7")
print("  bisect_left(6)       :", bisect.bisect_left(sorted_nums, 6), " (where 6 WOULD go)")
print("  bisect_left(100)     :", bisect.bisect_left(sorted_nums, 100))
bisect.insort(sorted_nums, 6)
print("  after insort(6)      :", sorted_nums, " = insert + stay sorted")

print("\n" + "=" * 60)
print("7. functools: lru_cache & reduce")
print("=" * 60)


@lru_cache(maxsize=None)
def fib(n):
    """Memoisation in ONE line — no manual dict needed."""
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print("  fib(100) with lru_cache:", fib(100))
print("  cache info             :", fib.cache_info())


def naive_fib(n):
    return n if n < 2 else naive_fib(n - 1) + naive_fib(n - 2)


print("  naive_fib(25)          :", naive_fib(25), " (would be hopeless at n=100)")
print("  reduce(mul, [1..5])    :", reduce(lambda a, b: a * b, range(1, 6)))
print("  reduce(add, [1..100])  :", reduce(lambda a, b: a + b, range(1, 101)))

print("\n" + "=" * 60)
print("8. os / sys")
print("=" * 60)
print("  python version  :", sys.version.split()[0])
print("  platform        :", sys.platform)
print("  argv            :", sys.argv)
print("  current dir     :", os.getcwd())
print("  env HOME set?   :", "HOME" in os.environ)
print("  max int         :", sys.maxsize, "(Python ints are bounded only by memory)")

print("\n" + "=" * 60)
print("9. Writing your own module (live demo)")
print("=" * 60)
# Create a real module file in a temp directory, import it, and use it.
import pathlib
import tempfile

workdir = pathlib.Path(tempfile.gettempdir()) / "course_modules_demo"
workdir.mkdir(parents=True, exist_ok=True)
(workdir / "helpers.py").write_text(
    '"""A tiny module created by lesson 13."""\n\n'
    'COURSE = "Python zero to DSA"\n\n'
    'def double(n):\n'
    '    """Return n * 2."""\n'
    '    return n * 2\n\n'
    'if __name__ == "__main__":\n'
    '    print("helpers.py run directly ->", double(21))\n',
    encoding="utf-8",
)

sys.path.insert(0, str(workdir))          # tell Python where to look
import helpers                            # noqa: E402 - import after sys.path change

print("  imported helpers from", helpers.__file__)
print("  helpers.COURSE      :", helpers.COURSE)
print("  helpers.double(21)  :", helpers.double(21))
print("  module docstring    :", helpers.__doc__)
print("  ('__main__' guard means the demo print did NOT run on import)")

# simulate running the module directly, as a subprocess would.
# (This needs a real operating system: in the browser playground Pyodide has no
#  processes, so we catch that and explain instead of crashing.)
try:
    import subprocess
    result = subprocess.run([sys.executable, "helpers.py"], cwd=workdir,
                            capture_output=True, text=True, check=False)
    print("  running it directly :", result.stdout.strip())
except (ImportError, OSError) as error:
    print(f"  running it directly : not possible here ({type(error).__name__}: {error})")
    print("                        → use a real terminal for this part")

sys.path.remove(str(workdir))
# clear the demo files. `glob` + `unlink` fails on the __pycache__ DIRECTORY the
# import just created, so remove the whole tree instead:
import shutil                                                          # noqa: E402
shutil.rmtree(workdir, ignore_errors=True)

print("\n" + "=" * 60)
print("10. Virtualenvs & pip — the commands to remember")
print("=" * 60)
commands = [
    "python3 -m venv .venv",
    "source .venv/bin/activate        # Windows: .venv\\Scripts\\activate",
    "python -m pip install requests",
    "python -m pip freeze > requirements.txt",
    "python -m pip install -r requirements.txt",
    "deactivate",
]
for command in commands:
    print("   $", command)

print("\n  Try it now (in the repo terminal):")
print("     cd python-course && python3 -m venv .venv && source .venv/bin/activate")
print("     python -m pip install pytest    # then: pytest -q")
print("  Note: this course deliberately needs NO third-party packages.")

print("\n" + "=" * 60)
print("11. Debugging toolkit (you will need this)")
print("=" * 60)
print("""   print(f"{variable=}")            # prints variable='value' with a label
   breakpoint()                     # drops into pdb (n=next, s=step, c=continue,
                                    #   l=list code, p expr=print, q=quit)
   python3 -m pdb script.py         # start under the debugger
   python3 -m trace --trace script.py
   python3 -X faulthandler script.py
   python3 -m cProfile -s cumtime script.py    # find the slow part
   python3 -m timeit -s "setup" "expression"   # micro-benchmarks""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Create `helpers.py` next to your own script with `is_even`, `double` and
#    a `__main__` demo guard; import and use it.
# 2. Use math to print the number of digits of 2**1000 (log10), and compare it
#    with len(str(2**1000)).
# 3. Simulate 1000 dice rolls with random (seed 1) and print the frequency of
#    each face using Counter.
# 4. Use statistics to compare mean and median of [1, 2, 3, 4, 1000].
# 5. Build a min-heap from a random list of 20 numbers and pop them all out in
#    sorted order (that is heap sort, in 3 lines).
# 6. Use bisect to count how many values in a sorted list are < 50 (hint: it is
#    one call + the list length).
# 7. Time naive_fib(28) vs fib(28) (with lru_cache) and print the speed-up.
# 8. Write a script that takes numbers from `sys.argv`, sums them, and prints
#    usage help if none are given.
print()
print("Lesson 13 done — now do exercises/ex_13_modules.py ✅")
