# 🐍 Python: Zero → Intermediate → Basic DSA

A hands-on, self-paced course for **Prathamesh**. Everything here is real,
runnable Python — no slides, no fluff. You read a short lesson, change the code,
and solve problems that are **auto-tested**, so you always know whether you got
it right.

---

## 🚀 Four ways to use this course

### 1. Interactive playground (start here — nothing to install)
Python runs **inside your browser** (Pyodide + WebAssembly, vendored locally so
it works offline). Edit code, press **Run**, and run the tests with one click.
Progress is saved in your browser (`localStorage`).

```bash
cd python-course
python3 serve.py                                  # then open:
# http://localhost:8080/python-course/playground/index.html
```

Or with the repo's Vite dev server (already configured in `vite.config.js`):

```bash
npm install && npm run dev                        # then open
# http://localhost:5173/python-course/playground/index.html
```

What you get in the playground:

* every lesson, exercise and problem in a sidebar with ✅ / ❌ / ⏳ badges,
* **▶ Run** for your code and **🎓 Solution** to see the reference run
  (it passes `--solution`, exactly like the terminal),
* a stdin box, so lessons that use `input()` still work,
* live progress: "12 / 37 done".

Screen space:

* the lesson panel gets ~70% of the height — **drag the divider** under it (or
  focus it and press ↑/↓; double-click resets) to give it up to 90%,
* **⤢ Big page** hides the output panel entirely so a long lesson fits on one
  screen; pressing **▶ Run** brings the output back automatically,
* **☰ Files** hides the sidebar for a wider page,
* **A− / A+** change the code font size (85% → 130%); your layout choices are
  remembered next time.

> The playground is slightly slower than real Python (it is WebAssembly) and
> can't run processes — `lesson_13_modules_venv.py` is marked 💻 for that reason.

### 2. Standalone Android APK (`PythonCourse-1.0.apk`)
Learn on your phone: the complete course and offline Pyodide runtime are
packaged into a ~5.7 MB standalone Android APK (`python-course/PythonCourse-1.0.apk`).

* **Fully offline**: all 16 lessons, 16 exercises, 12 DSA topics, 21 problems, and
  vendored Pyodide WebAssembly bundle are stored in local assets.
* **Zero permissions**: requires no network, location, or file system permissions.
* **Persistent**: your code edits and test progress are saved in Android DOM storage.
* **Rebuild**: `python3 tools/build_apk.py` packages and signs a new APK using
  the committed sideload keys.

### 3. Run the files locally (recommended once you are past lesson 3)
```bash
cd python-course

python3 lessons/lesson_01_hello.py     # read a lesson, see it run
python3 exercises/ex_01_basics.py      # solve it (the tests tell you if you're right)
python3 dsa/dsa_01_arrays.py           # DSA topic with worked examples
python3 problems/p01_fizzbuzz.py       # practice problem
python3 problems/solutions/p01_fizzbuzz.py   # the reference solution

python3 tools/grade.py                 # grade EVERYTHING (your score)
python3 tools/grade.py --solutions     # sanity check the reference solutions
python3 tools/grade.py exercises       # one section: exercises | dsa | problems
python3 tools/grade.py --verbose       # see the full output of each file

python3 exercises/ex_01_basics.py --solution   # run the built-in solution
```

### 3. Do it in the chat
Tell me "teach me lesson 3" and I'll walk you through it, check your code and
give you feedback. Best combined with option 1 or 2.

---

## 📚 The curriculum

### Part 1 — Foundations (you can't skip this part)
| # | Lesson | You'll be able to |
|---|--------|-------------------|
| 01 | Hello, Python | run code, read error messages instead of fearing them |
| 02 | Variables, types & input | store data, convert types, f-strings |
| 03 | Numbers & operators | `//`, `%`, `**`, comparison and boolean logic |
| 04 | Strings in depth | index, slice, 20+ string methods |
| 05 | Making decisions | `if/elif/else`, truthiness, `match` |
| 06 | Loops | `for`, `while`, `range`, `break/continue`, `enumerate`, `zip` |

### Part 2 — Data structures (the workhorses of DSA)
| # | Lesson | You'll be able to |
|---|--------|-------------------|
| 07 | Lists | index/slice, mutate, sort with `key`, comprehensions, prefix sums |
| 08 | Tuples & sets | immutable records, dedupe, set algebra, O(1) membership |
| 09 | Dictionaries | count, group, `Counter`/`defaultdict`, two-sum |
| 10 | Functions | defaults, `*args`/`**kwargs`, scope, closures, type hints |
| 11 | Errors & files | `try/except`, raising, `with open`, JSON, pathlib |

### Part 3 — Intermediate Python
| # | Lesson | You'll be able to |
|---|--------|-------------------|
| 12 | Comprehensions & generators | Pythonic one-liners, `yield`, `itertools` |
| 13 | Modules, pip & venv | structure a project, standard library, virtualenvs |
| 14 | Classes & OOP | `self`, dunder methods, properties, dataclasses |
| 15 | Lambdas, sorting & decorators | `sorted(key=...)`, `lru_cache`, write decorators |
| 16 | Big-O & fast Python | reason about speed, measure, avoid the classic O(n²) traps |

### Part 4 — DSA in Python
| # | Topic | Covered |
|---|-------|---------|
| dsa_01 | Arrays & two pointers | min/max, in-place reverse, rotation, prefix sums, Kadane |
| dsa_02 | Strings | palindrome, anagrams, run-length encoding, sliding window |
| dsa_03 | Hash maps | two-sum, frequency, grouping, longest consecutive run |
| dsa_04 | Sorting | bubble/selection/insertion/merge/quick/counting + Python's sort |
| dsa_05 | Binary search | classic, lower/upper bound, rotated arrays, answer-space search |
| dsa_06 | Recursion & backtracking | factorial, memo fib, subsets, permutations, N-queens, maze |
| dsa_07 | Stacks & queues | brackets, min stack, monotonic stack, deque windows |
| dsa_08 | Linked lists | build/reverse, Floyd cycle, merge, merge sort |
| dsa_09 | Trees & BST | 4 traversals, height, validate BST, delete, LCA |
| dsa_10 | Heaps | `heapq`, k-th largest, top-k, k-way merge, running median |
| dsa_11 | Graphs | BFS/DFS, components, cycles, topological sort, Dijkstra, union-find |
| dsa_12 | Dynamic programming | memo → table, stairs, coins, knapsack, LCS, LIS |

**Practice:** 16 exercise sets (one per lesson) + **21 auto-graded problems**
(`p00` warm-up → `p20` monotonic stacks), each with a reference solution in
`problems/solutions/`.

---

## 🗓️ A 6-week plan (≈45–60 min/day)

| Week | Do this | Goal |
|------|---------|------|
| 1 | Lessons 01–06 + exercises 01–06 | fluent with loops, strings, conditions |
| 2 | Lessons 07–11 + exercises 07–11 | lists/dicts/functions feel natural |
| 3 | Lessons 12–16 + exercises 12–16 | comprehensions, classes, Big-O thinking |
| 4 | dsa_01 … dsa_06 + problems p00–p10 | arrays, strings, hashing, sorting, searching, recursion |
| 5 | dsa_07 … dsa_12 + problems p11–p20 | stacks, lists, trees, heaps, graphs, DP |
| 6 | Re-solve everything from a blank file | real fluency — this is the week that matters |

**Rules that actually make you learn**
1. **Type the code, don't copy-paste it.** Muscle memory is real.
2. **Predict before you run.** Write down what you think will print, then run.
3. **Break things on purpose.** Change a number, delete a line, read the error.
4. **Never read a solution before attempting** for at least 15 minutes.
5. **State the Big-O of every solution you write** (lesson 16 teaches you how).

---

## 🧠 How grading works

`tools/harness.py` is a tiny test runner (no pytest needed). Exercise and
problem files end with:

```python
CASES = [("basic", "two_sum([2, 7, 11, 15], 9)", (0, 1))]
...
run_expressions("two_sum", CASES, globals())
summary()
```

Running the file gives you:

```
  ✅ basic
  ❌ no-solution   expected (0, 1) got None
  ⏭  empty        (not attempted yet)
two_sum
10 passed   0 failed   2 skipped
```

* `✅` passed · `❌` wrong answer · `⏭` you haven't implemented it yet
  (`NotImplementedError` is skipped on purpose)
* add `--solution` to any exercise/problem file to watch the reference pass
* `tools/grade.py` runs every file and prints your total score

---

## 📁 Layout

```
python-course/
├── README.md              ← you are here
├── CHEATSHEET.md          ← one-page syntax reference (print this)
├── serve.py               ← tiny web server for the playground
├── playground/            ← browser IDE (Pyodide) + progress tracking
│   ├── index.html · app.js · worker.js · style.css
│   └── vendor/pyodide/    ← Python 3.12 in WebAssembly (offline)
├── lessons/               ← 16 teaching lessons (run them!)
├── exercises/             ← 16 exercise sets, auto-tested (--solution built in)
├── dsa/                   ← 12 DSA topics with worked examples
├── problems/              ← 21 practice problems, auto-graded
│   └── solutions/         ← reference solutions for those problems
└── tools/
    ├── harness.py         ← test runner used everywhere
    ├── grade.py           ← grade all exercises / problems
    └── make_solutions.py  ← regenerate problems/solutions/ from the problems
```

---

## ⚙️ Requirements

Python **3.10+** (the code uses `match`, `X | Y` type hints and modern
dataclasses; it was written and tested on 3.11 and 3.12). No third-party
packages are required anywhere — lesson 13 teaches you how to *use* pip and
virtualenvs, so you can practise on your own projects:

```bash
cd python-course
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
python -m pip install pytest                           # optional playground for later
```
