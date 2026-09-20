"""
DSA 11 · Graphs

A graph is a set of nodes (vertices) connected by edges. Trees are special
graphs; graphs are the general case — and most "real world" problems are
graphs: maps, social networks, dependencies, puzzles, state machines.

Vocabulary
----------
* **directed** (edges have a direction, like a Twitter follow) vs **undirected**
* **weighted** (edges carry a cost, like road distances) vs unweighted
* **degree**: how many neighbours a node has
* **path**: a sequence of connected nodes; **cycle**: a path back to the start
* **connected component**: a group of nodes you can reach from each other
* **DAG**: directed, no cycles (task dependencies, build systems)
* **adjacency list** (usual choice) vs **adjacency matrix** (O(1) edge lookup,
  O(V²) memory)

Representation in Python
------------------------
    graph = {
        "A": ["B", "C"],
        "B": ["A"],
        "C": ["A"],
    }

    # weighted:  graph = {"A": [("B", 5), ("C", 2)], ...}
    # grid as a graph: neighbours are up/down/left/right (dsa_06 maze)

Traversal
---------
**BFS** — a queue, level by level. Finds the shortest path in an UNWEIGHTED
graph (fewest edges). Memory O(width).

**DFS** — recursion or an explicit stack. Explores one branch fully, then
backtracks. Great for cycles, components, topological order, paths. Memory
O(depth).

⚠  Always mark nodes as visited when you ADD them to the queue/stack, not when
you pop them, or you will push the same node many times.

Complexity
----------
    adjacency list: O(V + E) time to traverse, O(V + E) space
    adjacency matrix: O(V²) time and space

Choosing an algorithm
---------------------
    "fewest steps / shortest path, unweighted"  -> BFS
    "is there a path / count components"        -> DFS or BFS
    "does it have a cycle"                      -> DFS with colours, or union-find
    "order tasks with dependencies"             -> DFS post-order (topological)
    "shortest path with weights"                -> Dijkstra (heap-based BFS)
    "grid with walls, steps to exit"            -> BFS over cells
"""

from collections import deque, defaultdict
import heapq

print("=" * 60)
print("1. Building a graph (adjacency list)")
print("=" * 60)


def build_undirected(edges):
    """Each edge appears in both directions."""
    graph = defaultdict(list)
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    return dict(graph)


def build_directed(edges):
    graph = defaultdict(list)
    for source, target in edges:
        graph[source].append(target)
    return dict(graph)


friendships = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("F", "G")]
undirected = build_undirected(friendships)
print("  undirected graph:")
for node in sorted(undirected):
    print(f"    {node} -> {sorted(undirected[node])}")

follows = [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")]
directed = build_directed(follows)
print("  directed graph:", {key: sorted(value) for key, value in sorted(directed.items())})


def build_matrix(nodes, edges):
    """Adjacency matrix: O(1) edge check, O(V^2) memory."""
    index = {node: i for i, node in enumerate(nodes)}
    matrix = [[0] * len(nodes) for _ in nodes]
    for a, b in edges:
        matrix[index[a]][index[b]] = 1
        matrix[index[b]][index[a]] = 1
    return matrix, index


matrix, index = build_matrix(["A", "B", "C", "D"], [("A", "B"), ("A", "C"), ("B", "D")])
print("  adjacency matrix:", matrix)
print("  edge A-C?", matrix[index["A"]][index["C"]] == 1, "| edge C-D?",
      matrix[index["C"]][index["D"]] == 1)

print("\n" + "=" * 60)
print("2. BFS: shortest path in an unweighted graph")
print("=" * 60)


def bfs_order(graph, start):
    """Visit everything reachable, closest first."""
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, ()):
            if neighbour not in visited:
                visited.add(neighbour)         # mark when ENQUEUING
                queue.append(neighbour)
    return order


print("  BFS from 'A':", bfs_order(undirected, "A"))


def bfs_shortest_path(graph, start, goal):
    """Fewest edges from start to goal. BFS is optimal for unweighted graphs."""
    if start == goal:
        return [start]
    visited = {start}
    queue = deque([[start]])                    # store the path itself
    while queue:
        path = queue.popleft()
        for neighbour in graph.get(path[-1], ()):
            if neighbour == goal:
                return path + [neighbour]
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(path + [neighbour])
    return None


print("  path A->E:", bfs_shortest_path(undirected, "A", "E"))
print("  path A->G:", bfs_shortest_path(undirected, "A", "G"), "(different component)")
print("  hops A->E:", len(bfs_shortest_path(undirected, "A", "E")) - 1)


def bfs_distances(graph, start):
    """Distance (in edges) from start to every reachable node."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, ()):
            if neighbour not in distances:
                distances[neighbour] = distances[node] + 1
                queue.append(neighbour)
    return distances


print("  distances from A:", dict(sorted(bfs_distances(undirected, "A").items())))

print("\n" + "=" * 60)
print("3. DFS: recursive and iterative")
print("=" * 60)


def dfs_recursive(graph, node, visited=None, order=None):
    """Visit deep first, then backtrack. Watch the order vs BFS."""
    if visited is None:
        visited, order = set(), []
    visited.add(node)
    order.append(node)
    for neighbour in graph.get(node, ()):
        if neighbour not in visited:
            dfs_recursive(graph, neighbour, visited, order)
    return order


def dfs_iterative(graph, start):
    """An explicit stack instead of the call stack — no RecursionError."""
    visited = {start}
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        order.append(node)
        for neighbour in reversed(graph.get(node, ())):     # reversed for readability
            if neighbour not in visited:
                visited.add(neighbour)
                stack.append(neighbour)
    return order


print("  DFS recursive:", dfs_recursive(undirected, "A"))
print("  DFS iterative:", dfs_iterative(undirected, "A"))
print("  BFS order    :", bfs_order(undirected, "A"), " <- compare the shapes")

print("\n" + "=" * 60)
print("4. Connected components")
print("=" * 60)


def count_components(graph):
    """How many separate groups are there? One traversal per component."""
    seen = set()
    components = []
    for node in graph:
        if node in seen:
            continue
        component = []
        queue = deque([node])
        seen.add(node)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbour in graph.get(current, ()):
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        components.append(sorted(component))
    return components


components = count_components(undirected)
print("  components:", components)
print("  count     :", len(components))
print("  are A and G connected?", "G" in bfs_distances(undirected, "A"))


def has_path(graph, start, goal):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            return True
        for neighbour in graph.get(node, ()):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return False


print("  has_path(A, G):", has_path(undirected, "A", "G"))
print("  has_path(A, E):", has_path(undirected, "A", "E"))

print("\n" + "=" * 60)
print("5. Cycle detection")
print("=" * 60)


def has_cycle_undirected(graph):
    """DFS with the parent remembered: an already-seen non-parent = a cycle."""
    visited = set()

    def explore(node, parent):
        visited.add(node)
        for neighbour in graph.get(node, ()):
            if neighbour not in visited:
                if explore(neighbour, node):
                    return True
            elif neighbour != parent:
                return True
        return False

    return any(node not in visited and explore(node, None) for node in graph)


def has_cycle_directed(graph):
    """Three colours: white (unseen), grey (in the current path), black (done)."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = defaultdict(int)

    def explore(node):
        colour[node] = GREY
        for neighbour in graph.get(node, ()):
            if colour[neighbour] == GREY:      # back edge -> cycle
                return True
            if colour[neighbour] == WHITE and explore(neighbour):
                return True
        colour[node] = BLACK
        return False

    return any(colour[node] == WHITE and explore(node) for node in graph)


print("  undirected friendships cycle?", has_cycle_undirected(undirected))
print("  undirected tree (A-B-C) cycle?", has_cycle_undirected(build_undirected([("A", "B"), ("B", "C")])))
print("  directed follows cycle?     ", has_cycle_directed(directed))
print("  directed A->B->C, C->A cycle?", has_cycle_directed(build_directed([("A", "B"), ("B", "C"), ("C", "A")])))

print("\n" + "=" * 60)
print("6. Topological sort (dependency order on a DAG)")
print("=" * 60)


def topological_sort_dfs(graph):
    """Post-order DFS, reversed. Dependencies must appear before dependents."""
    visited = set()
    order = []

    def explore(node):
        visited.add(node)
        for neighbour in graph.get(node, ()):
            if neighbour not in visited:
                explore(neighbour)
        order.append(node)                  # finished -> append at the end

    for node in graph:
        if node not in visited:
            explore(node)
    return order[::-1]


def topological_sort_kahn(graph):
    """Kahn's algorithm: repeatedly take a node with no incoming edges (BFS)."""
    indegree = defaultdict(int)
    nodes = set(graph)
    for node in graph:
        for neighbour in graph[node]:
            indegree[neighbour] += 1
            nodes.add(neighbour)
    queue = deque(node for node in nodes if indegree[node] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, ()):
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)
    return order if len(order) == len(nodes) else None      # None means a cycle


courses = {
    "intro": ["algorithms"],
    "algorithms": ["data structures"],
    "data structures": ["graphs"],
    "graphs": [],
    "python basics": ["algorithms"],
}
print("  course dependencies:", {key: value for key, value in sorted(courses.items())})
print("  DFS version ->", topological_sort_dfs(courses))
print("  Kahn version->", topological_sort_kahn(courses))
cyclic_courses = {"a": ["b"], "b": ["c"], "c": ["a"]}
print("  with a cycle Kahn returns:", topological_sort_kahn(cyclic_courses), "(impossible)")

print("\n" + "=" * 60)
print("7. Weighted graphs: Dijkstra's shortest path")
print("=" * 60)


def dijkstra(graph, start):
    """Cheapest distance to every node. Heap-based BFS: O((V + E) log V).

    The heap always expands the cheapest unfinished node, which is why it works
    for non-negative weights and why it needs a heap at all.
    """
    distances = {start: 0}
    heap = [(0, start)]
    previous = {}
    while heap:
        cost, node = heapq.heappop(heap)
        if cost > distances.get(node, float("inf")):
            continue                                  # stale entry, skip
        for neighbour, weight in graph.get(node, ()):
            new_cost = cost + weight
            if new_cost < distances.get(neighbour, float("inf")):
                distances[neighbour] = new_cost
                previous[neighbour] = node
                heapq.heappush(heap, (new_cost, neighbour))
    return distances, previous


def reconstruct(previous, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(previous[path[-1]])
    return path[::-1]


roads = {
    "Pune": [("Mumbai", 150), ("Nashik", 210), ("Hyderabad", 560)],
    "Mumbai": [("Pune", 150), ("Surat", 280)],
    "Nashik": [("Pune", 210), ("Surat", 250)],
    "Surat": [("Mumbai", 280), ("Nashik", 250), ("Delhi", 1200)],
    "Hyderabad": [("Pune", 560), ("Delhi", 1500)],
    "Delhi": [("Surat", 1200), ("Hyderabad", 1500)],
}
distances, previous = dijkstra(roads, "Pune")
print("  cheapest distance from Pune:")
for city in sorted(distances):
    print(f"    {city:<10} {distances[city]:>5} km")
print("  route to Delhi:", " -> ".join(reconstruct(previous, "Pune", "Delhi")),
      f"({distances['Delhi']} km)")

print("\n" + "=" * 60)
print("8. BFS on a grid (the most common interview shape)")
print("=" * 60)

grid = [
    [0, 0, 0, 0, 1],
    [1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 1, 0],
]

for row in grid:
    print("   ", " ".join("." if cell == 0 else "#" for cell in row))


def shortest_path_grid(grid, start, goal):
    """BFS over 4-directional moves. Returns the number of steps or -1."""
    rows, columns = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return -1
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        (row, column), steps = queue.popleft()
        if (row, column) == goal:
            return steps
        for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            new_row, new_column = row + delta_row, column + delta_column
            if (0 <= new_row < rows and 0 <= new_column < columns
                    and grid[new_row][new_column] == 0
                    and (new_row, new_column) not in visited):
                visited.add((new_row, new_column))
                queue.append(((new_row, new_column), steps + 1))
    return -1


print("  shortest path (0,0) -> (4,4):", shortest_path_grid(grid, (0, 0), (4, 4)), "steps")
print("  shortest path (0,0) -> (1,0):", shortest_path_grid(grid, (0, 0), (1, 0)), "(wall)")


def count_islands(grid):
    """Number of connected groups of 1s — DFS flood fill, in place."""
    rows, columns = len(grid), len(grid[0])
    grid = [row[:] for row in grid]                  # do not mutate the caller's data

    def flood(row, column):
        if not (0 <= row < rows and 0 <= column < columns) or grid[row][column] != 1:
            return
        grid[row][column] = 0                        # mark visited
        flood(row + 1, column)
        flood(row - 1, column)
        flood(row, column + 1)
        flood(row, column - 1)

    islands = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == 1:
                islands += 1
                flood(row, column)
    return islands


print("  islands in the grid above:", count_islands(grid))
print("  islands in [[1,1,0],[0,1,0],[0,0,1]]:",
      count_islands([[1, 1, 0], [0, 1, 0], [0, 0, 1]]))

print("\n" + "=" * 60)
print("9. Union-Find (disjoint set) — the other way to merge components")
print("=" * 60)


class UnionFind:
    """Near-O(1) union and find, with path compression + union by size."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n                            # number of components

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]    # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        self.count -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)


uf = UnionFind(7)
for a, b in [(0, 1), (1, 2), (3, 4), (5, 6)]:
    uf.union(a, b)
print("  components after unions:", uf.count)
print("  0 and 2 connected:", uf.connected(0, 2), "| 0 and 3 connected:", uf.connected(0, 3))
uf.union(2, 3)
print("  after union(2,3) -> components:", uf.count, "| 0 and 4:", uf.connected(0, 4))


def count_provinces(matrix):
    """LeetCode-style problem directly solved with union-find."""
    n = len(matrix)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] == 1:
                uf.union(i, j)
    return uf.count


print("  provinces in [[1,1,0],[1,1,0],[0,0,1]]:",
      count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]))

print("\n" + "=" * 60)
print("10. Complexity summary & algorithm picker")
print("=" * 60)
print("""  BFS ...................... O(V + E) time, O(V) space (queue)
  DFS ...................... O(V + E) time, O(V) space (stack/recursion)
  topological sort ......... O(V + E)
  Dijkstra (binary heap) ... O((V + E) log V)
  Bellman-Ford ............. O(V * E)  (handles negative weights)
  Floyd-Warshall ........... O(V^3)    (all-pairs)
  union-find ............... ~O(1) per op with compression
  grid BFS ................. O(rows * cols)

  Pick:
    unweighted shortest path ......... BFS
    weighted shortest path ........... Dijkstra
    dependencies / ordering .......... topological sort
    grouping / merging ................ union-find
    "count connected things" ......... BFS, DFS or union-find
    negative weights .................. Bellman-Ford
    small V, all-pairs distances ...... Floyd-Warshall""")

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `bfs_shortest_path` — rewrite from memory, then use it to find the shortest
#    word ladder from "hit" to "cog" using a word list.
# 2. `count_components` — do it with DFS instead of BFS and confirm the same
#    number of components.
# 3. `is_bipartite(graph)` -> can you 2-colour it? (BFS with colours.)
# 4. `clone_graph(graph)` -> deep-copy an adjacency structure with a dict of
#    old -> new nodes.
# 5. `rotting_oranges(grid)` -> minutes until every fresh orange rots
#    (multi-source BFS: start from ALL rotten oranges at once).
# 6. `word_ladder(begin, end, word_list)` -> shortest transformation length.
# 7. `course_schedule(num_courses, prerequisites)` -> can all courses be
#    completed? (Cycle detection / Kahn.)
# 8. `shortest_path_with_teleport(grid, k)` -> BFS with extra state (the number
#    of teleports used) — this is "BFS on a state graph", the next level up.
# 9. `network_delay_time(times, n, k)` -> Dijkstra on a directed weighted graph.
print()
print("Now run: python3 dsa/dsa_12_dp.py")
