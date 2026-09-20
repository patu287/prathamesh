"""
LESSON 04 · Strings in depth

Strings are sequences of characters. DSA with strings is 80% of interviews,
so this lesson matters.

# Creating strings
    s = "hello"        t = 'hello'
    u = '''a triple-quoted string
    can span several lines'''

# Indexing — position starts at 0
    s = "PYTHON"
        P  Y  T  H  O  N
        0  1  2  3  4  5      <- from the front
       -6 -5 -4 -3 -2 -1      <- from the back

    s[0]    -> 'P'      s[-1]  -> 'N'      s[2] -> 'T'

    s[99]   -> IndexError: string index out of range

# Slicing — s[start:stop:step], stop is EXCLUDED
    s[1:4]   -> 'YTH'      s[:3]   -> 'PYT'     s[3:]  -> 'HON'
    s[-2:]   -> 'ON'       s[:]    -> whole string
    s[::2]   -> 'PTO'      s[::-1] -> 'NOHTYP'  <- reverse, a classic trick

# Strings are IMMUTABLE
    s[0] = "J"    -> TypeError: 'str' object does not support item assignment
You build new strings instead:  s = "J" + s[1:]

# Concatenation and repetition
    "ab" + "cd"  -> "abcd"        "ab" * 3 -> "ababab"

# The methods you must know (strings never change; these RETURN new strings)
    s.upper() / s.lower() / s.title() / s.capitalize() / s.swapcase()
    s.strip()      -> remove whitespace at both ends ("  hi \n" -> "hi")
    s.lstrip()/s.rstrip()
    s.replace("a", "b")
    s.split()              -> ["the","words"]      split on whitespace
    s.split(",")           -> split on a delimiter
    s.splitlines()
    ",".join(["a","b"])    -> "a,b"                the reverse of split
    s.find("th")           -> index or -1
    s.count("a")           -> how many times
    s.startswith("he") / s.endswith("lo")
    s.isdigit() / s.isalpha() / s.isalnum() / s.isspace() / s.isupper()
    s.zfill(5)             -> "42" -> "00042"

# Membership:  "th" in s  -> True/False        (fast, use it constantly)

# Looping
    for ch in s: ...            # each character
    for i, ch in enumerate(s):  # index + character

# Comparing strings
`==` compares content character by character. `<`/`>` compare
alphabetically (by Unicode code point): "apple" < "banana".
"A" < "a" is True because uppercase letters come first in ASCII.

# Characters are secretly numbers
    ord("A") -> 65        chr(65) -> "A"
    ord("a") - ord("a") = 0    <- the trick for counting letters with arrays

# f-strings recap: f"{name}" , f"{value:.2f}" , f"{name!r}"

# Escaping
    "\\n" newline   "\\t" tab   "\\\\" backslash   "\\"" quote inside quotes
    r"C:\\new"  <- raw string: backslashes are literal
"""

print("=" * 60)
print("1. Indexing and slicing")
print("=" * 60)
s = "PYTHON"
print("s           =", s)
print("s[0], s[1]  =", s[0], s[1])
print("s[-1], s[-2]=", s[-1], s[-2])
print("s[1:4]      =", repr(s[1:4]))
print("s[:3]       =", repr(s[:3]))
print("s[3:]       =", repr(s[3:]))
print("s[:]        =", repr(s[:]))
print("s[::2]      =", repr(s[::2]))
print("s[::-1]     =", repr(s[::-1]), "  <- reverse")
print("len(s)      =", len(s))

print("\n" + "=" * 60)
print("2. Immutability (and how to 'change' a string)")
print("=" * 60)
word = "cat"
try:
    word[0] = "b"
except TypeError as exc:
    print("word[0] = 'b' ->", type(exc).__name__, "-", exc)
new_word = "b" + word[1:]              # build a new string instead
print("'b' + word[1:] ->", new_word)
print("upper() gives a NEW string:", new_word.upper(), "| original still:", new_word)

print("\n" + "=" * 60)
print("3. Methods round-trip")
print("=" * 60)
sentence = "  Python is a great language  "
print("original      :", repr(sentence))
print("strip()       :", repr(sentence.strip()))
print("lower()       :", repr(sentence.strip().lower()))
print("title()       :", repr(sentence.strip().title()))
print("replace a->o  :", repr(sentence.strip().replace("a", "o")))
print("split()       :", sentence.split())
print("count('a')    :", sentence.count("a"))
print("find('great') :", sentence.find("great"))
print("find('xyz')   :", sentence.find("xyz"), " <- -1 means 'not found'")
print("'great' in s  :", "great" in sentence)
print("startswith(' '):", sentence.startswith(" "), "| endswith(' '):", sentence.endswith(" "))

csv = "ravi,priya,asha,dev"
names = csv.split(",")
print("\nsplit(',')    :", names)
print("' | '.join   :", " | ".join(names))
print("'-'.join('abc'):", "-".join("abc"))

print("\n" + "=" * 60)
print("4. Character checks")
print("=" * 60)
for value in ["42", "3.14", "abc", "abc123", "  ", "Hello", "hello"]:
    print(f"  {value!r:10} isdigit={value.isdigit()!s:5} isalpha={value.isalpha()!s:5} "
          f"isalnum={value.isalnum()!s:5} isspace={value.isspace()!s:5}")

print("\n" + "=" * 60)
print("5. Looping over a string")
print("=" * 60)
vowels = "aeiou"
count = 0
for ch in "programming":
    if ch in vowels:
        count += 1
print("vowels in 'programming':", count)

for index, ch in enumerate("abc"):
    print(f"  index {index} -> {ch}")

print("\n" + "=" * 60)
print("6. ord / chr — turning characters into numbers")
print("=" * 60)
print("ord('A') =", ord("A"), "| ord('a') =", ord("a"), "| chr(97) =", repr(chr(97)))
letters = [0] * 26
for ch in "banana":
    letters[ord(ch) - ord("a")] += 1
print("letter counts from 'banana':",
      {chr(ord('a') + i): c for i, c in enumerate(letters) if c})
print("(that dict comprehension is lesson 12 — just admire it for now)")

print("\n" + "=" * 60)
print("7. Palindrome — your first string algorithm, 3 ways")
print("=" * 60)
candidate = "A man, a plan, a canal: Panama"

def palindrome_slice(text):
    """Simplest: clean the text, then compare with its reverse."""
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

def palindrome_two_pointers(text):
    """Classic two-pointer walk — O(n) time, O(1) extra space."""
    left, right = 0, len(text) - 1
    while left < right:
        while left < right and not text[left].isalnum():
            left += 1
        while left < right and not text[right].isalnum():
            right -= 1
        if text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True

print("slice version      :", palindrome_slice(candidate))
print("two-pointer version:", palindrome_two_pointers(candidate))
print("'hello'            :", palindrome_two_pointers("hello"))
print("'abba'             :", palindrome_two_pointers("abba"))

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. Reverse the words (not letters) of "I love Python" -> "Python love I".
#    Hint: split(), reverse the list, join(" ").
# 2. Count how many times each letter appears in your full name.
# 3. Print your name in a "box":
#        ***********
#        *  Ravi   *
#        ***********
# 4. Check if a string is a valid "shouting" string: all letters uppercase and
#    at least one letter (use isupper(), isalpha(), and any()).
# 5. Given "2026-09-20", print day/month/year separately (split("-")).
# 6. Build a simple Censor: replace every vowel in a sentence with "*".
print()
print("Lesson 04 done — now do exercises/ex_04_strings.py ✅")
