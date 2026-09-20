#!/usr/bin/env python3
"""
Grade everything: exercises, DSA checkpoints and practice problems.

Usage
-----
    python3 tools/grade.py                 # run every file, show your score
    python3 tools/grade.py --solutions     # prove the reference solutions pass
    python3 tools/grade.py exercises       # only one section (exercises|dsa|problems)
    python3 tools/grade.py --verbose       # show the full output of each file

How it works: each file is run as a subprocess (exactly as you would run it by
hand) and its summary line is parsed. That is why every file ends with a call
to summary() — the output is both for you and for this script.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUMMARY_RE = re.compile(r"(\d+) passed\s+(\d+) failed\s+(\d+) skipped")

SECTIONS = {
    "exercises": sorted((ROOT / "exercises").glob("ex_*.py")),
    "dsa": sorted((ROOT / "dsa").glob("dsa_*.py")),
    "problems": sorted((ROOT / "problems").glob("p*.py")),
}
# with --solutions the problems section uses the standalone reference solutions
SOLUTION_SECTIONS = {
    "problems": sorted((ROOT / "problems" / "solutions").glob("p*.py")),
}
TITLES = {
    "exercises": "📚 Exercises (Python fundamentals)",
    "dsa": "🧠 DSA topics (worked examples — read them, then look for ✅)",
    "problems": "🎯 Practice problems (auto-graded)",
}


def run_file(path, check_solution=False, verbose=False):
    command = [sys.executable, str(path)]
    if check_solution:
        command.append("--solution")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
    output = result.stdout + result.stderr
    if verbose:
        print(output)
    match = SUMMARY_RE.search(output)
    if match:
        passed, failed, skipped = (int(value) for value in match.groups())
    else:
        passed, failed, skipped = 0, 0, 0
    return passed, failed, skipped, output


def main():
    arguments = [argument for argument in sys.argv[1:] if not argument.startswith("-")]
    verbose = "--verbose" in sys.argv
    check_solution = "--solutions" in sys.argv
    sections = arguments or list(SECTIONS)

    if check_solution:
        print("🧪 running the REFERENCE SOLUTIONS (these should all pass)\n")

    totals = [0, 0, 0]
    for section in sections:
        files = SECTIONS.get(section)
        if files is None:
            print(f"unknown section {section!r} (choose from {', '.join(SECTIONS)})")
            continue
        if check_solution and section in SOLUTION_SECTIONS:
            files = SOLUTION_SECTIONS[section]
        print(TITLES[section])
        print("─" * 72)
        for path in files:
            passed, failed, skipped, output = run_file(
                path, check_solution and section not in SOLUTION_SECTIONS, verbose)
            totals[0] += passed
            totals[1] += failed
            totals[2] += skipped
            if failed:
                mark = "❌"
            elif skipped:
                mark = "⏳"
            elif passed:
                mark = "✅"
            else:
                mark = "  "
            relative = path.relative_to(ROOT)
            print(f"  {mark} {str(relative):<42} {passed:>3} passed  {failed:>3} failed  "
                  f"{skipped:>3} skipped")
            if verbose and output and not verbose:
                print(output)
        print()

    passed, failed, skipped = totals
    print("=" * 72)
    print(f"TOTAL: {passed} passed   {failed} failed   {skipped} skipped")
    attempted = passed + failed
    if attempted:
        print(f"Score: {passed / attempted * 100:.1f}% of attempted cases")
    if failed == 0 and skipped == 0 and passed:
        print("🎉 Everything passes. You are ready for the next section.")
    elif check_solution and (failed or skipped):
        print("⚠️  A reference solution has a bug — tell your coach!")
    else:
        print("Keep going: implement the TODO functions and re-run.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
