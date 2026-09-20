"""
Tiny test harness used by exercises, DSA files and problems.

Why not pytest? Because this course must run anywhere with zero installs,
including inside the browser playground (Pyodide). This file is ~100 lines
you can read in 5 minutes — and reading it teaches you about exceptions.

Usage
-----
    from tools.harness import run_cases        # after bootstrap (see below)

    run_cases("my_function", [
        ("case name", lambda: my_function(1, 2), 3),   # expected value
        ("raises",    lambda: my_function(""),   ValueError),  # expected exception
    ])

Each case is `(name, thunk, expected)`. `thunk` is a zero-argument callable so
the harness can catch exceptions from it. `expected` may be:
  * a value            -> compared with ==
  * an exception class -> the case passes only if that exception is raised

If the thunk raises NotImplementedError the case is reported as SKIPPED,
which is what happens while you are still working on an exercise.
"""

import sys
import traceback

# ---------------------------------------------------------------------------
# colours (disabled automatically when output is piped to a file)
# ---------------------------------------------------------------------------
_HAS_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
GREEN = "\033[92m" if _HAS_TTY else ""
RED = "\033[91m" if _HAS_TTY else ""
YELLOW = "\033[93m" if _HAS_TTY else ""
DIM = "\033[2m" if _HAS_TTY else ""
RESET = "\033[0m" if _HAS_TTY else ""

PASSED = 0
FAILED = 0
SKIPPED = 0


def _preview(value, limit=90):
    """Short, readable representation of a value for error messages."""
    text = repr(value)
    if len(text) > limit:
        text = text[:limit] + f"... ({len(text)} chars)"
    return text


def run_cases(title, cases, stop_on_first_fail=False):
    """Run every case, print a report, return True if all passed.

    Parameters
    ----------
    title : str
        Name printed above the results (usually the function name).
    cases : list[tuple]
        (name, thunk) or (name, thunk, expected).
    stop_on_first_fail : bool
        Stop at the first wrong answer (useful for long cases).
    """
    global PASSED, FAILED, SKIPPED

    print(f"\n{DIM}── {title} " + "─" * max(0, 50 - len(str(title))) + f"{RESET}")
    ok = True

    for case in cases:
        name, thunk = case[0], case[1]
        expected = case[2] if len(case) > 2 else None
        has_expected = len(case) > 2

        try:
            got = thunk()
        except NotImplementedError:
            SKIPPED += 1
            print(f"  {YELLOW}⏭  {name}{RESET} {DIM}(not attempted yet){RESET}")
            ok = False
            continue
        except Exception as exc:                       # noqa: BLE001 - on purpose
            if has_expected and isinstance(expected, type) and issubclass(expected, BaseException):
                if isinstance(exc, expected):
                    PASSED += 1
                    print(f"  {GREEN}✅ {name}{RESET} {DIM}(raised {type(exc).__name__} as expected){RESET}")
                    continue
                FAILED += 1
                print(f"  {RED}❌ {name}{RESET} expected {expected.__name__}, "
                      f"got {type(exc).__name__}: {exc}")
            else:
                FAILED += 1
                print(f"  {RED}❌ {name}{RESET} raised {type(exc).__name__}: {exc}")
                print(f"     {DIM}{traceback.format_exc(limit=2).splitlines()[-2].strip()}{RESET}")
            ok = False
            if stop_on_first_fail:
                break
            continue

        if not has_expected:
            PASSED += 1
            print(f"  {GREEN}✅ {name}{RESET}")
            continue

        if isinstance(expected, type) and issubclass(expected, BaseException):
            FAILED += 1
            print(f"  {RED}❌ {name}{RESET} expected {expected.__name__} to be raised, "
                  f"but got {_preview(got)}")
            ok = False
        elif got == expected:
            PASSED += 1
            print(f"  {GREEN}✅ {name}{RESET}")
        else:
            FAILED += 1
            print(f"  {RED}❌ {name}{RESET}")
            print(f"     expected: {_preview(expected)}")
            print(f"     got     : {_preview(got)}")
            ok = False

        if not ok and stop_on_first_fail:
            break

    return ok


def run_expressions(title, cases, namespace):
    """Like run_cases, but cases are *expressions as strings*.

    This lets the very same tests be run twice: once against your code (the
    module globals) and once against the reference solution, by evaluating the
    expression in a different namespace.

        [("name", "two_sum([2, 7], 9)", [0, 1])]
    """
    global PASSED, FAILED, SKIPPED

    print(f"\n{DIM}── {title} " + "─" * max(0, 50 - len(str(title))) + f"{RESET}")
    ok = True
    for name, expression, expected in cases:
        try:
            got = eval(expression, namespace)          # noqa: S307 - on purpose
        except NotImplementedError:
            SKIPPED += 1
            print(f"  {YELLOW}⏭  {name}{RESET} {DIM}(not attempted yet){RESET}")
            ok = False
            continue
        except Exception as exc:                       # noqa: BLE001
            FAILED += 1
            print(f"  {RED}❌ {name}{RESET} raised {type(exc).__name__}: {exc}")
            ok = False
            continue
        if got == expected:
            PASSED += 1
            print(f"  {GREEN}✅ {name}{RESET}")
        else:
            FAILED += 1
            ok = False
            print(f"  {RED}❌ {name}{RESET}")
            print(f"     {DIM}expression:{RESET} {expression}")
            print(f"     {DIM}expected  :{RESET} {_preview(expected)}")
            print(f"     {DIM}got       :{RESET} {_preview(got)}")
    return ok


def summary():
    """Print the totals since the last summary() call.

    The counters are reset afterwards so that running several files in ONE
    interpreter (the browser playground does exactly that) still reports one
    file's results at a time.
    """
    global PASSED, FAILED, SKIPPED
    total = PASSED + FAILED
    print(f"\n{'=' * 54}")
    print(f"{GREEN}{PASSED} passed{RESET}   {RED}{FAILED} failed{RESET}   "
          f"{YELLOW}{SKIPPED} skipped{RESET}")
    if total and PASSED == total and SKIPPED == 0:
        print(f"{GREEN}🎉 All tests passed. Move on to the next one!{RESET}")
    elif SKIPPED:
        print(f"{YELLOW}Implement the functions marked TODO, then run this file again.{RESET}")
    else:
        print(f"{RED}Some answers are wrong — read the message above, fix, run again.{RESET}")
    all_passed = FAILED == 0
    PASSED = FAILED = SKIPPED = 0
    return all_passed


def expect_error(title, thunk, error_type, message_contains=None):
    """Assert that `thunk()` raises `error_type` (optionally with a message hint)."""
    try:
        result = thunk()
    except error_type as exc:
        if message_contains and message_contains.lower() not in str(exc).lower():
            print(f"  {RED}❌ {title}{RESET} raised {error_type.__name__} but message "
                  f"{str(exc)!r} does not contain {message_contains!r}")
            return False
        print(f"  {GREEN}✅ {title}{RESET}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  {RED}❌ {title}{RESET} expected {error_type.__name__}, "
              f"got {type(exc).__name__}: {exc}")
        return False
    print(f"  {RED}❌ {title}{RESET} expected {error_type.__name__}, nothing was raised "
          f"(returned {_preview(result)})")
    return False


def show(**values):
    """Pretty-print `name=value` pairs — handy inside lessons.

        show(total=42, name="Prathamesh")
    """
    for key, value in values.items():
        print(f"  {key} = {value!r}")


if __name__ == "__main__":  # self-test
    def double(x):
        return x * 2

    def broken():
        raise NotImplementedError

    def boom():
        raise ValueError("nope")

    run_cases("harness self-test", [
        ("doubles correctly", lambda: double(2), 4),
        ("wrong on purpose", lambda: double(2), 5),
        ("not attempted", lambda: broken(), 0),
        ("raises ValueError", lambda: boom(), ValueError),
        ("plain ok", lambda: double(3), 6),
    ])
    expect_error("expect_error works", lambda: boom(), ValueError, "nope")
    summary()
