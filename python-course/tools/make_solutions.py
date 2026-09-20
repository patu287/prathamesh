#!/usr/bin/env python3
"""
Generate problems/solutions/pNN_*.py from the SOLUTION strings embedded in the
problem files, so every problem has a standalone, runnable reference solution.

    python3 tools/make_solutions.py          # (re)write all solution files

Each generated file loads its problem module, execs the reference solution into
it (replacing the stubs), and then runs the problem's own test cases — one
source of truth for the tests.
"""

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROBLEMS = ROOT / "problems"
SOLUTIONS = PROBLEMS / "solutions"

TEMPLATE = '''"""
Reference solution for {relative}  —  {title}

    ▶ run all   : python3 tools/grade.py --solutions problems
    ▶ run this  : python3 {relative_solution}

The problem file and this solution share the same test cases, so if a test ever
disagrees with the written explanation, the explanation wins — fix the test.
"""

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.harness import run_expressions, summary                       # noqa: E402


def load_problem(relative_path):
    """Import a problem file WITHOUT running its main block."""
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)          # __name__ != "__main__":
    return module


problem = load_problem({relative!r})
exec(problem.SOLUTION, problem.__dict__)     # replace the stubs with the solution

if __name__ == "__main__":
    run_expressions({name!r} + " (reference solution)", problem.CASES, problem.__dict__)
    summary()
'''


def title_of(docstring):
    if not docstring:
        return "problem"
    first = docstring.strip().splitlines()[0]
    return first.split("·", 1)[-1].strip() or "problem"


def main():
    SOLUTIONS.mkdir(exist_ok=True)
    written = []
    for path in sorted(PROBLEMS.glob("p*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        docstring = ast.get_docstring(module) or ""
        has_solution = any(
            isinstance(node, ast.Assign)
            and any(getattr(target, "id", "") == "SOLUTION" for target in node.targets)
            for node in module.body
        )
        if not has_solution:
            print(f"skipping {path.name} (no SOLUTION string)")
            continue
        relative = f"problems/{path.name}"
        target = SOLUTIONS / path.name
        target.write_text(
            TEMPLATE.format(
                relative=relative,
                relative_solution=f"problems/solutions/{path.name}",
                title=title_of(docstring),
                name=path.stem,
            ),
            encoding="utf-8",
        )
        written.append(target.name)
    print(f"wrote {len(written)} reference solutions into problems/solutions/")


if __name__ == "__main__":
    main()
