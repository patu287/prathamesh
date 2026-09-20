"""
PROBLEM p20 · Monotonic stacks & queues               [Hard · stacks, deques]

"The next element that is bigger/smaller" questions are solved in one pass with
a stack that only ever holds items in increasing or decreasing order. Each index
is pushed once and popped once, so the whole scan is O(n).

    for index, value in enumerate(values):
        while stack and values[stack[-1]] < value:   # pop anything smaller
            smaller_index = stack.pop()
            answer[smaller_index] = value
        stack.append(index)

1. `next_greater(nums)` -> for each index, the first bigger value to its right,
   or -1 when there is none.
        next_greater([2, 1, 2, 4, 3]) -> [4, 2, 4, -1, -1]

2. `daily_temperatures(temps)` -> for each day, how many days until a warmer
   day (0 if never).
        daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) -> [1, 1, 4, 2, 1, 1, 0, 0]

3. `max_sliding_window(nums, k)` -> the maximum of every window of size k.
   Use a deque of indices whose values decrease (the front is the maximum).
        max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) -> [3, 3, 5, 5, 6, 7]

4. `evaluate_rpn(tokens)` -> evaluate Reverse Polish Notation, where operators
   come after their operands. Division truncates toward zero.
        evaluate_rpn(["2", "1", "+", "3", "*"]) -> 9    # (2+1)*3

    ▶ run        : python3 problems/p20_monotonic.py
    ▶ solution   : python3 problems/p20_monotonic.py --solution
    ▶ topic      : dsa/dsa_07_stacks_queues.py
    ▶ complexity : O(n) time, O(n) space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


def next_greater(nums):
    raise NotImplementedError


def daily_temperatures(temps):
    raise NotImplementedError


def max_sliding_window(nums, k):
    raise NotImplementedError


def evaluate_rpn(tokens):
    raise NotImplementedError


CASES = [
    ("next greater mixed",  "next_greater([2, 1, 2, 4, 3])",        [4, 2, 4, -1, -1]),
    ("next greater descending", "next_greater([5, 4, 3, 2, 1])",    [-1, -1, -1, -1, -1]),
    ("next greater ascending", "next_greater([1, 2, 3, 4])",        [2, 3, 4, -1]),
    ("next greater single", "next_greater([7])",                    [-1]),
    ("temperatures",        "daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])",
     [1, 1, 4, 2, 1, 1, 0, 0]),
    ("temperatures falling", "daily_temperatures([5, 4, 3])",       [0, 0, 0]),
    ("sliding window k=3",  "max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)",
     [3, 3, 5, 5, 6, 7]),
    ("sliding window k=1",  "max_sliding_window([4, 2, 9], 1)",     [4, 2, 9]),
    ("sliding window k=2",  "max_sliding_window([9, 11, 8, 5, 7, 10], 2)",
     [11, 11, 8, 7, 10]),
    ("rpn add/mul",         "evaluate_rpn(['2', '1', '+', '3', '*'])", 9),
    ("rpn division",        "evaluate_rpn(['4', '13', '5', '/', '+'])", 6),
    ("rpn negatives",       "evaluate_rpn(['10', '6', '9', '3', '+', '-11', '*', '/', '*', '17', '+', '5', '+'])",
     22),
]

SOLUTION = '''
from collections import deque


def next_greater(nums):
    result = [-1] * len(nums)
    stack = []
    for index, value in enumerate(nums):
        while stack and nums[stack[-1]] < value:
            result[stack.pop()] = value
        stack.append(index)
    return result


def daily_temperatures(temps):
    answer = [0] * len(temps)
    stack = []
    for day, temperature in enumerate(temps):
        while stack and temps[stack[-1]] < temperature:
            colder = stack.pop()
            answer[colder] = day - colder
        stack.append(day)
    return answer


def max_sliding_window(nums, k):
    result = []
    window = deque()
    for index, value in enumerate(nums):
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(index)
        if window[0] <= index - k:
            window.popleft()
        if index >= k - 1:
            result.append(nums[window[0]])
    return result


def evaluate_rpn(tokens):
    operations = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b),
    }
    stack = []
    for token in tokens:
        if token in operations:
            right = stack.pop()
            left = stack.pop()
            stack.append(operations[token](left, right))
        else:
            stack.append(int(token))
    return stack.pop()
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p20 · monotonic stacks & queues", CASES, globals())
    summary()
