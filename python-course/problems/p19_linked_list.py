"""
PROBLEM p19 · Linked lists                              [Hard · pointers]

A linked list is a chain of nodes. The `Node` class is provided for you — your
job is the pointer juggling. Draw boxes and arrows on paper before you code.

    head = Node(1, Node(2, Node(3)))        # 1 -> 2 -> 3 -> None

1. `build_list(values)` -> a chain in the given order; empty -> None.
2. `to_list(head)` -> the values as a Python list (empty -> []).
3. `length(head)` -> how many nodes.
4. `reverse_list(head)` -> the reversed chain (return the NEW head).
        to_list(reverse_list(build_list([1, 2, 3]))) -> [3, 2, 1]
   Do it iteratively with three variables (prev, current, following).
5. `middle_value(head)` -> the value of the middle node; for an even length
   return the value of the FIRST of the two middle nodes.
        middle_value(build_list([1, 2, 3, 4, 5])) -> 3
        middle_value(build_list([1, 2, 3, 4]))    -> 2
   Use the slow/fast pointer trick (slow moves 1, fast moves 2).
6. `has_cycle(head)` -> True when following `next` eventually loops forever.
   Use Floyd's tortoise and hare. The provided helper `make_cycle(values, index)`
   links the last node back to that index.
7. `merge_two_sorted(a, b)` -> one sorted chain from two sorted chains.
8. `nth_from_end(head, n)` -> the VALUE of the n-th node from the end
   (1 = the last node), or None when n is out of range, in ONE pass
   (keep a gap of n between two pointers).

    ▶ run        : python3 problems/p19_linked_list.py
    ▶ solution   : python3 problems/p19_linked_list.py --solution
    ▶ topic      : dsa/dsa_08_linked_lists.py
    ▶ complexity : O(n) time; reverse/merge are O(1) extra space
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


class Node:
    """A single link: a value plus a reference to the next node."""

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

    def __repr__(self):
        return f"Node({self.value})"


def make_cycle(values, index):
    """Provided helper: build a chain and link the last node back to `index`."""
    head = build_list(values)
    if head is None:
        return None
    node = head
    while node.next:
        node = node.next
    target = head
    for _ in range(index):
        target = target.next
    node.next = target
    return head


def value_or_none(node):
    """Provided helper: the value of a node, or None for an empty node."""
    return None if node is None else node.value


def build_list(values):
    raise NotImplementedError


def to_list(head):
    raise NotImplementedError


def length(head):
    raise NotImplementedError


def reverse_list(head):
    raise NotImplementedError


def middle_value(head):
    raise NotImplementedError


def has_cycle(head):
    raise NotImplementedError


def merge_two_sorted(a, b):
    raise NotImplementedError


def nth_from_end(head, n):
    raise NotImplementedError


CASES = [
    ("build and read",       "to_list(build_list([1, 2, 3]))",              [1, 2, 3]),
    ("build empty",          "to_list(build_list([]))",                     []),
    ("length",               "length(build_list([1, 2, 3, 4]))",            4),
    ("length empty",         "length(build_list([]))",                      0),
    ("reverse",              "to_list(reverse_list(build_list([1, 2, 3])))", [3, 2, 1]),
    ("reverse single",       "to_list(reverse_list(build_list([9])))",      [9]),
    ("reverse empty",        "to_list(reverse_list(build_list([])))",       []),
    ("middle odd",           "middle_value(build_list([1, 2, 3, 4, 5]))",   3),
    ("middle even",          "middle_value(build_list([1, 2, 3, 4]))",      2),
    ("middle single",        "middle_value(build_list([7]))",               7),
    ("no cycle",             "has_cycle(build_list([1, 2, 3]))",            False),
    ("has cycle",            "has_cycle(make_cycle([1, 2, 3, 4], 1))",      True),
    ("self cycle",           "has_cycle(make_cycle([1], 0))",               True),
    ("merge sorted",         "to_list(merge_two_sorted(build_list([1, 3, 5]), build_list([2, 4])))",
                             [1, 2, 3, 4, 5]),
    ("merge with empty",     "to_list(merge_two_sorted(build_list([]), build_list([1])))", [1]),
    ("nth from end",         "nth_from_end(build_list([1, 2, 3, 4, 5]), 2)", 4),
    ("nth from end last",    "nth_from_end(build_list([1, 2, 3]), 1)",       3),
    ("nth from end too big", "nth_from_end(build_list([1, 2]), 5)",          None),
]

SOLUTION = '''
def build_list(values):
    head = None
    for value in reversed(values):
        head = Node(value, head)
    return head


def to_list(head):
    values = []
    while head is not None:
        values.append(head.value)
        head = head.next
    return values


def length(head):
    count = 0
    while head is not None:
        count += 1
        head = head.next
    return count


def reverse_list(head):
    previous = None
    current = head
    while current is not None:
        following = current.next
        current.next = previous
        previous = current
        current = following
    return previous


def middle_value(head):
    slow = fast = head
    while fast is not None and fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next
    return slow.value if slow else None


def has_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def merge_two_sorted(a, b):
    dummy = Node(0)
    tail = dummy
    while a is not None and b is not None:
        if a.value <= b.value:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a is not None else b
    return dummy.next


def nth_from_end(head, n):
    fast = slow = head
    for _ in range(n):
        if fast is None:
            return None
        fast = fast.next
    while fast is not None:
        slow = slow.next
        fast = fast.next
    return slow.value
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())
        print("▶ showing the reference solution's results\n")
    run_expressions("p19 · linked lists", CASES, globals())
    summary()
