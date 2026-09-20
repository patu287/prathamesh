"""
EXERCISE 16 · Big-O & performance thinking

    ▶ run        : python3 exercises/ex_16_big_o.py
    ▶ solution   : python3 exercises/ex_16_big_o.py --solution

This one is different: half the answers are NUMBERS you compute (counting how
much work an algorithm does), and half are SHORT STRINGS naming a complexity.
Write complexities in plain lowercase with no spaces: "o(1)", "o(log n)",
"o(n)", "o(n log n)", "o(n^2)", "o(2^n)", "o(n!)".
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def count_operations_single_loop(n):
    """How many times does the body run?  for i in range(n): ..."""
    raise NotImplementedError


def count_operations_nested_loop(n):
    """for i in range(n): for j in range(n): ...  (count the inner-body runs)"""
    raise NotImplementedError


def count_operations_triangle(n):
    """for i in range(n): for j in range(i, n): ...  (inner-body runs)"""
    raise NotImplementedError


def count_halving_steps(n):
    """How many times can you halve n (using // 2) before reaching 0?
    count_halving_steps(8) -> 4  (8 -> 4 -> 2 -> 1 -> 0)
    """
    raise NotImplementedError


def count_operations_linear_pair(n):
    """Two separate loops, each running n times. Total body executions."""
    raise NotImplementedError


def complexity_single_loop():
    """The Big-O of  for x in items: print(x)   -> a string like "o(n)" """
    raise NotImplementedError


def complexity_binary_search():
    """The Big-O of binary search on a sorted list."""
    raise NotImplementedError


def complexity_nested_loops():
    """The Big-O of two nested loops over the same n items."""
    raise NotImplementedError


def complexity_sorting():
    """The Big-O of Python's sorted() on n items."""
    raise NotImplementedError


def complexity_dict_lookup():
    """The Big-O of  value = my_dict[key]  (average case)."""
    raise NotImplementedError


def complexity_dedupe_list():
    """You dedupe a list by checking `if value in result_list` for every value
    (building a plain list). What is the complexity of the whole dedupe?
    """
    raise NotImplementedError


def complexity_dedupe_set():
    """The same dedupe but checking `if value not in seen_set` instead."""
    raise NotImplementedError


def complexity_string_concat():
    """Building a big string inside a loop with `text += piece` (n pieces)."""
    raise NotImplementedError


def complexity_subsets():
    """Generating every subset of n elements."""
    raise NotImplementedError


def operations_at_scale(constant_time_operations, n):
    """Estimate the total operations for O(n^2) work when n grows:
    constant_time_operations * n * n.  operations_at_scale(1, 10) -> 100"""
    raise NotImplementedError


CASES = [
    ("single loop n=10",        "count_operations_single_loop(10)",    10),
    ("single loop n=0",         "count_operations_single_loop(0)",     0),
    ("nested loop n=5",         "count_operations_nested_loop(5)",     25),
    ("nested loop n=100",       "count_operations_nested_loop(100)",   10000),
    ("triangle n=4",            "count_operations_triangle(4)",        10),
    ("triangle n=5",            "count_operations_triangle(5)",        15),
    ("halving steps 8",         "count_halving_steps(8)",              4),
    ("halving steps 1",         "count_halving_steps(1)",              1),
    ("halving steps 1024",      "count_halving_steps(1024)",           11),
    ("two linear loops n=10",   "count_operations_linear_pair(10)",    20),
    ("complexity: single loop", "complexity_single_loop()",            "o(n)"),
    ("complexity: binary search", "complexity_binary_search()",        "o(log n)"),
    ("complexity: nested loops", "complexity_nested_loops()",          "o(n^2)"),
    ("complexity: sorting",     "complexity_sorting()",                "o(n log n)"),
    ("complexity: dict lookup", "complexity_dict_lookup()",            "o(1)"),
    ("complexity: dedupe with a list", "complexity_dedupe_list()",     "o(n^2)"),
    ("complexity: dedupe with a set", "complexity_dedupe_set()",       "o(n)"),
    ("complexity: string +=",   "complexity_string_concat()",          "o(n^2)"),
    ("complexity: subsets",     "complexity_subsets()",                "o(2^n)"),
    ("operations at scale",     "operations_at_scale(3, 1000)",        3000000),
]

SOLUTION = '''
def count_operations_single_loop(n):
    return n


def count_operations_nested_loop(n):
    return n * n


def count_operations_triangle(n):
    return n * (n + 1) // 2


def count_halving_steps(n):
    steps = 0
    while n > 0:
        n //= 2
        steps += 1
    return steps


def count_operations_linear_pair(n):
    return 2 * n


def complexity_single_loop():
    return "o(n)"


def complexity_binary_search():
    return "o(log n)"


def complexity_nested_loops():
    return "o(n^2)"


def complexity_sorting():
    return "o(n log n)"


def complexity_dict_lookup():
    return "o(1)"


def complexity_dedupe_list():
    return "o(n^2)"


def complexity_dedupe_set():
    return "o(n)"


def complexity_string_concat():
    return "o(n^2)"


def complexity_subsets():
    return "o(2^n)"


def operations_at_scale(constant_time_operations, n):
    return constant_time_operations * n * n
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 16 · big-O & performance", CASES, namespace)
    summary()
