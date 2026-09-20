"""
DSA 12 · Dynamic programming (DP)

DP is recursion + memory. If a problem keeps recomputing the same subproblems,
store the answers. That is the whole idea; everything else is bookkeeping.

How to recognise a DP problem
-----------------------------
1. You are asked for an optimal value (min/max), a count, or a yes/no.
2. The problem has **overlapping subproblems** — the same question shows up
   again and again (like fib(5) being needed by fib(6) and fib(7)).
3. It has **optimal substructure** — the best answer for n is built from the
   best answers for smaller inputs.

Recipe
------
1. Write the brute-force recursion. Say out loud what the function means:
   "dp(i) = the best value using the first i items".
2. Find the base case(s).
3. Write the recurrence: how does dp(i) depend on smaller i?
4. Memoise it (top-down) with @lru_cache or a dict. SAME complexity as the loop.
5. Optional but recommended: convert to a bottom-up table (usually faster, and
   often allows O(1) space by keeping only the last two rows).
6. State the complexity: number of subproblems × work per subproblem.

Top-down vs bottom-up
---------------------
| Top-down (memoised recursion)     | Bottom-up (table/iteration)      |
|-----------------------------------|----------------------------------|
| only computes needed states       | computes all states              |
| natural to write from the recursion| usually faster, no recursion limit|
| recursion overhead                | harder to get the fill order right|
Both are equally correct. Start top-down; convert if you need speed or space.

The four classic shapes
-----------------------
1. **1-D, linear** — climb stairs, house robber, min cost to reach the end
2. **2-D grids/strings** — unique paths, edit distance, longest common subsequence
3. **Knapsack** — pick items with capacity limits, coin change
4. **Interval / sequence** — longest increasing subsequence, palindromes

⚠  Keep the *meaning* of each cell written in a comment. Most DP bugs are
"correct code for the wrong definition of dp[i]".
"""

from functools import lru_cache
import time

print("=" * 60)
print("1. Fibonacci: recursion -> memo -> table -> O(1) space")
print("=" * 60)


def fib_recursive(n):
    """O(2^n) — the problem DP was invented to fix."""
    return n if n < 2 else fib_recursive(n - 1) + fib_recursive(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n):
    """Top-down DP: O(n) time, O(n) space. Same recursion, plus memory."""
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):
    """Bottom-up DP: fill a table from the smallest case upward."""
    table = [0] * (n + 1)
    table[1] = 1
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table[n]


def fib_constant_space(n):
    """Only the last two values matter -> O(1) space. The final optimisation."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


for n in [10, 30, 100]:
    print(f"  fib({n:>3}): recursive={fib_recursive(min(n, 30)):<10} "
          f"memo={fib_memo(n):<22} table={fib_table(n):<22} "
          f"constant-space={fib_constant_space(n)}")

print("\n" + "=" * 60)
print("2. Climbing stairs (the gateway DP)")
print("=" * 60)


def climb_stairs(n):
    """You climb 1 or 2 steps at a time; how many distinct ways to reach n?"""
    if n <= 2:
        return n
    two_back, one_back = 1, 2             # ways to reach step 1 and step 2
    for _ in range(3, n + 1):
        two_back, one_back = one_back, two_back + one_back
    return one_back


print("  stairs: ", [(n, climb_stairs(n)) for n in range(1, 9)])
print("  it is Fibonacci in disguise (shifted by one)")


def min_cost_climbing(cost):
    """Pay cost[i] to step on stair i; find the cheapest way to the top."""
    one_back = two_back = 0
    for index in range(len(cost)):
        one_back, two_back = cost[index] + min(one_back, two_back), one_back
    return min(one_back, two_back)


print("  min cost for [10,15,20]:", min_cost_climbing([10, 15, 20]),
      "| for [1,100,1,1,1,100,1,1,100,1]:", min_cost_climbing([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]))

print("\n" + "=" * 60)
print("3. House robber (take-or-skip decisions)")
print("=" * 60)


def rob(houses):
    """Max money with no two adjacent houses robbed. O(n) time, O(1) space."""
    previous, current = 0, 0
    for money in houses:
        previous, current = current, max(current, previous + money)
    return current


def rob_with_choice(houses):
    """Same, but showing the table so you can see the recurrence."""
    if not houses:
        return 0, []
    n = len(houses)
    table = [0] * (n + 1)                 # table[i] = best using the first i houses
    chosen = [False] * (n + 1)
    table[1] = houses[0]
    chosen[1] = True
    for i in range(2, n + 1):
        skip = table[i - 1]
        take = table[i - 2] + houses[i - 1]
        if take > skip:
            table[i] = take
            chosen[i] = True
        else:
            table[i] = skip
    picked = []
    i = n
    while i > 0:
        if chosen[i]:
            picked.append(houses[i - 1])
            i -= 2
        else:
            i -= 1
    return table[n], picked[::-1]


for houses in [[1, 2, 3, 1], [2, 7, 9, 3, 1], [5, 1, 1, 5]]:
    best, picked = rob_with_choice(houses)
    print(f"  houses {str(houses):<22} -> best {best:>3}  (robbed {picked})  simple version {rob(houses)}")


def rob_circular(houses):
    """Same, but the houses are in a circle so the first and last are adjacent."""
    if not houses:
        return 0
    if len(houses) == 1:
        return houses[0]
    return max(rob(houses[:-1]), rob(houses[1:]))     # exclude one end each time


print("  circular [2,3,2]:", rob_circular([2, 3, 2]),
      "| [1,2,3,1]:", rob_circular([1, 2, 3, 1]))

print("\n" + "=" * 60)
print("4. Grid DP: unique paths & min path sum")
print("=" * 60)


def unique_paths(rows, columns):
    """Moves: right/down only. O(rows*cols) time, O(columns) space."""
    row = [1] * columns                    # ways to reach each cell of the top row
    for _ in range(1, rows):
        for column in range(1, columns):
            row[column] += row[column - 1]  # from above (old value) + from the left
    return row[-1]


print("  unique paths 3x7:", unique_paths(3, 7), "| 3x3:", unique_paths(3, 3),
      "| C(4,2) = 6 ✔")
print("  unique paths 10x10:", unique_paths(10, 10))


def min_path_sum(grid):
    """Cheapest top-left to bottom-right path moving right/down."""
    rows, columns = len(grid), len(grid[0])
    table = [row[:] for row in grid]
    for column in range(1, columns):
        table[0][column] += table[0][column - 1]         # only from the left
    for row in range(1, rows):
        table[row][0] += table[row - 1][0]               # only from above
    for row in range(1, rows):
        for column in range(1, columns):
            table[row][column] += min(table[row - 1][column], table[row][column - 1])
    return table[-1][-1]


cost_grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
print("  grid:", cost_grid)
print("  min path sum:", min_path_sum(cost_grid), "(1->3->1->1->1 = 7)")


def max_path_sum_pyramid(triangle):
    """Classic triangle problem: work bottom-up, O(n) space."""
    best = triangle[-1][:]                 # start with the bottom row
    for row in range(len(triangle) - 2, -1, -1):
        for column in range(len(triangle[row])):
            best[column] = triangle[row][column] + max(best[column], best[column + 1])
    return best[0]


triangle = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]
print("  triangle:", triangle)
print("  max path sum:", max_path_sum_pyramid(triangle), "(2->4->7->8 = 21)")

print("\n" + "=" * 60)
print("5. Knapsack family")
print("=" * 60)


def coin_change(coins, amount):
    """Fewest coins that make `amount`, or -1. Bottom-up over the amount."""
    infinity = float("inf")
    table = [0] + [infinity] * amount      # table[a] = fewest coins for a
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and table[value - coin] + 1 < table[value]:
                table[value] = table[value - coin] + 1
    return -1 if table[amount] == infinity else table[amount]


print("  fewest coins [1,2,5] for 11:", coin_change([1, 2, 5], 11), "(5+5+1)")
print("  fewest coins [2] for 3     :", coin_change([2], 3), "(impossible)")
print("  fewest coins [1,5,10] for 27:", coin_change([1, 5, 10], 27), "(greedy would also work here)")


def count_coin_combinations(coins, amount):
    """How many combinations make the amount? (Order does not matter.)

    The loop order matters: coins OUTSIDE means each combination is counted
    once (1+2 is the same as 2+1). Swap them and you count permutations.
    """
    table = [0] * (amount + 1)
    table[0] = 1                           # one way to make zero: use nothing
    for coin in coins:
        for value in range(coin, amount + 1):
            table[value] += table[value - coin]
    return table[amount]


print("  combinations of [1,2,5] for 5       :", count_coin_combinations([1, 2, 5], 5),
      "(5, 2+2+1, 2+1+1+1, 1*5)")
print("  combinations of [2,3,5] for 8       :", count_coin_combinations([2, 3, 5], 8))


def knapsack_01(weights, values, capacity):
    """Each item can be taken at most once. Classic 0/1 knapsack O(n * capacity)."""
    table = [0] * (capacity + 1)           # best value for each capacity
    for index in range(len(weights)):
        # loop backwards so each item is used at most once
        for current in range(capacity, weights[index] - 1, -1):
            table[current] = max(table[current],
                                 table[current - weights[index]] + values[index])
    return table[capacity]


weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
print("  weights:", weights, "values:", values)
for capacity in [4, 5, 7, 10]:
    print(f"    capacity {capacity:>2} -> best value {knapsack_01(weights, values, capacity)}")


def knapsack_items(weights, values, capacity):
    """The same table, but keeping a full 2-D grid so we can rebuild the choice."""
    n = len(weights)
    grid = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for weight in range(capacity + 1):
            grid[i][weight] = grid[i - 1][weight]            # skip item i
            if weights[i - 1] <= weight:
                grid[i][weight] = max(grid[i][weight],
                                      grid[i - 1][weight - weights[i - 1]] + values[i - 1])
    picked = []
    remaining = capacity
    for i in range(n, 0, -1):
        if grid[i][remaining] != grid[i - 1][remaining]:
            picked.append(i - 1)
            remaining -= weights[i - 1]
    return grid[n][capacity], picked[::-1]


best, picked_indexes = knapsack_items(weights, values, 7)
print("  capacity 7 with piece tracking -> value", best,
      "using items", [(weights[i], values[i]) for i in picked_indexes])

print("\n" + "=" * 60)
print("6. String DP: LCS & edit distance")
print("=" * 60)


def longest_common_subsequence(a, b):
    """Length of the longest subsequence present in both (not contiguous!)."""
    rows, columns = len(a), len(b)
    table = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(1, rows + 1):
        for j in range(1, columns + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1          # extend the match
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])   # drop one
    return table[rows][columns]


def lcs_string(a, b):
    """Same table, then walk backwards to rebuild the actual subsequence."""
    rows, columns = len(a), len(b)
    table = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(1, rows + 1):
        for j in range(1, columns + 1):
            table[i][j] = (table[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1]
                           else max(table[i - 1][j], table[i][j - 1]))
    result = []
    i, j = rows, columns
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])
            i -= 1
            j -= 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(result))


pairs = [("abcde", "ace"), ("abc", "abc"), ("abc", "def"), ("AGGTAB", "GXTXAYB")]
for a, b in pairs:
    print(f"  LCS({a!r}, {b!r}) = {longest_common_subsequence(a, b)} -> {lcs_string(a, b)!r}")


def edit_distance(a, b):
    """Levenshtein distance: insert/delete/replace. O(n*m) time and space."""
    rows, columns = len(a), len(b)
    table = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(rows + 1):
        table[i][0] = i                    # delete all of a's prefix
    for j in range(columns + 1):
        table[0][j] = j                    # insert all of b's prefix
    for i in range(1, rows + 1):
        for j in range(1, columns + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1]
            else:
                table[i][j] = 1 + min(table[i - 1][j],        # delete
                                      table[i][j - 1],        # insert
                                      table[i - 1][j - 1])    # replace
    return table[rows][columns]


for a, b in [("kitten", "sitting"), ("flaw", "lawn"), ("abc", "abc")]:
    print(f"  edit_distance({a!r}, {b!r}) = {edit_distance(a, b)}")

print("\n" + "=" * 60)
print("7. Longest increasing subsequence (O(n^2), then O(n log n))")
print("=" * 60)


def lis_dp(nums):
    """table[i] = length of the LIS ENDING at i. O(n^2)."""
    if not nums:
        return 0, []
    table = [1] * len(nums)
    parent = [-1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and table[j] + 1 > table[i]:
                table[i] = table[j] + 1
                parent[i] = j
    best_end = max(range(len(nums)), key=lambda i: table[i])
    sequence = []
    index = best_end
    while index != -1:
        sequence.append(nums[index])
        index = parent[index]
    return table[best_end], sequence[::-1]


def lis_binary_search(nums):
    """O(n log n) with patience sorting (tails + bisect)."""
    import bisect
    tails = []                             # tails[k] = smallest tail of an LIS of length k+1
    for value in nums:
        position = bisect.bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)


for nums in [[10, 9, 2, 5, 3, 7, 101, 18], [3, 10, 2, 1, 20], [7, 7, 7]]:
    length, sequence = lis_dp(nums)
    print(f"  {str(nums):<32} -> length {length} (binary-search version {lis_binary_search(nums)}), LIS {sequence}")

print("\n" + "=" * 60)
print("8. Top-down vs bottom-up, measured")
print("=" * 60)


def coin_change_topdown(coins, amount):
    """Memoised recursion — the same answer as the bottom-up version above."""
    @lru_cache(maxsize=None)
    def solve(remaining):
        if remaining == 0:
            return 0
        if remaining < 0:
            return float("inf")
        return 1 + min(solve(remaining - coin) for coin in coins)

    result = solve(amount)
    return -1 if result == float("inf") else result


for amount in [11, 63, 99]:
    start = time.perf_counter()
    bottom = coin_change([1, 2, 5], amount)
    bottom_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    top = coin_change_topdown((1, 2, 5), amount)
    top_ms = (time.perf_counter() - start) * 1000
    print(f"  amount {amount:>3}: bottom-up {bottom:>3} ({bottom_ms:6.2f} ms) | "
          f"top-down {top:>3} ({top_ms:6.2f} ms)")

print("\n  space optimisation demo: 0/1 knapsack needs only ONE row")
print("  (loop the capacity BACKWARDS so each item is counted once)")

print("\n" + "=" * 60)
print("9. How to attack a new DP problem (checklist)")
print("=" * 60)
print("""  1. What decision am I making at each step?     (take/skip, move, split)
  2. Define the state in words: "dp[i][j] = the best ___ using ___".
  3. Write the recurrence as a formula in that language.
  4. Write the base cases (empty input, 0 capacity, single element).
  5. What is the answer cell? (dp[n], dp[n][m], max over the last row...)
  6. Complexity = number of states × transitions per state.
  7. Optimise space last: can a row be overwritten in place? (Usually yes.)""")

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  climb stairs / house robber .... O(n) time,  O(1) space
  unique paths r x c ............. O(r*c), can be O(min(r,c)) space
  min path sum / triangle ........ O(r*c)
  coin change (min coins) ........ O(amount * coins)
  number of combinations ......... O(amount * coins)
  0/1 knapsack ................... O(n * capacity)
  longest common subsequence ..... O(n * m)
  edit distance .................. O(n * m)
  LIS ............................ O(n^2) naive, O(n log n) with bisect
  DP space can often be reduced ... keep 1 or 2 rows instead of the full table""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `ways_to_climb(n, steps)` -> ways to reach n using any allowed step sizes.
# 2. `house_robber` -> write both the O(n) table and the O(1) space version.
# 3. `longest_palindromic_subsequence(s)` -> LCS(s, reversed(s)).
# 4. `word_break(s, word_dict)` -> can s be segmented into dictionary words?
# 5. `max_product_subarray(nums)` -> track both max and min (negatives flip).
# 6. `longest_increasing_subsequence` -> both versions, with the sequence.
# 7. `partition_equal_subset(nums)` -> can the list be split into two equal-sum
#    halves? (Subset-sum DP — knapsack in disguise.)
# 8. `unique_paths_with_obstacles(grid)` -> count paths around walls.
# 9. `min_edit_distance` -> then modify it to allow only insertions and
#    deletions (that version equals n + m - 2*LCS).
# 10. `longest_common_substring(a, b)` -> contiguous version (the table resets
#     to 0 on a mismatch).
print()
print("🎉 That is the end of the DSA tour! Now do problems/p00_warmup.py.")
