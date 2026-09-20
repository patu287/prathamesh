# 🐍 Python + DSA cheat sheet

Print this. Keep it next to you for the first month.

---

## The basics

```python
x = 5                     # int       y = 3.14      # float
s = "text"                # str       b = True      # bool
n = None                  # nothing
name = input("Name? ")    # ALWAYS a string -> int(name) if you need a number
print(a, b, sep=", ", end="\n")

type(x)                   int(x)  str(x)  float(x)  bool(x)  round(x, 2)
f"{value:.2f}"   f"{value:>8}"   f"{value:,}"   f"{value!r}"   f"{value=}"   # debug
```

## Operators

```python
+ - * /        # / always gives a float
// % **        # floor division, remainder, power
== != < <= > >=    and   or   not
+= -= *= /= //= %= **=          # no x++ in Python!
0.1 + 0.2 != 0.3                # floats are approximations
```

## Strings (immutable)

```python
s[i]  s[-1]  s[1:4]  s[:3]  s[3:]  s[::2]  s[::-1]     # reverse!
len(s)  "x" in s  s + t  s * 3
s.upper() s.lower() s.strip() s.split() s.split(",") s.replace("a","b")
",".join(parts)  s.find("x")  s.count("x")  s.startswith("a") s.endswith("z")
s.isdigit() s.isalpha() s.isalnum() s.isspace()      ord("a")  chr(97)
s[0] = "x"    # ✗ TypeError — build a new string instead
```

## Lists (mutable, ordered)

```python
nums = [3, 1, 4]     empty = []     matrix = [[0]*3 for _ in range(2)]
nums[0] nums[-1] nums[1:3] nums[::-1] len(nums) sum(nums) min(nums) max(nums)
nums.append(x) nums.insert(0, x) nums.extend([...]) nums.remove(x)
nums.pop() nums.pop(0) del nums[0] nums.clear() nums.index(x) nums.count(x)
x in nums    nums.sort()    nums.sort(key=len, reverse=True)    sorted(nums)
[n*n for n in nums if n % 2 == 0]        # comprehension
b = a            # ✗ both names, ONE list — use a[:] or a.copy() for a copy
```

## Tuples & sets

```python
point = (3, 4)      x, y = point        # unpack
set(nums)           unique, unordered, O(1) membership
s.add(x) s.discard(x)  a | b  a & b  a - b  a ^ b  a <= b
# tuples can be dict keys, lists cannot
```

## Dicts (key → value)

```python
d = {"a": 1}
d["b"] = 2        d.get("z", default)      "a" in d
for k, v in d.items(): ...      d.keys()  d.values()  sorted(d.items(), key=lambda kv: -kv[1])
d.pop("a", None)   d.setdefault(k, 0)   del d["a"]
{k: v*2 for k, v in d.items()}             # comprehension

from collections import Counter, defaultdict
Counter("banana").most_common(2)           # [('a', 3), ('n', 2)]
counter[item] += 1                         # KeyError if new → use defaultdict(int)
counts.get(item, 0) + 1                    # the manual version
defaultdict(list)[key].append(value)       # grouping
```

## Control flow

```python
if cond: ... elif cond: ... else: ...
value = "yes" if cond else "no"            # ternary
match command:                             # 3.10+
    case "add": ...
    case _: ...

for x in items: ...                        # for-each
for i, x in enumerate(items, start=1): ...
for a, b in zip(list1, list2): ...
for i in range(0, 10, 2): ...              # stop is EXCLUDED
while cond: ...                            # make sure it changes!
break / continue / for...else
while True: ...; break                     # input loop
```

## Functions

```python
def f(a, b=10, *args, **kwargs) -> int:
    """Docstring."""
    return a + b

f(1)   f(a=1, b=2)   f(*values)   f(**mapping)
# ✗ never use a mutable default: def f(items=[])  → use items=None
global x      # avoid; pass values in and return values out
```

## Errors & files

```python
try:
    risky()
except (ValueError, TypeError) as exc:
    print(type(exc).__name__, exc)
else:
    ...
finally:
    ...
raise ValueError("message")     assert cond, "message"
```

```python
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("hello\n")
with open("data.txt", encoding="utf-8") as f:
    for line in f: ...
import json, pathlib
pathlib.Path("a/b.json").write_text(json.dumps(data), encoding="utf-8")
json.dump(data, f, indent=2)     json.load(f)
```

## Intermediate

```python
[n*n for n in nums]  {k: v for k, v in d.items()}  {x for x in nums}   # comprehensions
(n*n for n in nums)                                                # lazy generator
def gen(n):
    for i in range(n): yield i            # generator function
sum(x*x for x in nums)  any(...)  all(...)    # no giant list needed

sorted(items, key=lambda x: (-x.score, x.name))     # multi-key sort
from operator import itemgetter, attrgetter
@lru_cache(maxsize=None)                            # memoisation
from functools import lru_cache, reduce, wraps

@dataclass                       # class with __init__/__repr__/__eq__ for free
class Point:
    x: int
    y: int = 0
    tags: list = field(default_factory=list)     # safe mutable default
# method: def m(self)   str: __str__  repr: __repr__  eq: __eq__  lt: __lt__
# property: @property   static: @staticmethod   alternative ctor: @classmethod
```

## DSA building blocks

```python
stack = []      stack.append(x)      stack.pop()      stack[-1]        # LIFO
from collections import deque
queue = deque()  queue.append(x)     queue.popleft()                   # FIFO (O(1)!)
import heapq
h = [] ; heapq.heappush(h, x) ; heapq.heappop(h) ; h[0]                # min-heap
heapq.heappush(h, -x)                                                  # max-heap
import bisect
bisect.bisect_left(sorted_list, x)   bisect_right(...)   bisect.insort(...)
from itertools import accumulate, combinations, permutations, product, islice, chain
```

## The two-pointer + prefix-sum templates

```python
left, right = 0, len(a) - 1                 # shrinking window (sorted data)
while left < right:
    ...
    left += 1; right -= 1

prefix = [0] * (len(a) + 1)                 # O(1) range sums
for i, v in enumerate(a):
    prefix[i+1] = prefix[i] + v
range_sum = prefix[j] - prefix[i]           # sum of a[i:j]
```

## Complexity you should be able to say out loud

| Structure / op          | Cost        |
|-------------------------|-------------|
| list index / append     | O(1)        |
| list insert(0) / pop(0) | O(n) ⚠      |
| `x in list`             | O(n)        |
| dict / set lookup       | O(1) avg    |
| sort                    | O(n log n)  |
| heap push/pop           | O(log n)    |
| bisect on sorted        | O(log n)    |
| BFS / DFS on a graph    | O(V + E)    |
| recursion depth d       | O(d) memory |

**Pick the tool:** need "have I seen it?" → set · need "count / lookup later"
→ dict · need "biggest/smallest next" → heap · need "sorted + search" → sort +
bisect · need "no shifting at the front" → deque.

## The 10 mistakes that cost you the most time

1. `input()` returns a string — convert it.
2. `=` vs `==`.
3. `b = a` on a list is aliasing, not copying.
4. `def f(items=[])` — mutable default shared forever.
5. Modifying a list while looping over it.
6. `list.pop(0)` in a loop (use `deque`).
7. Off-by-one with `range` (stop is excluded).
8. Comparing floats with `==`.
9. Forgetting `self` or the `()` when calling a method.
10. `sort()` returns `None` (it sorts in place) — use `sorted()` for a new list.

## Getting unstuck (in order)

1. Read the error message bottom-up: type + message + line number.
2. `print(f"{variable=}")` right before the failure.
3. `breakpoint()` and step through (`n`, `s`, `p expr`, `c`, `q`).
4. Check your assumptions with tiny inputs: `[]`, `[1]`, `[1, 1]`, negatives.
5. Explain the problem out loud to a rubber duck.
6. Write the brute force first; optimise after it passes.
