"""
Reference solution for problems/p20_monotonic.py  —  Monotonic stacks & queues               [Hard · stacks, deques]

    ▶ run all   : python3 tools/grade.py --solutions problems
    ▶ run this  : python3 problems/solutions/p20_monotonic.py

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


problem = load_problem('problems/p20_monotonic.py')
exec(problem.SOLUTION, problem.__dict__)     # replace the stubs with the solution

if __name__ == "__main__":
    run_expressions('p20_monotonic' + " (reference solution)", problem.CASES, problem.__dict__)
    summary()
