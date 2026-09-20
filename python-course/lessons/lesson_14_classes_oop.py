"""
LESSON 14 · Classes & OOP

You do not need OOP to solve DSA problems (functions + dicts usually win), but
you *do* need it to read other people's code and to build anything bigger than
a script. And some DSA topics are naturally objects: Linked List, TreeNode,
Stack, Queue, Graph.

# The idea in one line

A **class** bundles data (attributes) with the operations on that data
(methods). An **object** (instance) is one concrete thing built from the class.

    class Dog:
        def __init__(self, name, age):     # constructor: runs on creation
            self.name = name               # attribute
            self.age = age
        def speak(self):                   # method
            return f"{self.name} says woof"
        def birthday(self):
            self.age += 1

    rex = Dog("Rex", 3)      # __init__ runs -> an instance
    rex.speak()              # 'Rex says woof'
    rex.birthday(); rex.age  # 4

`self` is the instance itself, passed automatically as the first argument.
Writing it explicitly is how Python keeps method calls obvious.

# The dunder (magic) methods — make your objects behave like built-ins

    __init__    constructor
    __str__     str(obj) / print(obj)      -> readable for humans
    __repr__    repr(obj) / debugger, REPL -> unambiguous for developers
    __eq__      obj1 == obj2
    __lt__      obj1 < obj2                -> enables sorting
    __hash__    usable in sets / as dict keys
    __len__     len(obj)
    __getitem__ obj[i]                     -> indexing and slicing
    __iter__ / __next__   for x in obj
    __contains__          x in obj
    __add__ / __mul__     obj + obj

Define `__repr__` on almost everything you create — it makes debugging pleasant.

# Class vs instance attributes

    class Counter:
        kind = "counter"          # CLASS attribute: shared by all instances
        def __init__(self):
            self.value = 0        # INSTANCE attribute: one per object

Beware: mutable class attributes are shared, exactly like mutable defaults.

# Inheritance (and when to avoid it)

    class Animal:
        def __init__(self, name):
            self.name = name
        def speak(self):
            raise NotImplementedError
        def describe(self):
            return f"{self.name}: {self.speak()}"

    class Cat(Animal):
        def speak(self):                 # override
            return "meow"

    class Dog(Animal):
        def speak(self):
            return "woof"
        def describe(self):
            return "🐶 " + super().describe()    # extend the parent

Subclass only when the child **is a kind of** the parent ("is-a"). Never for
"has-a" (that is composition: store the other object as an attribute).

# @property — computed attributes with validation

    class Circle:
        def __init__(self, radius):
            self._radius = radius
        @property
        def radius(self): return self._radius
        @radius.setter
        def radius(self, value):
            if value <= 0:
                raise ValueError("radius must be positive")
            self._radius = value
        @property
        def area(self):
            return 3.14159 * self._radius ** 2

`c.area` (no parentheses) computes on the fly; `c.radius = -1` raises.

# @dataclass — the 10-second version of a data-holding class

    from dataclasses import dataclass, field

    @dataclass
    class Point:
        x: int
        y: int
        label: str = "origin"       # defaults work naturally
        tags: list[str] = field(default_factory=list)   # safe mutable default!

    Point(1, 2) == Point(1, 2)      # True — __eq__ is generated for you
    repr(Point(1, 2))               # Point(x=1, y=2, label='origin')

You get `__init__`, `__repr__`, `__eq__` for free. Use dataclasses for records
and plain classes when behaviour dominates.

# Static and class methods

    class Math:
        @staticmethod
        def square(n):          # no self, just a namespaced function
            return n * n
        @classmethod
        def from_string(cls, text):    # alternative constructor
            return cls(int(text))

# DSA-flavoured example: a Stack

    class Stack:
        def __init__(self):
            self._items = []
        def push(self, item): self._items.append(item)
        def pop(self): return self._items.pop()
        def peek(self): return self._items[-1]
        def is_empty(self): return not self._items
        def __len__(self): return len(self._items)
        def __repr__(self): return f"Stack({self._items})"

# SOLID / design in one breath (for later)

* Keep classes small and focused (Single Responsibility).
* Prefer composition over inheritance.
* Depend on behaviour, not on internals (the `_name` convention means "private").
* If a class has no state, you probably wanted a function.
"""

from dataclasses import dataclass, field


print("=" * 60)
print("1. A first class")
print("=" * 60)


class Dog:
    """A dog with a name and an age."""

    species = "Canis familiaris"          # class attribute (shared)

    def __init__(self, name, age):
        self.name = name                   # instance attributes (per object)
        self.age = age

    def speak(self):
        return f"{self.name} says woof"

    def birthday(self):
        self.age += 1
        return self.age

    def __repr__(self):
        return f"Dog(name={self.name!r}, age={self.age})"


rex = Dog("Rex", 3)
luna = Dog("Luna", 5)
print("rex            :", rex)
print("luna           :", luna)
print("rex.speak()    :", rex.speak())
print("rex.birthday() :", rex.birthday(), "-> rex now", rex.age)
print("class attribute:", Dog.species, "| also reachable as rex.species:", rex.species)
print("instances are independent:", rex.age, luna.age)

print("\n" + "=" * 60)
print("2. Dunder methods: make objects behave like built-ins")
print("=" * 60)


class Money:
    """Rupees, with correct addition and readable printing."""

    def __init__(self, amount):
        self.amount = round(float(amount), 2)

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __eq__(self, other):
        return isinstance(other, Money) and self.amount == other.amount

    def __lt__(self, other):
        return self.amount < other.amount

    def __str__(self):
        return f"₹{self.amount:,.2f}"

    def __repr__(self):
        return f"Money({self.amount})"


wallet = Money(250.5)
snacks = Money(80)
print("wallet, snacks       :", wallet, snacks)
print("wallet + snacks      :", wallet + snacks)
print("snacks < wallet      :", snacks < wallet)
print("sorted wallets       :", sorted([wallet, snacks, Money(10)]))
print("repr vs str          :", repr(wallet), "|", str(wallet))
print("sum of a list        :", sum([wallet, snacks], Money(0)), " (needs __add__)")

print("\n" + "=" * 60)
print("3. Inheritance and overriding")
print("=" * 60)


class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("subclasses must implement speak()")

    def describe(self):
        return f"{self.name} says {self.speak()}"


class Cat(Animal):
    def speak(self):
        return "meow"


class Dog2(Animal):
    def __init__(self, name, breed):
        super().__init__(name)             # call the parent constructor
        self.breed = breed

    def speak(self):
        return "woof"

    def describe(self):
        return f"[{self.breed}] " + super().describe()   # extend, don't replace


for animal in [Cat("Whiskers"), Dog2("Rex", "lab")]:
    print("  ", animal.describe())
print("  isinstance checks:", isinstance(Dog2("R", "lab"), Animal), isinstance(Cat("W"), Dog2))

print("\n" + "=" * 60)
print("4. @property")
print("=" * 60)


class Circle:
    def __init__(self, radius):
        self.radius = radius               # goes through the setter below

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError(f"radius must be > 0, got {value}")
        self._radius = value

    @property
    def area(self):
        """Computed every time it is read — no parentheses needed."""
        return round(3.14159265 * self._radius ** 2, 4)

    @property
    def diameter(self):
        return self._radius * 2


circle = Circle(2)
print("  circle.area     =", circle.area, "(a property, not a method call)")
print("  circle.diameter =", circle.diameter)
circle.radius = 5
print("  after radius = 5:", circle.area)
try:
    circle.radius = -1
except ValueError as exc:
    print("  circle.radius = -1 ->", type(exc).__name__, "-", exc)

print("\n" + "=" * 60)
print("5. @dataclass — the fast way to make a record type")
print("=" * 60)


@dataclass
class Student:
    name: str
    marks: list[int]
    level: str = "beginner"
    tags: list[str] = field(default_factory=list)     # safe mutable default

    @property
    def average(self) -> float:
        return sum(self.marks) / len(self.marks) if self.marks else 0.0

    def is_passing(self) -> bool:
        return self.average >= 40


student = Student("Prathamesh", [88, 92, 79])
other = Student("Ravi", [60, 65])
print("  repr         :", student)
print("  average      :", round(student.average, 2))
print("  is_passing() :", student.is_passing(), student.is_passing() and "✅")
print("  equality     :", Student("A", [1]) == Student("A", [1]), "(generated __eq__)")
print("  sorting      :", [s.name for s in sorted([student, other], key=lambda s: s.average, reverse=True)])
print("  defaults     :", other.level, other.tags)
other.tags.append("newbie")
print("  mutable default is per-instance:", other.tags, "| student.tags:", student.tags)

print("\n" + "=" * 60)
print("6. DSA objects: Stack, Queue, ListNode, TreeNode")
print("=" * 60)


class Stack:
    """LIFO: last in, first out."""

    def __init__(self, items=None):
        self._items = list(items) if items else []

    def push(self, item):
        self._items.append(item)
        return self

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"


stack = Stack([1, 2])
stack.push(3).push(4)                      # fluent interface: returns self
print("  ", stack, "| len:", len(stack))
print("  peek:", stack.peek(), "| pop:", stack.pop(), "->", stack)
print("  'in' works via __contains__ fallback (uses __iter__/__getitem__):", 2 in stack._items)

print("\n  Now the two objects every DSA course needs:")


@dataclass
class ListNode:
    val: int
    next: "ListNode | None" = None         # self-referencing type hint

    def __repr__(self):
        return f"ListNode({self.val})"


@dataclass
class TreeNode:
    val: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None

    def __repr__(self):
        return f"TreeNode({self.val})"


def build_list(values):
    """1 -> 2 -> 3 -> None"""
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def traverse(head):
    values = []
    while head:
        values.append(head.val)
        head = head.next
    return values


def inorder(node):
    """Left, root, right — for a BST this comes out sorted."""
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)


print("  linked list:", traverse(build_list([1, 2, 3])))
root = TreeNode(2, TreeNode(1), TreeNode(3))
print("  tree nodes :", root, root.left, root.right, "| inorder:", inorder(root))
print("  (full implementations in dsa_08 and dsa_09)")

print("\n" + "=" * 60)
print("7. Class vs instance attributes (the shared-mutable trap)")
print("=" * 60)


class BadRoom:
    occupants = []                     # shared by EVERY instance 😱

    def add(self, name):
        self.occupants.append(name)


class GoodRoom:
    def __init__(self):
        self.occupants = []            # fresh list per instance ✅

    def add(self, name):
        self.occupants.append(name)


r1, r2 = BadRoom(), BadRoom()
r1.add("Ravi")
print("  BadRoom :", r2.occupants, " <- r2 sees r1's data!")
g1, g2 = GoodRoom(), GoodRoom()
g1.add("Ravi")
print("  GoodRoom:", g2.occupants, " <- properly isolated")

print("\n" + "=" * 60)
print("8. staticmethod / classmethod")
print("=" * 60)


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @staticmethod
    def c_to_f(c):
        """No self, no cls — just a namespaced helper."""
        return c * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, f):
        """Alternative constructor: build an object from other units."""
        return cls((f - 32) * 5 / 9)

    def __repr__(self):
        return f"Temperature({self.celsius:.1f}°C)"


print("  static:", Temperature.c_to_f(0), "F at 0 C")
print("  classmethod:", Temperature.from_fahrenheit(212))

# ---------------------------------------------------------------------------
# 🎯 CHALLENGES
# ---------------------------------------------------------------------------
# 1. `class Rectangle` with width/height, `area` and `perimeter` properties,
#    `__eq__` and `__repr__`.
# 2. `class Playlist` with `add(song)`, `remove(song)`, `__len__`, `__iter__`,
#    and `__contains__` so `"song" in playlist` works.
# 3. `@dataclass Book(title, author, year, tags=[])` and sort a list of books
#    by year, then by title.
# 4. Extend the Stack class with `min_stack()` returning the minimum in O(1)
#    (hint: keep a second stack of running minima).
# 5. `class BankAccount` with `deposit`, `withdraw` (raise a custom exception),
#    and a `history` property.
# 6. `class Matrix` supporting `__add__` and `__matmul__` (or just `multiply`).
# 7. Write `class PriorityQueue` wrapping heapq with push/pop/peek/is_empty.
print()
print("Lesson 14 done — now do exercises/ex_14_classes.py ✅")
