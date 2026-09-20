"""
DSA 08 · Linked lists

A linked list is a chain of nodes. Each node holds a value and a reference to
the next node (and sometimes the previous one). The last node points to `None`.

    head
     ↓
    ┌───┬───┐   ┌───┬───┐   ┌───┬──────┐
    │ 1 │ ●─┼──▶│ 2 │ ●─┼──▶│ 3 │ None │
    └───┴───┘   └───┴───┘   └───┴──────┘

Linked list vs Python list (array)
----------------------------------
| Operation            | Array/list        | Linked list      |
|----------------------|-------------------|------------------|
| access by index i    | O(1)              | O(n) — walk it   |
| insert at front      | O(n) — shift all  | O(1)             |
| delete a known node  | O(n)              | O(1)             |
| find a value         | O(n)              | O(n)             |
| memory               | contiguous, tight | scattered, extra pointer per node |
| cache friendliness   | excellent         | poor             |

So: use a list when you need indexing; use a linked list when you constantly
insert/delete at the ends (queues, LRU caches, adjacency lists).

Interview warning: interviewers LOVE linked lists because they expose whether
you can juggle pointers. You will need to draw boxes and arrows on paper.

The four patterns that cover almost everything
----------------------------------------------
1. **Two pointers (slow/fast / tortoise-hare)** — find the middle, detect a
   cycle. Fast moves 2 steps for every 1 of slow.
2. **Dummy head node** — a fake node in front so that "insert/delete at the
   head" stops being a special case. Removes 80% of your edge-case bugs.
3. **Reverse the links (prev/cur/next three-pointer dance)** — reversing,
   palindrome checking, reordering.
4. **Walk with a lagging pointer** — remove the n-th node from the end.

Python note: this is the one data structure where Python is *harder* to read
than C, because "pointer" is just "attribute". Always draw the picture first.
"""

from dataclasses import dataclass


@dataclass
class Node:
    """A single link in the chain."""
    value: int
    next: "Node | None" = None

    def __repr__(self):
        return f"Node({self.value})"


def build(values):
    """Build a list from a Python list, keeping the order. O(n)."""
    head = None
    for value in reversed(values):        # walk backwards so the order is right
        head = Node(value, head)
    return head


def to_list(head):
    """Collect all values into a Python list. O(n)."""
    values = []
    while head is not None:
        values.append(head.value)
        head = head.next
    return values


def length(head):
    count = 0
    while head:
        count += 1
        head = head.next
    return count


print("=" * 60)
print("1. Building, printing and traversing")
print("=" * 60)
head = build([1, 2, 3, 4])
print("  built      :", to_list(head))
print("  head value :", head.value, "| head.next:", head.next, "| length:", length(head))
print("  walk manually: ", end="")
node = head
while node:
    print(node.value, end=" -> " if node.next else " -> None\n")
    node = node.next

print("=" * 60)
print("2. Insert, delete, search")
print("=" * 60)


def push_front(head, value):
    """O(1) — the linked list's superpower."""
    return Node(value, head)


def append(head, value):
    """O(n) — you must walk to the end. (Keeping a `tail` reference makes it O(1).)"""
    new_node = Node(value)
    if head is None:
        return new_node
    current = head
    while current.next:
        current = current.next
    current.next = new_node
    return head


def insert_after(node, value):
    """O(1) given the node."""
    node.next = Node(value, node.next)
    return node.next


def delete_value(head, value):
    """Delete the first node with this value. Uses a dummy head for clean edges."""
    dummy = Node(0, head)
    previous = dummy
    while previous.next:
        if previous.next.value == value:
            previous.next = previous.next.next      # unlink
            break
        previous = previous.next
    return dummy.next


def find(head, value):
    """O(n) — no way around it."""
    index = 0
    while head:
        if head.value == value:
            return index
        head = head.next
        index += 1
    return -1


head = build([1, 2, 3])
head = push_front(head, 0)
print("  after push_front(0):", to_list(head))
head = append(head, 4)
print("  after append(4)    :", to_list(head))
insert_after(head.next.next, 99)
print("  after insert_after :", to_list(head))
head = delete_value(head, 99)
print("  after delete(99)   :", to_list(head))
print("  find(3) -> index", find(head, 3), "| find(42) ->", find(head, 42))

print("\n" + "=" * 60)
print("3. Reverse a linked list (the three-pointer dance)")
print("=" * 60)


def reverse_iterative(head):
    """O(n) time, O(1) space. Watch prev/current/next at every step.

    before:  1 -> 2 -> 3 -> None
    after :  3 -> 2 -> 1 -> None
    """
    previous = None
    current = head
    while current:
        following = current.next      # 1. remember where we were going
        current.next = previous       # 2. flip the arrow
        previous = current            # 3. advance prev
        current = following           # 4. advance current
    return previous                   # previous is the new head


def reverse_recursive(head):
    """Elegant but O(n) stack space — and RecursionError on very long lists."""
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head             # the next node now points back at us
    head.next = None                  # and we become the tail
    return new_head


chain = build([1, 2, 3, 4, 5])
print("  original :", to_list(chain))
print("  reversed :", to_list(reverse_iterative(chain)))
print("  recursive:", to_list(reverse_recursive(build([1, 2, 3, 4, 5]))))


def reverse_between(head, left, right):
    """Reverse only positions left..right (1-indexed). Dummy head saves the day."""
    if left == right:
        return head
    dummy = Node(0, head)
    previous = dummy
    for _ in range(left - 1):
        previous = previous.next
    current = previous.next
    for _ in range(right - left):
        following = current.next
        current.next = following.next
        following.next = previous.next
        previous.next = following
    return dummy.next


print("  reverse positions 2..4 of [1..6]:",
      to_list(reverse_between(build([1, 2, 3, 4, 5, 6]), 2, 4)))

print("\n" + "=" * 60)
print("4. Fast & slow pointers: middle, cycle, k-th from the end")
print("=" * 60)


def find_middle(head):
    """Slow moves 1, fast moves 2. When fast finishes, slow is at the middle."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


def has_cycle(head):
    """Floyd's tortoise and hare. O(n) time, O(1) space."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:              # they met inside the loop
            return True
    return False


def cycle_start(head):
    """Find WHERE the cycle begins: after meeting, restart one pointer at head."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow
    return None


def nth_from_end(head, n):
    """One pass: keep a gap of n between two pointers."""
    fast = slow = head
    for _ in range(n):
        if fast is None:
            return None
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    return slow


print("  middle of [1..5] :", find_middle(build([1, 2, 3, 4, 5])),
      "| of [1..6]:", find_middle(build([1, 2, 3, 4, 5, 6])))
print("  has_cycle(1->2->3)      :", has_cycle(build([1, 2, 3])))
cyclic = build([1, 2, 3, 4])
cyclic.next.next.next.next = cyclic.next          # 4 -> 2 closes a loop
print("  has_cycle(1->2->3->4->2):", has_cycle(cyclic), "| cycle starts at:", cycle_start(cyclic))
print("  2nd from the end of [1..5]:", nth_from_end(build([1, 2, 3, 4, 5]), 2))

print("\n" + "=" * 60)
print("5. Merging and sorting")
print("=" * 60)


def merge_two_sorted(a, b):
    """Like the merge step of merge sort but on nodes. O(n + m)."""
    dummy = Node(0)
    tail = dummy
    while a and b:
        if a.value <= b.value:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a or b                # hang the remainder
    return dummy.next


print("  merge [1,3,5] and [2,4,6]:",
      to_list(merge_two_sorted(build([1, 3, 5]), build([2, 4, 6]))))
print("  merge [1,2] and []       :", to_list(merge_two_sorted(build([1, 2]), None)))


def merge_sort_list(head):
    """Sort a linked list in O(n log n): split at the middle, sort, merge."""
    if head is None or head.next is None:
        return head
    # split in half
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                  # cut the chain
    return merge_two_sorted(merge_sort_list(head), merge_sort_list(second))


print("  merge_sort_list([3,1,4,2,5]):",
      to_list(merge_sort_list(build([3, 1, 4, 2, 5]))))


def remove_duplicates_sorted(head):
    """Sorted list: skip values equal to the next node."""
    current = head
    while current and current.next:
        if current.value == current.next.value:
            current.next = current.next.next
        else:
            current = current.next
    return head


print("  remove duplicates from [1,1,2,3,3,3,4]:",
      to_list(remove_duplicates_sorted(build([1, 1, 2, 3, 3, 3, 4]))))

print("\n" + "=" * 60)
print("6. Is it a palindrome? (fast/slow + reverse)")
print("=" * 60)


def is_palindrome_list(head):
    """Find the middle, reverse the second half, compare, then restore. O(n)."""
    if head is None or head.next is None:
        return True
    slow = fast = head
    while fast.next and fast.next.next:        # slow ends at the first middle
        slow = slow.next
        fast = fast.next.next
    second_half = reverse_iterative(slow.next)
    first, second = head, second_half
    result = True
    while second:
        if first.value != second.value:
            result = False
            break
        first = first.next
        second = second.next
    slow.next = reverse_iterative(second_half)  # restore the original list
    return result


print("  [1,2,2,1] palindrome:", is_palindrome_list(build([1, 2, 2, 1])))
print("  [1,2,3]   palindrome:", is_palindrome_list(build([1, 2, 3])))

print("\n" + "=" * 60)
print("7. The dummy-head trick, side by side")
print("=" * 60)


def remove_elements_messy(head, target):
    """Without a dummy: three special cases at the head. Easy to get wrong."""
    while head and head.value == target:
        head = head.next
    current = head
    while current and current.next:
        if current.next.value == target:
            current.next = current.next.next
        else:
            current = current.next
    return head


def remove_elements_clean(head, target):
    """With a dummy: one uniform loop, no special cases."""
    dummy = Node(0, head)
    current = dummy
    while current.next:
        if current.next.value == target:
            current.next = current.next.next
        else:
            current = current.next
    return dummy.next


values = [1, 2, 1, 3, 1]
print("  messy :", to_list(remove_elements_messy(build(values), 1)))
print("  clean :", to_list(remove_elements_clean(build(values), 1)))
print("  both agree:", to_list(remove_elements_messy(build(values), 1))
      == to_list(remove_elements_clean(build(values), 1)))

print("\n" + "=" * 60)
print("8. Doubly linked list (when you need to go backwards)")
print("=" * 60)


@dataclass
class DoubleNode:
    value: int
    next: "DoubleNode | None" = None
    previous: "DoubleNode | None" = None


class DoublyLinkedList:
    """Extra pointer per node buys O(1) removal given a node (LRU cache fuel)."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        node = DoubleNode(value, None, self.tail)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1
        return node

    def remove(self, node):
        if node.previous:
            node.previous.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.previous = node.previous
        else:
            self.tail = node.previous
        self.size -= 1

    def __iter__(self):
        current = self.head
        while current:
            yield current.value
            current = current.next

    def backwards(self):
        current = self.tail
        while current:
            yield current.value
            current = current.previous

    def __repr__(self):
        return f"DoublyLinkedList({list(self)})"


dll = DoublyLinkedList()
nodes = [dll.append(value) for value in [10, 20, 30, 40]]
print("  ", dll)
print("  backwards:", list(dll.backwards()))
dll.remove(nodes[1])                  # O(1) because we have the node
print("  after removing node(20):", dll, "| size:", dll.size)

print("\n" + "=" * 60)
print("9. Complexity summary")
print("=" * 60)
print("""  access i-th node ......... O(n)
  search ................... O(n)
  insert/delete at head .... O(1)
  insert/delete after a known node ... O(1)
  insert/delete at tail (with tail ref) O(1)
  reverse .................. O(n) time, O(1) space
  merge two sorted lists ... O(n + m)
  merge sort a list ........ O(n log n) time, O(log n) stack
  cycle detection .......... O(n) time, O(1) space (Floyd)""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `to_list` / `build` from memory — then verify with asserts.
# 2. `delete_nth_from_end(head, n)` -> one pass, two pointers.
# 3. `swap_pairs(head)` -> [1,2,3,4] becomes [2,1,4,3].
# 4. `add_two_numbers(l1, l2)` -> digits stored in reverse order, e.g. (2->4->3)
#    + (5->6->4) = 807 -> (7->0->8). Watch the carry!
# 5. `intersection_point(headA, headB)` -> do the two lists merge? (Two pointers
#    that switch lists when they hit the end.)
# 6. `rotate_right(head, k)` -> rotate the list right by k nodes.
# 7. `partition(head, x)` -> values < x first, then the rest, order preserved.
# 8. `reorder(head)` -> [1,2,3,4,5] becomes [1,5,2,4,3] (middle + reverse + merge).
# 9. Implement an LRU cache class with a dict + doubly linked list (O(1) get/put).
print()
print("Now run: python3 dsa/dsa_09_trees.py")
