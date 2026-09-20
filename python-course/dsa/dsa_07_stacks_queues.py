"""
DSA 07 · Stacks & queues

Two containers that restrict where you can add and remove. The restriction is
the point: it makes some problems trivial and gives O(1) guarantees.

    Stack (LIFO)                     Queue (FIFO)
    push/pop at the top              enqueue at the back, dequeue at the front
    ┌───┐                            ┌───────────────────┐
    │ 3 │ <- pop() / push()          │ 1 │ 2 │ 3 │ 4   │
    ├───┤                            └───────────────────┘
    │ 2 │                             dequeue()      enqueue()
    ├───┤
    │ 1 │  <- the "top"
    └───┘

In Python
---------
    Stack : a plain list — append() and pop() are both O(1). Perfect.
    Queue : collections.deque — append()/popleft() are both O(1).
            ⚠  Never use list.pop(0) as a dequeue: it is O(n) every time,
               turning a BFS into O(n^2).

When to reach for a stack
-------------------------
* Matching/nesting: brackets, tags, "valid X" problems.
* Undo/redo, browser history, function call stacks.
* Reversing order.
* "The next greater element" family -> monotonic stack (O(n) total).
* DFS (iteratively) -> dsa_11.

When to reach for a queue
-------------------------
* BFS (shortest path in an unweighted graph) -> dsa_11.
* Task scheduling, rate limiting, buffering.
* Sliding-window maximum -> monotonic deque (O(n) total).
"""

from collections import deque
import time

print("=" * 60)
print("1. A stack with a plain list")
print("=" * 60)

stack = []
for value in [1, 2, 3]:
    stack.append(value)                 # push
print("  stack        :", stack)
print("  peek (top)   :", stack[-1], " (O(1) — just look at the last item)")
print("  pop()        :", stack.pop(), "-> stack:", stack)
print("  is_empty     :", not stack, "| stack after 2 pops:", (stack.pop(), stack)[1])

print("\n" + "=" * 60)
print("2. Balanced brackets (the classic stack problem)")
print("=" * 60)

BRACKETS = {")": "(", "]": "[", "}": "{"}


def is_balanced(text):
    """Valid only if every closer matches the most recent opener. O(n)."""
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in BRACKETS:
            if not stack or stack.pop() != BRACKETS[char]:
                return False
        # ignore all other characters
    return not stack                      # leftovers mean unbalanced


for text in ["()", "()[]{}", "(]", "([{}])", "(()", "", "a(b[c]{d})e", ")("]:
    print(f"  {text!r:14} -> {is_balanced(text)}")


def min_removals_to_balance(text):
    """How many characters must be removed to balance the brackets?"""
    stack = []
    removals = 0
    for char in text:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if stack:
                stack.pop()
            else:
                removals += 1             # unmatched closer
    return removals + len(stack)          # unmatched openers


print("  min removals for '(()))(' :", min_removals_to_balance("(()))("))

print("\n" + "=" * 60)
print("3. Min stack — O(1) minimum (a great interview question)")
print("=" * 60)


class MinStack:
    """A stack that also answers "what is the minimum?" in O(1).

    Trick: keep a second stack of the running minima, so the minimum for the
    current state is always on top.
    """

    def __init__(self):
        self._items = []
        self._minima = []

    def push(self, value):
        self._items.append(value)
        current_min = min(value, self._minima[-1] if self._minima else value)
        self._minima.append(current_min)

    def pop(self):
        if not self._items:
            raise IndexError("pop from an empty stack")
        self._minima.pop()
        return self._items.pop()

    def top(self):
        return self._items[-1]

    def get_min(self):
        return self._minima[-1]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"MinStack({self._items}, min={self.get_min() if self._items else None})"


ms = MinStack()
for value in [5, 3, 7, 2]:
    ms.push(value)
    print(f"  push({value}) -> {ms}")
print("  pop() =", ms.pop(), "->", ms)
print("  pop() =", ms.pop(), "->", ms)

print("\n" + "=" * 60)
print("4. Monotonic stack: next greater element in O(n)")
print("=" * 60)


def next_greater_elements(nums):
    """For each element, the first element to its right that is bigger.

    Each index is pushed and popped at most once -> O(n) total, even though
    there is a `while` inside a `for`.
    """
    result = [-1] * len(nums)
    stack = []                          # indices with no bigger element yet
    for index, value in enumerate(nums):
        while stack and nums[stack[-1]] < value:
            smaller_index = stack.pop()
            result[smaller_index] = value         # current value is its answer
        stack.append(index)
    return result                              # leftovers keep -1


for nums in [[2, 1, 2, 4, 3], [5, 4, 3, 2, 1], [1, 2, 3, 4]]:
    print(f"  next greater in {str(nums):<18} -> {next_greater_elements(nums)}")


def daily_temperatures(temps):
    """How many days until a warmer day? Same pattern. O(n)."""
    answer = [0] * len(temps)
    stack = []
    for day, temperature in enumerate(temps):
        while stack and temps[stack[-1]] < temperature:
            colder_day = stack.pop()
            answer[colder_day] = day - colder_day
        stack.append(day)
    return answer


temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
print("  temperatures      :", temperatures)
print("  days until warmer :", daily_temperatures(temperatures))

print("\n" + "=" * 60)
print("5. Queues with deque (and why not a list)")
print("=" * 60)

queue = deque(["first", "second"])
queue.append("third")                 # enqueue at the back
print("  queue          :", queue)
print("  popleft()      :", queue.popleft(), "-> queue:", queue)   # dequeue
queue.appendleft("urgent")            # both ends are O(1)
print("  appendleft()   :", queue)
print("  queue[0] peek  :", queue[0])
print("  rotate(1)      :", (queue.rotate(1), queue)[1])
print("  maxlen=3 keeps the last 3:", deque(range(5), maxlen=3))

print("\n  The O(n) trap (measured):")
SIZE = 60_000
start = time.perf_counter()
work = list(range(SIZE))
while work:
    work.pop(0)                       # O(n) each -> O(n^2)
list_ms = (time.perf_counter() - start) * 1000
start = time.perf_counter()
work = deque(range(SIZE))
while work:
    work.popleft()                    # O(1) each -> O(n)
deque_ms = (time.perf_counter() - start) * 1000
print(f"    list.pop(0) x {SIZE:,}   : {list_ms:8.2f} ms")
print(f"    deque.popleft() x {SIZE:,}: {deque_ms:8.2f} ms   ({list_ms / deque_ms:.0f}x faster)")

print("\n" + "=" * 60)
print("6. Sliding-window maximum with a monotonic deque")
print("=" * 60)


def max_sliding_window(nums, k):
    """Maximum of every window of size k. O(n) — the answer to "why deque?".

    The deque holds INDICES whose values are decreasing. The front is always
    the maximum of the current window.
    """
    result = []
    window = deque()
    for index, value in enumerate(nums):
        while window and nums[window[-1]] <= value:
            window.pop()                      # anything smaller is now useless
        window.append(index)
        if window[0] <= index - k:
            window.popleft()                  # the front fell out of the window
        if index >= k - 1:
            result.append(nums[window[0]])
    return result


series = [1, 3, -1, -3, 5, 3, 6, 7]
for k in [1, 3, 4]:
    print(f"  max sliding window k={k} of {series}:\n     {max_sliding_window(series, k)}")

print("\n" + "=" * 60)
print("7. Stacks in expression evaluation")
print("=" * 60)


def evaluate_rpn(tokens):
    """Reverse Polish Notation: ["2","1","+","3","*"] -> 9. O(n)."""
    stack = []
    operations = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b),       # truncate toward zero
    }
    for token in tokens:
        if token in operations:
            right = stack.pop()             # order matters for - and /
            left = stack.pop()
            stack.append(operations[token](left, right))
        else:
            stack.append(int(token))
    return stack.pop()


print("  ['2','1','+','3','*']       ->", evaluate_rpn(["2", "1", "+", "3", "*"]))
print("  ['4','13','5','/','+']      ->", evaluate_rpn(["4", "13", "5", "/", "+"]))
print("  ['10','6','9','3','+','-11','*','/','*','17','+','5','+'] ->",
      evaluate_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]))

print("\n" + "=" * 60)
print("8. Queue applications: simple scheduler & palindrome check")
print("=" * 60)


def run_scheduler(tasks, quantum=2):
    """Round-robin: each task gets `quantum` units, then goes to the back."""
    queue = deque(tasks)
    timeline = []
    clock = 0
    while queue:
        name, remaining = queue.popleft()
        used = min(quantum, remaining)
        clock += used
        remaining -= used
        timeline.append((clock, name, used, remaining))
        if remaining > 0:
            queue.append((name, remaining))
    return timeline


for moment, name, used, remaining in run_scheduler([("A", 5), ("B", 3), ("C", 1)], 2):
    print(f"  t={moment:<3} ran {name} for {used}  (remaining {remaining})")


def is_palindrome_deque(text):
    """Use both ends of a deque — a nice way to see FIFO + LIFO together."""
    clean = deque(char.lower() for char in text if char.isalnum())
    while len(clean) > 1:
        if clean.popleft() != clean.pop():
            return False
    return True


print("  is_palindrome_deque('A man, a plan, a canal: Panama') =",
      is_palindrome_deque("A man, a plan, a canal: Panama"))

print("\n" + "=" * 60)
print("9. Implementing a queue with two stacks (a classic question)")
print("=" * 60)


class QueueWithStacks:
    """FIFO using two LIFO stacks. Amortised O(1) per operation."""

    def __init__(self):
        self._inbox = []          # newest items arrive here
        self._outbox = []         # reversed order for serving

    def enqueue(self, item):
        self._inbox.append(item)

    def dequeue(self):
        if not self._outbox:
            while self._inbox:            # pour everything over (reverses order)
                self._outbox.append(self._inbox.pop())
        if not self._outbox:
            raise IndexError("dequeue from an empty queue")
        return self._outbox.pop()

    def __len__(self):
        return len(self._inbox) + len(self._outbox)

    def __repr__(self):
        return f"QueueWithStacks(in={self._inbox}, out={self._outbox})"


queue2 = QueueWithStacks()
for value in [1, 2, 3]:
    queue2.enqueue(value)
print("  ", queue2)
print("  dequeue ->", queue2.dequeue(), "|", queue2)
queue2.enqueue(4)
print("  enqueue(4) ->", queue2)
print("  dequeue ->", queue2.dequeue(), "| dequeue ->", queue2.dequeue(), "|", queue2)

print("\n" + "=" * 60)
print("10. Complexity summary")
print("=" * 60)
print("""  list.append / list.pop .......... O(1)      <- perfect stack
  list.pop(0) / insert(0, x) ...... O(n)  ⚠   <- never for queues
  deque.append / popleft .......... O(1)      <- the right queue
  deque.appendleft / pop .......... O(1)
  heapq push/pop .................. O(log n)  <- priority queue (dsa_10)
  monotonic stack pass ............ O(n) total (each index pushed once)
  monotonic deque window .......... O(n) total
  min stack ....................... O(1) per operation, O(n) extra space""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `reverse_first_k(queue, k)` -> reverse the first k items of a queue using
#    only a stack and the queue itself.
# 2. `remove_adjacent_duplicates(text)` -> "abbaca" -> "ca" (stack).
# 3. `simplify_path("/a/./b/../../c/")` -> "/c" (stack of directories).
# 4. `largest_rectangle_histogram(heights)` -> the monotonic-stack classic.
# 5. `infix_to_postfix("a+b*c")` -> "abc*+" (operator stack).
# 6. `stock_span(prices)` -> for each day, how many consecutive days had a price
#    <= today's (monotonic stack).
# 7. `rotate_queue(queue, k)` -> rotate using only queue operations.
# 8. `first_non_repeating_in_stream(chars)` -> at each step, the first character
#    that has appeared exactly once so far (queue + counter).
print()
print("Now run: python3 dsa/dsa_08_linked_lists.py")
