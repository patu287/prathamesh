"""
PROBLEM p13 · Fibonacci & stairs                       [Medium · DP, recursion]

The Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13 ... where every number is the
sum of the two before it.

The recursion `fib(n) = fib(n-1) + fib(n-2)` is beautiful but exponentially
slow. Everything here should run in O(n) (or better) by working upwards.

1. `fib(n)` -> the n-th Fibonacci number, with fib(0) = 0 and fib(1) = 1.
        fib(10) -> 55

2. `fib_list(n)` -> the first n Fibonacci numbers.
        fib_list(6) -> [0, 1, 1, 2, 3, 5]

3. `climb_stairs(n)` -> you climb 1 or 2 steps at a time; how many different
   ways can you reach step n? (Yes, it is Fibonacci shifted.)
        climb_stairs(4) -> 5
   And `climb_stairs_k(n, k)`: the same, but each step may be 1..k long.
        climb_stairs_k(4, 3) -> 7

4. `is_fibonacci(n)` -> True when n is a Fibonacci number.
        is_fibonacci(13) -> True       is_fibonacci(14) -> False

    ▶ run        : python3 problems/p13_fibonacci.py
    ▶ solution   : python3 problems/p13_fibonacci.py --solution
    ▶ topic      : dsa/dsa_12_dp.py, dsa/dsa_06_recursion.py
    ▶ complexity : O(n) time, O(1) space for fib
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def fib(n):
    """fib(0) = 0, fib(1) = 1. n < 0 -> None."""
    raise NotImplementedError


def fib_list(n):
    """The first n Fibonacci numbers.  fib_list(0) -> []"""
    raise NotImplementedError


def climb_stairs(n):
    """Ways to climb n stairs using steps of 1 or 2. climb_stairs(0) -> 1"""
    raise NotImplementedError


def climb_stairs_k(n, k):
    """Ways to climb n stairs using steps of length 1..k."""
    raise NotImplementedError


def is_fibonacci(n):
    """True when n is a Fibonacci number."""
    raise NotImplementedError


CASES = [
    ("fib 0",                "fib(0)",                        0),
    ("fib 1",                "fib(1)",                        1),
    ("fib 10",               "fib(10)",                       55),
    ("fib 30",               "fib(30)",                       832040),
    ("fib negative",         "fib(-1)",                       None),
    ("fib list",             "fib_list(6)",                   [0, 1, 1, 2, 3, 5]),
    ("fib list empty",       "fib_list(0)",                   []),
    ("climb stairs 4",       "climb_stairs(4)",               5),
    ("climb stairs 0",       "climb_stairs(0)",               1),
    ("climb stairs 10",      "climb_stairs(10)",              89),
    ("climb stairs k=3, n=4", "climb_stairs_k(4, 3)",         7),
    ("climb stairs k=1, n=4", "climb_stairs_k(4, 1)",         1),
    ("is fibonacci 13",      "is_fibonacci(13)",              True),
    ("is fibonacci 14",      "is_fibonacci(14)",              False),
    ("is fibonacci 0",       "is_fibonacci(0)",               True),
]

SOLUTION = '''
def fib(n):
    if n < 0:
        return None
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def fib_list(n):
    result = []
    previous, current = 0, 1
    for _ in range(n):
        result.append(previous)
        previous, current = current, previous + current
    return result


def climb_stairs(n):
    if n <= 1:
        return 1
    one_back, two_back = 1, 1
    for _ in range(2, n + 1):
        one_back, two_back = one_back + two_back, one_back
    return one_back


def climb_stairs_k(n, k):
    table = [0] * (n + 1)
    table[0] = 1
    for step in range(1, n + 1):
        for jump in range(1, k + 1):
            if jump <= step:
                table[step] += table[step - jump]
    return table[n]


def is_fibonacci(n):
    a, b = 0, 1
    while a < n:
        a, b = b, a + b
    return a == n
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p13 · fibonacci & stairs", CASES, globals())
    summary()
