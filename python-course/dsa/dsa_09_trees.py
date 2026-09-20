"""
DSA 09 · Trees & binary search trees

A tree is a hierarchy of nodes: one root, each node has children, no cycles.
A **binary tree** gives each node at most two children, `left` and `right`.

            1              depth 0  (root)
          /   \\
         2     3           depth 1
        / \\     \\
       4   5     6         depth 2
                  \\
                   7       depth 3 (a leaf)

Vocabulary: root, leaf, parent/child, subtree, depth (edges from the root),
height (longest path down to a leaf), level (= depth), balanced.

A **binary search tree (BST)** adds the ordering rule:

    everything in the LEFT subtree  <  node <  everything in the RIGHT subtree

That single rule makes search/insert/delete O(height) — O(log n) when balanced,
O(n) in the worst case (a straight line — which is why balanced trees exist).

The traversals (memorise these four)
------------------------------------
    in-order    left, root, right   -> a BST comes out SORTED ✅
    pre-order   root, left, right   -> copy/serialise a tree
    post-order  left, right, root   -> delete a tree, evaluate expressions
    level-order BFS with a queue    -> level-by-level, shortest paths

Every tree problem is one of:
    1. a traversal with a tweak,
    2. recursion that returns a value up the tree (height, sum, is-valid...),
    3. BFS by levels.

Recursion is natural here: "solve for the root using the answers of its two
subtrees". Always ask: what is the base case for an empty tree? (`if node is None`)

Counting facts worth knowing
----------------------------
* a binary tree of height h has at most 2^(h+1) - 1 nodes
* a complete-ish tree with n nodes has height ~log2(n)
* a BST built from SORTED input degenerates to a linked list (O(n) height)
"""

from collections import deque
from dataclasses import dataclass


@dataclass
class TreeNode:
    value: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None

    def __repr__(self):
        return f"TreeNode({self.value})"


def build_tree(values):
    """Build a balanced BST from a list by inserting in order. O(n log n) average."""
    root = None
    for value in values:
        root = insert(root, value)
    return root


def insert(root, value):
    """BST insert: walk left/right by comparison. O(height)."""
    if root is None:
        return TreeNode(value)
    if value < root.value:
        root.left = insert(root.left, value)
    elif value > root.value:
        root.right = insert(root.right, value)
    # equal values are ignored (no duplicates in a simple BST)
    return root


def search(root, value):
    """O(height). Compare each step like binary search, but on nodes."""
    steps = 0
    while root:
        steps += 1
        if value == root.value:
            return root, steps
        root = root.left if value < root.value else root.right
    return None, steps


print("=" * 60)
print("1. Build a BST and see the ordering rule")
print("=" * 60)
root = build_tree([8, 3, 10, 1, 6, 14, 4, 7, 13])
print("  inserted 8,3,10,1,6,14,4,7,13 -> root:", root)


def draw(node, prefix="", is_left=True, label=True):
    """Ugly-but-useful sideways tree printer."""
    if node is None:
        return
    draw(node.right, prefix + ("│   " if is_left else "    "), False)
    print(prefix + ("└── " if is_left else "┌── ") + str(node.value))
    draw(node.left, prefix + ("    " if is_left else "│   "), True)


print("  the tree (rotated 90°):")
draw(root, "  ")

for value in [6, 13, 99]:
    found, steps = search(root, value)
    print(f"  search({value:>2}): {'found' if found else 'not found':<9} in {steps} step(s)")

print("\n" + "=" * 60)
print("2. The four traversals")
print("=" * 60)


def inorder(node):
    """left, root, right — sorted order for a BST."""
    return inorder(node.left) + [node.value] + inorder(node.right) if node else []


def preorder(node):
    """root, left, right — used to copy/serialise."""
    return [node.value] + preorder(node.left) + preorder(node.right) if node else []


def postorder(node):
    """left, right, root — children before parents (safe deletion)."""
    return postorder(node.left) + postorder(node.right) + [node.value] if node else []


def level_order(node):
    """Root, then level by level — BFS with a queue."""
    if node is None:
        return []
    result = []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        result.append(current.value)
        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)
    return result


def levels(node):
    """A list of lists, one per level — the shape most level problems need."""
    if node is None:
        return []
    result = []
    queue = deque([node])
    while queue:
        level = []
        for _ in range(len(queue)):        # exactly the current level
            current = queue.popleft()
            level.append(current.value)
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)
        result.append(level)
    return result


print("  in-order   :", inorder(root), " <- sorted, because it is a BST")
print("  pre-order  :", preorder(root))
print("  post-order :", postorder(root))
print("  level-order:", level_order(root))
print("  levels     :", levels(root))

print("\n" + "=" * 60)
print("3. Recursive properties (the 'return a value up the tree' pattern)")
print("=" * 60)


def height(node):
    """Edges in the longest root-to-leaf path. Empty tree -> -1, single -> 0."""
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def node_count(node):
    if node is None:
        return 0
    return 1 + node_count(node.left) + node_count(node.right)


def sum_tree(node):
    if node is None:
        return 0
    return node.value + sum_tree(node.left) + sum_tree(node.right)


def max_value(node):
    """Largest value in the tree — works on any binary tree, not just a BST.

    ⚠  Do NOT write `max(node.value, max_value(node.left), max_value(node.right))`:
    an empty child returns None and `max()` then compares None with an int.
    Always skip the Nones explicitly.
    """
    if node is None:
        return None
    best = node.value
    for child in (node.left, node.right):
        child_best = max_value(child)
        if child_best is not None and child_best > best:
            best = child_best
    return best


def min_depth(node):
    """Shortest path to a leaf (careful: a missing child is not a leaf)."""
    if node is None:
        return 0
    if node.left is None:
        return 1 + min_depth(node.right)
    if node.right is None:
        return 1 + min_depth(node.left)
    return 1 + min(min_depth(node.left), min_depth(node.right))


print("  height      :", height(root))
print("  node count  :", node_count(root))
print("  sum         :", sum_tree(root))
print("  max value   :", max_value(root))
print("  min depth   :", min_depth(root))
print("  leaf values :", [n.value for n in [root.left.left, root.left.right.right, root.right.right.left]])


def collect_leaves(node):
    if node is None:
        return []
    if node.left is None and node.right is None:
        return [node.value]
    return collect_leaves(node.left) + collect_leaves(node.right)


print("  leaves (collected properly):", collect_leaves(root))


def is_balanced(node):
    """Every node's subtrees differ in height by at most 1. O(n) with one pass."""
    def check(current):
        if current is None:
            return 0, True
        left_height, left_ok = check(current.left)
        right_height, right_ok = check(current.right)
        balanced = left_ok and right_ok and abs(left_height - right_height) <= 1
        return 1 + max(left_height, right_height), balanced

    return check(node)[1]


print("  is_balanced :", is_balanced(root))
degenerate = build_tree([1, 2, 3, 4, 5])          # sorted input -> a straight line
print("  a BST from sorted input is NOT balanced:", is_balanced(degenerate),
      "height:", height(degenerate))

print("\n" + "=" * 60)
print("4. Validating a BST (the classic trap)")
print("=" * 60)


def is_bst_naive(node):
    """WRONG: only checks parent vs immediate children — misses deeper violations."""
    if node is None:
        return True
    if node.left and node.left.value >= node.value:
        return False
    if node.right and node.right.value <= node.value:
        return False
    return is_bst_naive(node.left) and is_bst_naive(node.right)


def is_bst(node, low=float("-inf"), high=float("inf")):
    """Correct: carry the allowed range down the tree. O(n)."""
    if node is None:
        return True
    if not (low < node.value < high):
        return False
    return (is_bst(node.left, low, node.value)
            and is_bst(node.right, node.value, high))


def is_bst_inorder(node):
    """Alternative: in-order traversal must be strictly increasing."""
    values = inorder(node)
    return all(values[i] < values[i + 1] for i in range(len(values) - 1))


tricky = TreeNode(10, TreeNode(5, None, TreeNode(15)), TreeNode(20))
print("  tree: 10 with a 15 hiding under the left subtree")
print("  naive check (wrong) :", is_bst_naive(tricky))
print("  range check (right) :", is_bst(tricky))
print("  in-order check      :", is_bst_inorder(tricky))
print("  the real tree       : naive", is_bst_naive(root), "| range", is_bst(root),
      "| inorder", is_bst_inorder(root))

print("\n" + "=" * 60)
print("5. Delete & find in a BST")
print("=" * 60)


def find_min(node):
    while node and node.left:
        node = node.left
    return node


def delete(root, value):
    """Three cases: leaf, one child, two children (replace with the successor)."""
    if root is None:
        return None
    if value < root.value:
        root.left = delete(root.left, value)
    elif value > root.value:
        root.right = delete(root.right, value)
    else:
        if root.left is None:
            return root.right                  # leaf or only a right child
        if root.right is None:
            return root.left                   # only a left child
        successor = find_min(root.right)       # smallest value in the right subtree
        root.value = successor.value
        root.right = delete(root.right, successor.value)
    return root


print("  in-order before delete:", inorder(root))
print("  delete 10 (two children) ->", inorder(delete(root, 10)))
print("  delete 1  (leaf)         ->", inorder(delete(root, 1)))

print("\n" + "=" * 60)
print("6. Two trees at once (comparing structures)")
print("=" * 60)


def is_same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return (a.value == b.value
            and is_same_tree(a.left, b.left)
            and is_same_tree(a.right, b.right))


def is_symmetric(node):
    """A tree is symmetric if its left mirror equals its right."""
    def mirror(left, right):
        if left is None and right is None:
            return True
        if left is None or right is None:
            return False
        return (left.value == right.value
                and mirror(left.left, right.right)
                and mirror(left.right, right.left))

    return node is None or mirror(node.left, node.right)


def invert(node):
    """Mirror the tree: swap every left and right child."""
    if node is None:
        return None
    node.left, node.right = invert(node.right), invert(node.left)
    return node


a = build_tree([5, 3, 8])
b = build_tree([5, 3, 8])
c = build_tree([5, 3, 9])
print("  same_tree(a, b):", is_same_tree(a, b), "| same_tree(a, c):", is_same_tree(a, c))
symmetric_tree = TreeNode(1, TreeNode(2, TreeNode(3), TreeNode(4)), TreeNode(2, TreeNode(4), TreeNode(3)))
print("  is_symmetric(1(2(3,4),2(4,3))):", is_symmetric(symmetric_tree))
print("  inverted tree in-order:", inorder(invert(build_tree([5, 3, 8]))), "<- descending now")


def lowest_common_ancestor_bst(root, a_value, b_value):
    """In a BST the answer is where the two values split. O(height)."""
    current = root
    while current:
        if a_value < current.value and b_value < current.value:
            current = current.left
        elif a_value > current.value and b_value > current.value:
            current = current.right
        else:
            return current
    return None


big = build_tree([20, 10, 30, 5, 15, 25, 35])
print("  LCA(5, 15) in a BST:", lowest_common_ancestor_bst(big, 5, 15))
print("  LCA(5, 35) in a BST:", lowest_common_ancestor_bst(big, 5, 35))
print("  (general binary trees need the recursive version — challenge 6)")

print("\n" + "=" * 60)
print("7. BFS vs DFS in one picture")
print("=" * 60)
print("""      DFS (recursion): dives to a leaf, then backtracks
         - uses the call stack: O(height) memory
         - great for paths, subtree properties, in-order work
      BFS (queue): visits everything at depth 1, then depth 2, ...
         - uses a queue: O(width) memory (can be huge)
         - great for levels, shortest paths, "nearest" questions""")
print("  DFS pre-order here :", preorder(root))
print("  BFS level-order    :", level_order(root))
print("  widest level       :", max(len(level) for level in levels(root)), "nodes")


def right_side_view(node):
    """The last node of every level — a BFS question in disguise."""
    return [level[-1] for level in levels(node)]


print("  right side view    :", right_side_view(root))


def zigzag_order(node):
    """Level by level, alternating direction. BFS + a flag."""
    if node is None:
        return []
    result = []
    queue = deque([node])
    left_to_right = True
    while queue:
        level = [queue.popleft() for _ in range(len(queue))]
        values = [item.value for item in level]
        result.append(values if left_to_right else values[::-1])
        for item in level:
            if item.left:
                queue.append(item.left)
            if item.right:
                queue.append(item.right)
        left_to_right = not left_to_right
    return result


print("  zigzag order       :", zigzag_order(root))

print("\n" + "=" * 60)
print("8. Complexity summary")
print("=" * 60)
print("""  BST search / insert / delete ... O(height)
      balanced tree (n nodes)  .... O(log n)
      degenerate tree ............ O(n)  ⚠  (sorted input!)
  traversals (any tree) .......... O(n) time
      DFS memory ................. O(height)
      BFS memory ................. O(max width)
  building from n unsorted items . O(n log n) average
  build a BALANCED BST from sorted array ... O(n) (take the middle as the root)
  height of a tree ............... O(n) time (one pass)""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. All four traversals from memory (in-, pre-, post-order recursively and
#    level-order with a queue).
# 2. `tree_diameter(root)` -> the longest path between any two nodes (O(n)).
#    Hint: at each node, left_height + right_height + 2 is a candidate.
# 3. `path_to(root, value)` -> the list of values from the root to that node.
# 4. `build_balanced(sorted_values)` -> a balanced BST from a sorted list by
#    always taking the middle element as the root.
# 5. `kth_smallest_bst(root, k)` -> use in-order traversal and stop early.
# 6. `lowest_common_ancestor(root, a, b)` for a general binary tree (recursive:
#    if both sides return non-null, the current node is the answer).
# 7. `max_path_sum(root)` -> the maximum sum along any path (values may be
#    negative). This is the classic "return a value up the tree" problem.
# 8. `serialize(root)` / `deserialize(text)` -> text back into the same tree.
# 9. `is_subtree(a, b)` -> is b a subtree of a?
# 10. `sum_of_left_leaves(root)` and `count_good_nodes(root)`.
print()
print("Now run: python3 dsa/dsa_10_heaps.py")
