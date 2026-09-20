"""
DSA 02 · Strings as arrays of characters

A string is an immutable sequence of characters, so every array technique
applies — indexing, two pointers, sliding windows. The twist is that you cannot
modify it in place: you build a NEW string (or work on a list and `join`).

Vocabulary you need
-------------------
* **palindrome**   — reads the same forwards and backwards: "racecar"
* **anagram**      — same characters, different order: "listen"/"silent"
* **substring**    — contiguous slice: "ell" in "hello"
* **subsequence**  — same order, not necessarily contiguous: "hlo" in "hello"
* **permutation**  — a rearrangement of all the characters

Core toolkit
------------
    len(s)             O(1)
    s[i]               O(1)
    s[i:j]             O(j-i)  (copies!)
    s + t              O(len(s) + len(t))
    "".join(parts)     O(total length)   ← the fast way to build strings
    x in s             O(len(s) * len(x)) worst case
    s == t             O(len(s))
    sorted(s)          O(k log k) where k is the alphabet used

Character tricks
----------------
    ord(ch) - ord("a")          letter -> 0..25 (array index!)
    chr(97)                     number -> letter
    ch.lower() / ch.isalpha() / ch.isdigit() / ch.isalnum() / ch.isspace()

Techniques
----------
1. Two pointers (palindrome checks, reversing)
2. Frequency counting with a dict/Counter (anagrams, first unique char)
3. Sliding window (longest substring without repeats, fixed-size windows)
4. Building output with a list + join
5. Early exit (return as soon as you know)
"""

from collections import Counter, defaultdict

print("=" * 60)
print("1. Palindrome: three ways")
print("=" * 60)

def is_palindrome_slice(text):
    """Clean, then compare against the reverse. O(n) time, O(n) space (easy)."""
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]


def is_palindrome_two_pointers(text):
    """O(n) time, O(1) space — the version interviewers want."""
    left, right = 0, len(text) - 1
    while left < right:
        if not text[left].isalnum():
            left += 1
            continue
        if not text[right].isalnum():
            right -= 1
            continue
        if text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


def is_palindrome_number(n):
    """Numbers: reverse the digits and compare (no string conversion)."""
    if n < 0:
        return False
    original, reversed_number = n, 0
    while n:
        reversed_number = reversed_number * 10 + n % 10
        n //= 10
    return original == reversed_number


for text in ["racecar", "A man, a plan, a canal: Panama", "hello", "", "ab"]:
    print(f'  {text!r:34} slice={is_palindrome_slice(text)!s:5} '
          f'two_pointers={is_palindrome_two_pointers(text)}')
print("  palindrome numbers:", [n for n in range(100, 200) if is_palindrome_number(n)][:8], "...")

print("\n" + "=" * 60)
print("2. Anagrams: sorting vs counting")
print("=" * 60)

def are_anagrams_sort(a, b):
    """O(n log n): sort both and compare."""
    clean = lambda s: sorted(ch.lower() for ch in s if ch.isalnum())
    return clean(a) == clean(b)


def are_anagrams_count(a, b):
    """O(n): count characters, compare counters. The better answer."""
    clean = lambda s: Counter(ch.lower() for ch in s if ch.isalnum())
    return clean(a) == clean(b)


pairs = [("listen", "silent"), ("hello", "world"), ("Dormitory", "dirty room"), ("abc", "ab")]
for a, b in pairs:
    print(f"  {a!r:12} vs {b!r:14} sort={are_anagrams_sort(a, b)!s:5} count={are_anagrams_count(a, b)}")


def group_anagrams(words):
    """Group words that are anagrams of each other. O(n * k log k)."""
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word.lower()))       # the anagram "fingerprint"
        groups[key].append(word)
    return list(groups.values())


print("  group_anagrams:", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))

print("\n" + "=" * 60)
print("3. Frequency counting")
print("=" * 60)

def first_non_repeating(text):
    """First character that appears exactly once; None if all repeat."""
    counts = Counter(text)
    for char in text:                      # keep the original order
        if counts[char] == 1:
            return char
    return None


def most_common_char(text):
    """Most frequent character; ties go to whichever appears first."""
    if not text:
        return None
    counts = Counter(text)
    return max(counts, key=counts.get)


def can_form_palindrome(text):
    """A palindrome needs at most ONE character with an odd count."""
    odd_count = sum(count % 2 for count in Counter(text.lower()).values() if count)
    return odd_count <= 1


for text in ["aabbcdd", "abracadabra", "aabbcc", ""]:
    print(f"  {text!r:14} first_non_repeating={first_non_repeating(text)!r:6} "
          f"most_common={most_common_char(text)!r}")

print("  can_form_palindrome('carrace'):", can_form_palindrome("carrace"),
      "| ('abc'):", can_form_palindrome("abc"))

print("\n" + "=" * 60)
print("4. Reverse words and reverse characters")
print("=" * 60)

def reverse_words(sentence):
    """'the sky is blue' -> 'blue is sky the'. O(n)."""
    return " ".join(sentence.split()[::-1])


def reverse_each_word(sentence):
    """'abc def' -> 'cba fed'."""
    return " ".join(word[::-1] for word in sentence.split())


def reverse_words_in_place_list(sentence):
    """The in-place idea (works on a list of chars, which is what an interviewer
    asking for O(1) space means). Characters first, then each word."""
    chars = list(sentence.strip())
    chars.reverse()
    start = 0
    for index in range(len(chars) + 1):
        if index == len(chars) or chars[index] == " ":
            chars[start:index] = chars[start:index][::-1]
            start = index + 1
    return "".join(chars)


print("  reverse_words     :", reverse_words("the sky is blue"))
print("  reverse_each_word :", reverse_each_word("abc def gh"))
print("  in place (list)   :", reverse_words_in_place_list("the sky is blue"))

print("\n" + "=" * 60)
print("5. Sliding window: longest substring without repeats")
print("=" * 60)

def longest_unique_substring(s):
    """O(n) with a dict of last-seen index. The classic interval problem."""
    last_seen = {}
    best = 0
    start = 0
    best_span = (0, 0)
    for index, char in enumerate(s):
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1        # jump past the previous occurrence
        last_seen[char] = index
        if index - start + 1 > best:
            best = index - start + 1
            best_span = (start, index + 1)
    return best, s[best_span[0]:best_span[1]]


for text in ["abcabcbb", "bbbbb", "pwwkew", "", "abcdef"]:
    length, substring = longest_unique_substring(text)
    print(f"  {text!r:10} -> length {length}, substring {substring!r}")

print("\n" + "=" * 60)
print("6. Character frequency with an array (fast, memory-cheap)")
print("=" * 60)

def char_counts_array(text):
    """Only works for a-z, but it is the fastest and most memory-efficient."""
    counts = [0] * 26
    for char in text.lower():
        if "a" <= char <= "z":
            counts[ord(char) - ord("a")] += 1
    return counts


text = "the quick brown fox"
counts = char_counts_array(text)
print("  counts for 'a'..'z':", {chr(97 + i): c for i, c in enumerate(counts) if c})

def first_unique_with_array(text):
    """First unique character using the array trick."""
    counts = char_counts_array(text)
    for char in text.lower():
        if "a" <= char <= "z" and counts[ord(char) - ord("a")] == 1:
            return char
    return None


print("  first unique in 'aabbcde' :", first_unique_with_array("aabbcde"))
print("  first unique in 'aabbcc'  :", first_unique_with_array("aabbcc"))

print("\n" + "=" * 60)
print("7. Subsequence and substring checks (two pointers)")
print("=" * 60)

def is_subsequence(sub, text):
    """Is `sub` a subsequence of `text`? O(n) two-pointer walk."""
    iterator = iter(text)
    return all(char in iterator for char in sub)     # elegant but cryptic:

def is_subsequence_explicit(sub, text):
    """Same thing written out — use this style while learning."""
    index = 0
    for char in text:
        if index < len(sub) and char == sub[index]:
            index += 1
        if index == len(sub):
            return True
    return index == len(sub)


for sub, text in [("ace", "abcde"), ("aec", "abcde"), ("", "abc"), ("abc", "abc")]:
    print(f"  is_subsequence({sub!r:6}, {text!r:8}) = {is_subsequence_explicit(sub, text)}")

print("\n" + "=" * 60)
print("8. Run-length encoding / compression (build a string properly)")
print("=" * 60)

def run_length_encode(text):
    """'aaabbc' -> 'a3b2c1'. This is where a list + join beats `+=`."""
    if not text:
        return ""
    parts = []
    current = text[0]
    count = 1
    for char in text[1:]:
        if char == current:
            count += 1
        else:
            parts.append(f"{current}{count}")
            current, count = char, 1
    parts.append(f"{current}{count}")
    return "".join(parts)          # O(n) instead of O(n^2) with +=


def run_length_decode(encoded):
    """'a3b2c1' -> 'aaabbc'."""
    parts = []
    count = ""
    letter = ""
    for char in encoded:
        if char.isdigit():
            count += char
        else:
            if letter:
                parts.append(letter * int(count or 1))
            letter, count = char, ""
    if letter:
        parts.append(letter * int(count or 1))
    return "".join(parts)


for text in ["aaabbc", "abcd", "wwwwwwwwwwww", ""]:
    encoded = run_length_encode(text)
    print(f"  {text!r:16} -> {encoded!r:14} -> {run_length_decode(encoded)!r}")

print("\n" + "=" * 60)
print("9. Common-prefix / common-suffix (shortest-string scan)")
print("=" * 60)

def longest_common_prefix(words):
    """O(total characters): compare against the shortest word only."""
    if not words:
        return ""
    shortest = min(words, key=len)
    for index, char in enumerate(shortest):
        if any(word[index] != char for word in words):
            return shortest[:index]
    return shortest


for words in [["flower", "flow", "flight"], ["dog", "racecar", "car"], ["abc"], []]:
    print(f"  {str(words):<40} -> {longest_common_prefix(words)!r}")

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  palindrome check ................ O(n) time,  O(1) space (two pointers)
  anagram (count) ................. O(n) time,  O(k) space (k = alphabet)
  anagram grouping ................ O(n * k log k)
  first unique char ............... O(n) time,  O(k) space
  longest unique substring ........ O(n) time,  O(k) space (sliding window)
  reverse words ................... O(n) time,  O(n) space
  substring search (naive) ........ O(n * m)   <- use `in`, KMP is O(n+m)
  subsequence check ............... O(n) time,  O(1) space
  building a string with += ....... O(n^2)  ⚠  use "".join(parts)""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `is_rotation(a, b)` -> is b a rotation of a? ("abcde", "cdeab" -> True)
#    Hint: check `len` equal and `b in a + a`.
# 2. `remove_duplicates(text)` keeping the first occurrence of each character.
# 3. `count_words(sentence)` -> dict of word -> count, case-insensitive and
#    punctuation-free.
# 4. `longest_palindromic_substring(s)` -> brute force O(n^3) first, then try
#    the O(n^2) "expand around the centre" trick.
# 5. `is_valid_anagram_shift(a, b)`? Simpler: `capitalise_words(sentence)`.
# 6. `compress(text)` and then make it return the ORIGINAL when the compressed
#    version is not shorter. Then test with "abc" and "aaabbbcccddd".
# 7. `string_permutations(s)` -> all permutations using a recursive helper
#    (preview of dsa_06) — try it before peeking at itertools.
# 8. `word_frequency(text)` -> the 3 most common words with counts, ties broken
#    alphabetically.
print()
print("Now run: python3 dsa/dsa_03_hashmaps.py")
