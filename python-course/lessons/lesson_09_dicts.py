"""
LESSON 09 · Dictionaries — key → value

A dict maps **keys** to **values**. If lists are the most used structure in
DSA, dicts are the most *powerful*: they turn O(n²) search loops into O(n).
This lesson is where "basic DSA" really clicks.

# Creating

    student = {"name": "Ravi", "age": 20, "marks": [88, 92]}
    empty = {}
    counts = dict.fromkeys("abc", 0)      # {'a': 0, 'b': 0, 'c': 0}
    pairs = [("a", 1), ("b", 2)]
    dict(pairs)                           # {'a': 1, 'b': 2}

Keys must be **hashable and unique** (str, int, float, bool, tuple, None).
Values can be anything. Insertion order is preserved in Python 3.7+.

# Reading

    student["name"]              # KeyError if missing
    student.get("name")          # None if missing
    student.get("phone", "-")    # default value if missing  <- prefer this
    "name" in student            # membership test on KEYS, O(1)

# Writing / updating

    student["city"] = "Pune"     # add or overwrite
    student.update({"age": 21, "phone": "123"})
    del student["city"]          # KeyError if missing
    student.pop("phone")         # remove & return value
    student.pop("nope", None)    # safe pop with default
    student.clear()
    student.setdefault("city", "Pune")   # set only if the key is absent

# Iterating

    for key in d:                       # keys
    for value in d.values():            # values
    for key, value in d.items():        # both  <- the one you want 90% of the time

# Comprehensions

    {k: v * 2 for k, v in d.items()}
    {word: len(word) for word in words}
    {k: v for k, v in d.items() if v > 10}     # filtering

# Inverting a dict (values -> keys)

    {v: k for k, v in d.items()}

# Sorting a dict

    sorted(d)                       # sorted keys
    sorted(d.items(), key=lambda kv: kv[1], reverse=True)   # by value
    dict(sorted(d.items()))         # a dict rebuilt in key order

Dicts preserve insertion order, so "sorted by value" is often done as:
    dict(sorted(d.items(), key=lambda kv: -kv[1]))

# Two power tools from collections

    from collections import Counter, defaultdict

    Counter("banana")                  # Counter({'a': 3, 'n': 2, 'b': 1})
    counter.most_common(2)             # [('a', 3), ('n', 2)]
    counts["x"] += 1 on a plain dict   # KeyError if 'x' is new
    defaultdict(int)["x"] += 1         # auto-creates missing keys -> 1

# The pattern that solves a hundred problems

Count occurrences in ONE pass, then answer in O(1) lookups:

    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1     # classic
    # or:  from collections import Counter ; counts = Counter(items)

# Nested dicts (records inside records)

    db = {"ravi": {"age": 20, "city": "Pune"}}
    db["ravi"]["age"]        # 20
    db.get("priya", {}).get("age", "unknown")     # safe deep access

# Complexity

    insert / lookup / delete / `in` : O(1) average, O(n) worst case
    iterate over everything         : O(n)
    building from n items           : O(n)

That "average O(1)" is why "use a hash map" is the single most common
interview hint. Ask yourself: *what if I remembered what I already saw?*
"""

from collections import Counter, defaultdict

print("=" * 60)
print("1. Create & read")
print("=" * 60)
student = {"name": "Prathamesh", "age": 21, "marks": [88, 92, 79]}
print("student        =", student)
print('student["name"] =', student["name"])
print('student.get("name")        =', student.get("name"))
print('student.get("phone")       =', student.get("phone"))
print('student.get("phone", "-")  =', student.get("phone", "-"))
print('"age" in student           =', "age" in student)
try:
    student["phone"]
except KeyError as exc:
    print("student['phone'] ->", type(exc).__name__, "-", exc, " (always use .get for optional keys)")

print("\n" + "=" * 60)
print("2. Add / update / delete")
print("=" * 60)
student["city"] = "Pune"
print("after adding city     :", student)
student.update({"age": 22, "email": "p@example.com"})
print("after update(...)     : keys ->", list(student))
del student["email"]
print("after del email       : keys ->", list(student))
print("pop('city') ->", student.pop("city"), "| left:", list(student))
print("pop('zzz', 'default') ->", student.pop("zzz", "default"))
student.setdefault("level", "beginner")
print("setdefault            :", student["level"])

print("\n" + "=" * 60)
print("3. Iterating")
print("=" * 60)
ages = {"ravi": 20, "priya": 22, "asha": 19}
for key in ages:
    print("  key only     :", key)
for value in ages.values():
    print("  value only   :", value)
for name, age in ages.items():
    print(f"  item         : {name} is {age}")

print("\n" + "=" * 60)
print("4. Comprehensions")
print("=" * 60)
print("squares   :", {n: n * n for n in range(5)})
print("lengths   :", {w: len(w) for w in ["a", "abc", "hi"]})
print("filtered  :", {k: v for k, v in ages.items() if v >= 20})
print("inverted  :", {v: k for k, v in ages.items()})
print("counting  :", {ch: "banana".count(ch) for ch in set("banana")})
print("grouped   :", {word[0]: word for word in ["apple", "avocado", "banana"]}, " <- last wins")

print("\n" + "=" * 60)
print("5. Sorting and ranking a dict")
print("=" * 60)
scores = {"ravi": 88, "priya": 95, "asha": 72, "dev": 95}
print("sorted by key        :", dict(sorted(scores.items())))
print("sorted by value      :", sorted(scores.items(), key=lambda kv: -kv[1]))
print("top 2 by value       :", sorted(scores.items(), key=lambda kv: -kv[1])[:2])
print("top 2 with Counter   :", Counter(scores.values()).most_common(2))
print("max by value         :", max(scores, key=scores.get), "=", max(scores.values()))
print("sum of all values    :", sum(scores.values()))

print("\n" + "=" * 60)
print("6. Counter & defaultdict")
print("=" * 60)
text = "the quick brown fox jumps over the lazy dog the end"
word_counts = Counter(text.split())
print("Counter          :", word_counts)
print("3 most common    :", word_counts.most_common(3))
print("count of 'the'   :", word_counts["the"], "| missing word ->", word_counts["unicorn"])
print("letter counts    :", Counter("banana").most_common())

groups = defaultdict(list)
for name, age in ages.items():
    groups["adult" if age >= 20 else "teen"].append(name)
print("defaultdict(list):", dict(groups))

counter = defaultdict(int)
for ch in "mississippi":
    counter[ch] += 1                # no KeyError, auto-starts at 0
print("defaultdict(int) :", dict(counter))

print("\n" + "=" * 60)
print("7. THE pattern: trade memory for speed (O(n²) -> O(n))")
print("=" * 60)

def two_sum_brute(nums, target):
    """Check every pair. O(n^2) time, O(1) space."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None

def two_sum_hash(nums, target):
    """Remember what we have already seen. O(n) time, O(n) space."""
    seen = {}                            # value -> index
    for index, value in enumerate(nums):
        needed = target - value
        if needed in seen:               # O(1) lookup
            return (seen[needed], index)
        seen[value] = index
    return None

data = [2, 7, 11, 15, 3, 6]
print("brute force:", two_sum_brute(data, 9))
print("hash map   :", two_sum_hash(data, 9))
print("hash map   :", two_sum_hash(data, 26))

print("\n" + "=" * 60)
print("8. Worked examples: frequency counting everywhere")
print("=" * 60)

def first_non_repeating(text):
    """First character that appears exactly once (or None)."""
    counts = Counter(text)
    for ch in text:                     # keep the original order!
        if counts[ch] == 1:
            return ch
    return None

def are_anagrams(a, b):
    """Same letters with the same counts (ignores case and spaces)."""
    clean = lambda s: Counter(ch.lower() for ch in s if ch.isalnum())
    return clean(a) == clean(b)

def group_by_first_letter(words):
    groups = defaultdict(list)
    for word in words:
        groups[word[0].upper()].append(word)
    return dict(groups)

def most_frequent(nums):
    """Most frequent element; ties broken by first appearance."""
    counts = Counter(nums)                       # Counter remembers insertion order
    return counts.most_common(1)[0][0]

print("first non-repeating in 'aabbcdd' :", first_non_repeating("aabbcdd"))
print("first non-repeating in 'aabbcc'  :", first_non_repeating("aabbcc"))
print("anagram('Listen','Silent')       :", are_anagrams("Listen", "Silent"))
print("anagram('hello','world')         :", are_anagrams("hello", "world"))
print("group by letter                  :", group_by_first_letter(["apple", "avocado", "banana", "berry"]))
print("most frequent [1,3,3,2,3,1]      :", most_frequent([1, 3, 3, 2, 3, 1]))

print("\n" + "=" * 60)
print("9. Counting with a normal dict vs defaultdict vs Counter")
print("=" * 60)
votes = ["red", "blue", "red", "green", "red", "blue"]

manual = {}
for vote in votes:
    manual[vote] = manual.get(vote, 0) + 1
print("get(...) + 1 :", manual)

dd = defaultdict(int)
for vote in votes:
    dd[vote] += 1
print("defaultdict  :", dict(dd))
print("Counter      :", dict(Counter(votes)))
print("winner       :", Counter(votes).most_common(1)[0][0])

print("\n" + "=" * 60)
print("10. Nested dicts (mini database)")
print("=" * 60)
db = {
    "p01": {"name": "Prathamesh", "level": "beginner", "solved": 12},
    "p02": {"name": "Ravi", "level": "intermediate", "solved": 140},
}
for pid, record in db.items():
    print(f"  {pid}: {record['name']:<12} {record['level']:<14} solved={record['solved']}")
print("total solved:", sum(r["solved"] for r in db.values()))
print("safe deep access:", db.get("p99", {}).get("solved", 0))

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Count the frequency of each word in a paragraph (use split + Counter),
#    then print the 3 most common words.
# 2. Given marks = {"ravi": 88, "priya": 95, "asha": 72}, print the topper and
#    the average. Then invert the dict (score -> name).
# 3. Write `is_permutation_of_palindrome(s)` -> can the letters be rearranged
#    into a palindrome? (Hint: at most ONE letter may have an odd count.)
# 4. Write `intersection_of_lists(a, b)` returning common elements without
#    duplicates, using a set AND again using a dict.
# 5. Write `word_frequency_top_k(text, k)` returning the k most frequent words,
#    ties broken alphabetically (hint: sort with a tuple key).
# 6. Write `two_sum_all_pairs(nums, target)` returning EVERY pair of indices
#    that sums to the target, in O(n) average time using a dict.
# 7. Write `char_positions(text)` -> {char: [positions]} using defaultdict(list).
print()
print("Lesson 09 done — now do exercises/ex_09_dicts.py ✅")
