"""
DSA 06 · Recursion, memoisation & backtracking

Recursion is a function that calls itself on a smaller version of the problem.
It is the foundation of trees (dsa_09), graphs (dsa_11), divide & conquer
(dsa_04) and dynamic programming (dsa_12). Learn it properly once.

The three-part recipe (always the same)
---------------------------------------
1. **Base case** — when is the answer immediate? (n == 0, empty list, leaf node)
2. **Recursive case** — solve a SMALLER version of the same problem.
3. **Combine** — turn the small answer into the answer for the current call.

If you cannot name a strictly smaller sub-problem, recursion will not work.

Mental model: the call stack
----------------------------
Each call gets its own frame with its own variables. `factorial(3)` becomes:

    factorial(3) -> 3 * factorial(2)
                     factorial(2) -> 2 * factorial(1)
                                      factorial(1)  -> base case -> 1
                     = 2 * 1
    = 3 * 2 * 1 = 6

The stack unwinds in reverse order. Cost: O(depth) memory. Python's default
limit is 1000 frames (`sys.getrecursionlimit()`), so deep recursion on linked
lists or long paths must be converted to a loop or an explicit stack.

Recursion vs iteration
----------------------
* Recursion is usually shorter and matches the problem's structure (trees!).
* Iteration is faster and uses O(1) space; do not fear rewriting a recursive
  solution iteratively if the depth is large.

Memoisation: the bridge to dynamic programming
---------------------------------------------
Naive recursive Fibonacci is O(2^n) because it recomputes the same subproblems
over and over. Remember the answers (`@lru_cache` or a dict) and it becomes
O(n). Subproblem + memo = dynamic programming (dsa_12 develops this fully).

Backtracking: recursion that explores choices
---------------------------------------------
Pattern:

    def backtrack(path, choices):
        if is_solution(path):
            record(path)
            return
        for choice in choices:
            if is_valid(choice):
                path.append(choice)          # choose
                backtrack(path, next_choices) # explore
                path.pop()                    # un-choose (the "backtrack")

That choose/explore/un-choose rhythm generates subsets, permutations,
combinations, sudoku solutions, N-queens...

Complexity intuition
--------------------
    T(n) = T(n - 1) + O(1)      -> O(n)          (factorial, sum of a list)
    T(n) = T(n - 1) + T(n - 2)  -> O(2^n)        (naive fibonacci)
    T(n) = 2 * T(n / 2) + O(n)  -> O(n log n)    (merge sort)
    T(n) = 2 * T(n / 2) + O(1)  -> O(n)          (binary search with one call)
    subsets: O(2^n * n)  |  permutations: O(n! * n)
"""

import functools
import sys
import time
from itertools import permutations

print("=" * 60)
print("1. The simplest recursion: counting down and summing")
print("=" * 60)


def countdown(n):
    """Base case + recursive call. Watch the order of prints!"""
    if n <= 0:
        print("     liftoff 🚀")
        return
    print(f"     {n}...")
    countdown(n - 1)


countdown(3)


def recursive_sum(nums):
    """Sum a list without a loop: first element + sum of the rest."""
    if not nums:
        return 0                        # base case: empty list
    return nums[0] + recursive_sum(nums[1:])


print("  recursive_sum([1,2,3,4,5]) =", recursive_sum([1, 2, 3, 4, 5]))
print("  (O(n) time but O(n^2) because slicing copies — use sum() in real code)")


def recursive_len(items):
    if not items:
        return 0
    return 1 + recursive_len(items[1:])


print("  recursive_len('hello') =", recursive_len("hello"))


def recursive_max(nums):
    """Compare the first with the max of the rest."""
    if len(nums) == 1:
        return nums[0]                  # base case: one element
    rest_max = recursive_max(nums[1:])
    return nums[0] if nums[0] > rest_max else rest_max


print("  recursive_max([3, 9, 4, 7]) =", recursive_max([3, 9, 4, 7]))

print("\n" + "=" * 60)
print("2. Factorial and the call stack")
print("=" * 60)


def factorial(n):
    """n! = n * (n-1)!. Trace it mentally before running."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def factorial_traced(n, depth=0):
    """Same thing, printing the stack so you can SEE the unwinding."""
    indent = "   " * depth
    print(f"{indent}factorial({n}) called")
    if n <= 1:
        print(f"{indent}-> base case, returning 1")
        return 1
    result = n * factorial_traced(n - 1, depth + 1)
    print(f"{indent}-> returning {result} up to the caller")
    return result


print("  factorial(5) =", factorial(5), "| factorial(20) =", factorial(20))
print("  factorial(500) =", str(factorial(500))[:30], "... (Python ints never overflow)")
print()
print("  trace of factorial(3):")
factorial_traced(3)

print("\n" + "=" * 60)
print("3. Fibonacci: exponential -> linear with memoisation")
print("=" * 60)


def fib_naive(n):
    """O(2^n). The recursion tree recomputes everything."""
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, memo=None):
    """O(n) time, O(n) space — remember subproblem answers."""
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


@functools.lru_cache(maxsize=None)
def fib_cached(n):
    """The same memoisation, applied by a decorator."""
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


def fib_iterative(n):
    """O(n) time, O(1) space — usually the best answer for Fibonacci."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


for n in [10, 20, 30]:
    start = time.perf_counter()
    naive = fib_naive(n)
    naive_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    memo = fib_memo(n)
    memo_ms = (time.perf_counter() - start) * 1000
    print(f"  fib({n:>2}): naive {naive:>8} in {naive_ms:8.3f} ms | "
          f"memoised {memo:>8} in {memo_ms:6.3f} ms")

print("  fib_cached(100) =", fib_cached(100))
print("  fib_iterative(100) =", fib_iterative(100))
print("  fib_cached(200) =", str(fib_cached(200))[:40], "...")
print("  (at n=35 the naive version already takes ~1 second)")

print("\n" + "=" * 60)
print("4. Recursion depth limits (know this trap)")
print("=" * 60)
print("  sys.getrecursionlimit() =", sys.getrecursionlimit())


def sum_to(n):
    if n == 0:
        return 0
    return n + sum_to(n - 1)


print("  sum_to(900) =", sum_to(900))
try:
    sum_to(5000)
except RecursionError as exc:
    print("  sum_to(5000) ->", type(exc).__name__, "- use a loop instead")


def sum_to_iterative(n):
    return n * (n + 1) // 2


print("  sum_to_iterative(5000) =", sum_to_iterative(5000), "(and it is O(1)!)")
print("  If you must recurse deeply: sys.setrecursionlimit(10000) — but each")
print("  frame still costs memory, so prefer an explicit stack (see dsa_11).")

print("\n" + "=" * 60)
print("5. Divide and conquer: merge sort and binary search")
print("=" * 60)


def merge_sorted(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(items):
    """T(n) = 2T(n/2) + O(n) -> O(n log n)."""
    if len(items) <= 1:
        return items
    middle = len(items) // 2
    return merge_sorted(merge_sort(items[:middle]), merge_sort(items[middle:]))


print("  merge_sort([5,1,4,2,8,3]) =", merge_sort([5, 1, 4, 2, 8, 3]))


def binary_search(nums, target, left=None, right=None, depth=0):
    """T(n) = T(n/2) + O(1) -> O(log n) calls."""
    if left is None:
        left, right = 0, len(nums) - 1
    if left > right:
        return -1
    middle = (left + right) // 2
    if nums[middle] == target:
        return middle
    if nums[middle] < target:
        return binary_search(nums, target, middle + 1, right, depth + 1)
    return binary_search(nums, target, left, middle - 1, depth + 1)


print("  binary_search([1..13], 11) =", binary_search(list(range(1, 14, 2)), 11))

print("\n" + "=" * 60)
print("6. Backtracking I: generating subsets (the power set)")
print("=" * 60)


def subsets(nums):
    """Every subset: 2^n of them. For each element: include it, or don't."""
    result = []

    def explore(index, path):
        if index == len(nums):           # made a decision for every element
            result.append(path[:])       # copy! path keeps mutating
            return
        explore(index + 1, path)         # choice 1: skip nums[index]
        path.append(nums[index])         # choice 2: take nums[index]
        explore(index + 1, path)
        path.pop()                       # un-choose (backtrack)

    explore(0, [])
    return result


for values in [[1, 2], [1, 2, 3]]:
    generated = subsets(values)
    print(f"  subsets({values}) -> {len(generated)} sets: {generated}")
print("  2^10 =", len(subsets(list(range(10)))), "subsets for a 10-element list")


def subsets_bitmask(nums):
    """The same result with bit tricks — one pass, no recursion."""
    result = []
    for mask in range(1 << len(nums)):            # 0 .. 2^n - 1
        subset = [nums[i] for i in range(len(nums)) if mask & (1 << i)]
        result.append(subset)
    return result


print("  bitmask version gives the same 2^n subsets:",
      len(subsets_bitmask([1, 2, 3])), "sets")
print("  equal to the recursive version:",
      sorted(map(tuple, subsets([1, 2, 3]))) == sorted(map(tuple, subsets_bitmask([1, 2, 3]))))

print("\n" + "=" * 60)
print("7. Backtracking II: permutations")
print("=" * 60)


def permutations_recursive(items):
    """n! arrangements. Swap-based, in place, fast."""
    result = []

    def backtrack(start):
        if start == len(items):
            result.append(items[:])
            return
        for index in range(start, len(items)):
            items[start], items[index] = items[index], items[start]   # choose
            backtrack(start + 1)                                      # explore
            items[start], items[index] = items[index], items[start]   # un-choose

    backtrack(0)
    return result


print("  permutations([1,2,3]) ->", permutations_recursive([1, 2, 3]))
print("  3! =", len(permutations_recursive([1, 2, 3])), "| 5! =",
      len(permutations_recursive([1, 2, 3, 4, 5])))
print("  itertools version:", [list(p) for p in permutations([1, 2], 2)])


def permutations_of_string(text):
    """Permutations of a string with duplicate handling."""
    results = set()

    def backtrack(current, remaining):
        if not remaining:
            results.add(current)
            return
        for index, char in enumerate(remaining):
            backtrack(current + char, remaining[:index] + remaining[index + 1:])

    backtrack("", text)
    return sorted(results)


print("  permutations_of_string('aab') ->", permutations_of_string("aab"))

print("\n" + "=" * 60)
print("8. Backtracking III: combination sum & N-Queens")
print("=" * 60)


def combination_sum(candidates, target):
    """All combinations that add up to target (each number reusable)."""
    results = []

    def backtrack(start, remaining, path):
        if remaining == 0:
            results.append(path[:])
            return
        if remaining < 0:
            return                                     # prune: overshot
        for index in range(start, len(candidates)):
            if candidates[index] > remaining:
                continue                               # prune: too big
            path.append(candidates[index])
            backtrack(index, remaining - candidates[index], path)   # reuse allowed
            path.pop()

    backtrack(0, target, [])
    return results


print("  combination_sum([2,3,5], 8) ->", combination_sum([2, 3, 5], 8))


def solve_n_queens(n):
    """Place n queens so none attack each other. Returns all boards."""
    solutions = []
    columns = set()
    diagonals_down = set()          # row - column
    diagonals_up = set()            # row + column

    def backtrack(row, placed):
        if row == n:
            solutions.append(placed[:])
            return
        for column in range(n):
            if (column in columns or (row - column) in diagonals_down
                    or (row + column) in diagonals_up):
                continue
            columns.add(column)
            diagonals_down.add(row - column)
            diagonals_up.add(row + column)
            placed.append(column)
            backtrack(row + 1, placed)
            placed.pop()
            columns.discard(column)
            diagonals_down.discard(row - column)
            diagonals_up.discard(row + column)

    backtrack(0, [])
    return solutions


for n in [4, 6, 8]:
    boards = solve_n_queens(n)
    print(f"  {n}-queens: {len(boards)} solutions", end="")
    if n == 4:
        print(f"  first: {boards[0]}")
    else:
        print()


def draw_board(solution):
    size = len(solution)
    return "\n".join(
        "     " + " ".join("Q" if column == row_queen else "." for column in range(size))
        for row_queen in solution
    )


print("  one 4-queens solution:")
print(draw_board(solve_n_queens(4)[0]))

print("\n" + "=" * 60)
print("9. Backtracking IV: a maze / grid path (preview of dsa_11)")
print("=" * 60)

maze = [
    "S..#",
    ".#..",
    "...#",
    "##.E",
]


def solve_maze(grid):
    """Find a path from S to E with DFS + backtracking."""
    rows, columns = len(grid), len(grid[0])
    start = end = None
    for r in range(rows):
        for c in range(columns):
            if grid[r][c] == "S":
                start = (r, c)
            elif grid[r][c] == "E":
                end = (r, c)

    path = []
    visited = set()

    def explore(position):
        if position == end:
            path.append(position)
            return True
        row, column = position
        if not (0 <= row < rows and 0 <= column < columns):
            return False
        if (row, column) in visited or grid[row][column] == "#":
            return False
        # ⚠  the classic bug here is adding an INT while checking a TUPLE
        #    (visited.add(row * columns + column)) — the marker never matches,
        #    and the recursion walks forever until RecursionError.
        visited.add((row, column))
        path.append(position)
        for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if explore((row + delta_row, column + delta_column)):
                return True
        path.pop()                       # dead end -> backtrack
        return False

    return path if explore(start) else None


path = solve_maze(maze)
print("  maze:")
for line in maze:
    print("     ", line)
print("  path:", path)
print("  steps:", len(path) - 1 if path else None)

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  sum/max of a list ............ O(n) time,      O(n) stack
  factorial(n) ................. O(n)
  naive fibonacci .............. O(2^n)   <- memoise it
  memoised fibonacci ........... O(n) time,      O(n) space
  merge sort ................... O(n log n) time, O(n) + O(log n) stack
  subsets ...................... O(2^n * n)
  permutations ................. O(n! * n)
  combination sum .............. exponential in the worst case (but pruned heavily)
  N-queens ..................... O(n!) with pruning; n=8 -> 92 solutions""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `power(base, exponent)` recursively (handle exponent = 0, odd, even).
#    Bonus: do it in O(log n) with fast exponentiation.
# 2. `reverse_string_recursive(s)` and `is_palindrome_recursive(s)`.
# 3. `sum_digits_recursive(9876)` -> 30.
# 4. `count_paths(rows, cols)` from the top-left to the bottom-right moving only
#    right/down — write the recursion, then memoise it, then do it with a loop.
# 5. `generate_parentheses(n)` -> all valid combinations of n pairs of brackets.
# 6. `letter_combinations("23")` -> ["ad","ae",...] (phone keypad, backtracking).
# 7. `word_search(board, word)` -> does the word exist in the grid (backtracking
#    with visited tracking)?
# 8. `combination_sum_unique(candidates, target)` -> each number used once.
# 9. `tower_of_hanoi(n)` -> print the moves; count them. 2^n - 1 moves.
print()
print("Now run: python3 dsa/dsa_07_stacks_queues.py")
