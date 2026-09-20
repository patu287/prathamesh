"""
DSA 03 · Hash maps — the pattern that solves half of all interview problems

A hash map (Python `dict`) stores key -> value with O(1) average lookup,
insert and delete. A hash *set* is the same idea without values.

The mindset
-----------
Ask yourself, in this order:

1. **"Have I seen this before?"**               -> set
2. **"How many times have I seen this?"**       -> dict counter / Counter
3. **"What do I need to look up later?"**       -> dict: store it now, use it later
4. **"Can I trade memory for time?"**           -> yes, and that is usually the answer

Turning an inner loop into a lookup is THE core optimisation:

    O(n²) nested loop   ->   O(n) single pass + dict

Problems in this file
---------------------
* two-sum (the canonical example)
* frequency counting / most common element
* dedupe while preserving order
* grouping (anagrams, buckets)
* first non-repeating element
* pair counting / complementary counting
* longest consecutive sequence (set-based)
* intersection / union / difference of collections

Trade-off to state out loud: **O(n) extra space to get O(n) time**.
"""

from collections import Counter, defaultdict
import time

print("=" * 60)
print("1. Two-sum: brute force vs hash map")
print("=" * 60)


def two_sum_brute(nums, target):
    """O(n^2) time, O(1) space. Fine for tiny inputs, hopeless for big ones."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None


def two_sum_hash(nums, target):
    """O(n) time, O(n) space. Store what you have seen: value -> index."""
    seen = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:            # the "have I seen the other half?"
            return (seen[complement], index)
        seen[value] = index
    return None


data = [2, 7, 11, 15, 3, 6]
print("  brute:", two_sum_brute(data, 9), " hash:", two_sum_hash(data, 9))
print("  brute:", two_sum_brute(data, 17), " hash:", two_sum_hash(data, 17))
print("  no solution ->", two_sum_hash(data, 100))


def two_sum_all_pairs(nums, target):
    """Every pair of indices that sums to the target. O(n) average."""
    pairs = []
    seen = {}
    for index, value in enumerate(nums):
        complement = target - value
        for earlier_index in seen.get(complement, []):
            pairs.append((earlier_index, index))
        seen.setdefault(value, []).append(index)
    return pairs


print("  all pairs in [1,1,2,3,4,5] summing to 5:", two_sum_all_pairs([1, 1, 2, 3, 4, 5], 5))

print("\n  timing at n = 4000 (target never present -> worst case)")
import random
random.seed(1)
sample = random.sample(range(100_000), 4_000)
start = time.perf_counter()
two_sum_brute(sample, -5)
brute_ms = (time.perf_counter() - start) * 1000
start = time.perf_counter()
two_sum_hash(sample, -5)
hash_ms = (time.perf_counter() - start) * 1000
print(f"    O(n^2): {brute_ms:8.2f} ms     O(n): {hash_ms:6.3f} ms     "
      f"{brute_ms / hash_ms:.0f}x faster")

print("\n" + "=" * 60)
print("2. Frequency counting")
print("=" * 60)


def count_occurrences(items):
    """Three ways to do the same job."""
    manual = {}
    for item in items:
        manual[item] = manual.get(item, 0) + 1

    dd = defaultdict(int)
    for item in items:
        dd[item] += 1

    counter = Counter(items)

    return manual, dict(dd), dict(counter)


items = ["a", "b", "a", "c", "a", "b"]
manual, dd, counter = count_occurrences(items)
print("  dict.get     :", manual)
print("  defaultdict  :", dd)
print("  Counter      :", counter)
print("  all equal    :", manual == dd == counter)


def most_frequent(items):
    """Most frequent element; ties break by first appearance."""
    counts = Counter(items)                     # Counter keeps insertion order
    return counts.most_common(1)[0]


def least_frequent(items):
    counts = Counter(items)
    fewest = min(counts.values())
    return [(item, count) for item, count in counts.items() if count == fewest]


numbers = [1, 3, 3, 2, 3, 1, 4]
print("  most frequent in", numbers, "->", most_frequent(numbers))
print("  least frequent ones:", least_frequent(numbers))

print("\n" + "=" * 60)
print("3. Dedupe while preserving order")
print("=" * 60)


def dedupe_ordered(items):
    """dict.fromkeys preserves insertion order and dedupes. O(n)."""
    return list(dict.fromkeys(items))


def dedupe_seen_set(items):
    """The explicit version — same complexity, clearer intent."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def duplicates_only(items):
    """Values seen more than once, in order of first appearance."""
    counts = Counter(items)
    return [item for item in dedupe_ordered(items) if counts[item] > 1]


messy = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
print("  original        :", messy)
print("  dedupe(dict)    :", dedupe_ordered(messy))
print("  dedupe(set)     :", dedupe_seen_set(messy))
print("  duplicates only :", duplicates_only(messy))

print("\n" + "=" * 60)
print("4. Grouping things by a key")
print("=" * 60)


def group_by_first_letter(words):
    groups = defaultdict(list)
    for word in words:
        groups[word[0].upper()].append(word)
    return dict(groups)


def group_by_length(words):
    groups = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)
    return dict(sorted(groups.items()))


def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        groups["".join(sorted(word.lower()))].append(word)
    return [sorted(group) for group in groups.values()]


words = ["apple", "avocado", "banana", "Blueberry", "cherry", "date", "fig"]
print("  by first letter:", group_by_first_letter(words))
print("  by length      :", group_by_length(words))
print("  anagrams       :", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))

print("\n" + "=" * 60)
print("5. First non-repeating / first repeating")
print("=" * 60)


def first_non_repeating(items):
    counts = Counter(items)
    for item in items:
        if counts[item] == 1:
            return item
    return None


def first_repeating(items):
    """First value that appears twice, scanning left to right."""
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


stream = [4, 5, 1, 2, 0, 4, 5]
print("  stream              :", stream)
print("  first non-repeating :", first_non_repeating(stream))
print("  first repeating     :", first_repeating(stream))
print("  first repeating in [1,2,3]:", first_repeating([1, 2, 3]))

print("\n" + "=" * 60)
print("6. Complementary counting (pairs that match a rule)")
print("=" * 60)


def count_pairs_with_sum(nums, target):
    """Count index pairs whose values sum to target. O(n)."""
    counts = {}
    total = 0
    for value in nums:
        total += counts.get(target - value, 0)      # partners seen so far
        counts[value] = counts.get(value, 0) + 1
    return total


def count_pairs_with_difference(nums, difference):
    """Count pairs with |a - b| == difference using a set."""
    seen = set(nums)
    return sum(1 for value in set(nums) if value + difference in seen)


print("  pairs summing to 6 in [1,2,3,4,5]:", count_pairs_with_sum([1, 2, 3, 4, 5], 6))
print("  pairs summing to 10 in [5,5,5,5]:", count_pairs_with_sum([5, 5, 5, 5], 10))
print("  pairs with difference 3 in [1,2,4,5,7]:", count_pairs_with_difference([1, 2, 4, 5, 7], 3))

print("\n" + "=" * 60)
print("7. Longest consecutive sequence (the set trick)")
print("=" * 60)


def longest_consecutive(nums):
    """O(n) — only start counting from the BEGINNING of a run.

    Sorting would be O(n log n); a set lets us check "is value-1 present?" in
    O(1), so each number is visited at most twice.
    """
    values = set(nums)
    best = 0
    best_run = []
    for value in values:
        if value - 1 in values:         # not the start of a run -> skip
            continue
        length = 1
        while value + length in values:
            length += 1
        if length > best:
            best = length
            best_run = list(range(value, value + length))
    return best, best_run


for candidate in [[100, 4, 200, 1, 3, 2], [0, 3, 7, 2, 5, 8, 4, 6, 0, 1], [1, 1, 1]]:
    length, run = longest_consecutive(candidate)
    print(f"  {str(candidate):<38} -> length {length} {run}")

print("\n" + "=" * 60)
print("8. Set operations on collections")
print("=" * 60)


def compare_collections(team_a, team_b):
    a, b = set(team_a), set(team_b)
    return {
        "both": sorted(a & b),
        "only_a": sorted(a - b),
        "only_b": sorted(b - a),
        "all": sorted(a | b),
        "a_is_subset_of_b": a <= b,
        "disjoint": a.isdisjoint(b),
    }


py_team = ["ravi", "priya", "asha", "dev"]
js_team = ["priya", "asha", "meera"]
for key, value in compare_collections(py_team, js_team).items():
    print(f"  {key:<18}: {value}")

print("\n" + "=" * 60)
print("9. Real-world shape: a tiny inventory/inverted index")
print("=" * 60)

documents = {
    "doc1": "python is fun and python is fast",
    "doc2": "java is verbose but fast",
    "doc3": "python and java are both popular",
}

index = defaultdict(set)
for doc_id, text in documents.items():
    for word in text.lower().split():
        index[word].add(doc_id)                 # inverted index: word -> docs

print("  index for 'python':", sorted(index["python"]))
print("  index for 'fast'  :", sorted(index["fast"]))
print("  docs with BOTH python and java:",
      sorted(index["python"] & index["java"]))
print("  top words by document frequency:",
      sorted(((word, len(docs)) for word, docs in index.items()), key=lambda pair: -pair[1])[:4])


def search(query):
    """AND search across documents using the inverted index."""
    terms = query.lower().split()
    if not terms:
        return []
    result = set(documents)
    for term in terms:
        result &= index.get(term, set())
    return sorted(result)


print("  search('python fast')  :", search("python fast"))
print("  search('java popular') :", search("java popular"))
print("  search('cobol')        :", search("cobol"))

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  dict/set lookup, insert, delete ..... O(1) average (O(n) worst case)
  build a Counter from n items ........ O(n)
  two-sum with a dict ................. O(n) time, O(n) space
  dedupe with dict.fromkeys ........... O(n)
  grouping with defaultdict ........... O(n)
  longest consecutive with a set ...... O(n)
  sorting the keys afterwards ......... O(k log k)
  ⚠  dict order is insertion order — never rely on it for "sorted" output""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `three_sum_exists(nums, target)` -> True/False using a set (O(n^2) is fine
#    here — think about why you cannot do better easily).
# 2. `mode(nums)` -> the most frequent value AND how many times it occurs.
# 3. `symmetric_difference_pairs(a, b)` -> elements in exactly one of the lists.
# 4. `subarray_sum_zero(nums)` uses prefix sums + a dict: return True if any
#    contiguous subarray sums to zero.
# 5. `top_k_frequent(nums, k)` -> the k most frequent values (use Counter, then
#    sort — later dsa_10 shows the heap version).
# 6. `is_isomorphic(a, b)` -> "egg"/"add" True, "foo"/"bar" False, using two
#    dicts (mapping both ways).
# 7. `find_missing_and_duplicate(nums)` from 1..n, using a set.
# 8. `longest_subarray_with_distinct_values(nums)` — sliding window with a dict.
print()
print("Now run: python3 dsa/dsa_04_sorting.py")
