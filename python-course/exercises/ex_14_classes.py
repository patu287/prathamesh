"""
EXERCISE 14 · Classes & OOP

    ▶ run        : python3 exercises/ex_14_classes.py
    ▶ solution   : python3 exercises/ex_14_classes.py --solution
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.harness import run_expressions, summary                       # noqa: E402


class Rectangle:
    """A rectangle with a width and a height.

    TODO: implement __init__, area(), perimeter() and __repr__.
    repr(Rectangle(2, 3)) must be exactly "Rectangle(2, 3)".
    """

    def __init__(self, width, height):
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __eq__(self, other):
        """Two rectangles are equal when their areas are equal and both are Rectangles."""
        raise NotImplementedError


class Counter2:
    """A counter that starts at 0 and can go up or down, never below zero.

    TODO: __init__ (store the value), increment(n=1), decrement(n=1),
    value property, and __repr__ -> "Counter2(5)".
    """

    def __init__(self, start=0):
        raise NotImplementedError

    def increment(self, amount=1):
        raise NotImplementedError

    def decrement(self, amount=1):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Stack:
    """A LIFO stack built on a plain list.

    TODO: push(item) (return nothing), pop() (raise IndexError when empty),
    peek(), is_empty(), __len__, __repr__ -> "Stack([1, 2])".
    """

    def __init__(self):
        raise NotImplementedError

    def push(self, item):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def peek(self):
        raise NotImplementedError

    def is_empty(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


def error_name(thunk):
    """Provided helper: report which exception a call raises."""
    try:
        thunk()
    except NotImplementedError:
        raise                                      # keep "not attempted yet" visible
    except Exception as exc:                       # noqa: BLE001
        return type(exc).__name__
    return "none"


CASES = [
    ("rectangle area",        "Rectangle(2, 3).area()",                       6),
    ("rectangle perimeter",   "Rectangle(2, 3).perimeter()",                  10),
    ("rectangle repr",        "repr(Rectangle(2, 3))",                        "Rectangle(2, 3)"),
    ("rectangle equality",    "Rectangle(2, 3) == Rectangle(3, 2)",           True),
    ("rectangle inequality",  "Rectangle(2, 3) == Rectangle(2, 4)",           False),
    ("counter starts at 0",   "Counter2().value",                             0),
    ("counter increment",     "(lambda c: (c.increment(), c.value)[1])(Counter2(5))", 6),
    ("counter value after increments", "(lambda c: (c.increment(3), c.value)[1])(Counter2())", 3),
    ("counter never below zero", "(lambda c: (c.decrement(10), c.value)[1])(Counter2(2))", 0),
    ("counter decrement",     "(lambda c: (c.decrement(2), c.value)[1])(Counter2(5))", 3),
    ("counter repr",          "repr(Counter2(7))",                            "Counter2(7)"),
    ("stack push/peek",       "(lambda s: (s.push(1), s.push(2), s.peek())[2])(Stack())", 2),
    ("stack pop",             "(lambda s: (s.push(1), s.pop())[1])(Stack())", 1),
    ("stack len",             "(lambda s: (s.push(1), s.push(2), len(s))[2])(Stack())", 2),
    ("stack empty",           "Stack().is_empty()",                           True),
    ("stack not empty",       "(lambda s: (s.push(9), s.is_empty())[1])(Stack())", False),
    ("stack pop empty raises", "error_name(lambda: Stack().pop())",           "IndexError"),
    ("stack repr",            "(lambda s: (s.push(1), s.push(2), repr(s))[2])(Stack())", "Stack([1, 2])"),
]

SOLUTION = '''
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def __repr__(self):
        return f"Rectangle({self.width}, {self.height})"

    def __eq__(self, other):
        return isinstance(other, Rectangle) and self.area() == other.area()


class Counter2:
    def __init__(self, start=0):
        self._value = max(0, start)

    def increment(self, amount=1):
        self._value += amount

    def decrement(self, amount=1):
        self._value = max(0, self._value - amount)

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"Counter2({self._value})"


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
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
'''

if __name__ == "__main__":
    if "--solution" in sys.argv:
        exec(SOLUTION, globals())          # overwrite the stubs in place
        print("▶ showing the reference solution's results\n")
    namespace = globals()
    run_expressions("exercise 14 · classes & OOP", CASES, namespace)
    summary()
