#!/usr/bin/env python3
"""
run_checks.py - Run all code quality checks, report summary at the end.
Does NOT stop on first failure - runs everything, then reports.
"""
import os
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
TARGET_DIRS = ["bot", "core", "sources", "run_checks.py"]


def print_step(num, text):
    print(f"\n{num}. {text}")
    print("-" * 50)


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=False, **kwargs)


def run_flake8():
    print_step(1, "flake8")
    r = run([PYTHON, "-m", "flake8", *TARGET_DIRS])
    if r.returncode != 0:
        print("FAILED: flake8")
        return False
    print("OK: flake8")
    return True


def run_mypy():
    print_step(2, "mypy")
    r = run([
        PYTHON, "-m", "mypy", *TARGET_DIRS,
        "--ignore-missing-imports",
        "--no-error-summary",
    ])
    if r.returncode != 0:
        print("FAILED: mypy")
        return False
    print("OK: mypy")
    return True


def run_pylint():
    print_step(3, "pylint (errors + similarities)")
    r = run([
        PYTHON, "-m", "pylint", *TARGET_DIRS,
        "--disable=all",
        "--enable=E,similarities",
        "--min-similarity-lines=10",
    ])
    if r.returncode != 0:
        print("FAILED: pylint")
        return False
    print("OK: pylint")
    return True


def run_pytest_collect():
    print_step(4, "pytest --collect-only")
    r = run(
        [PYTHON, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "."},
    )
    if r.returncode != 0:
        combined = (r.stderr or "") + (r.stdout or "")
        if "no tests ran" in combined.lower() or "no tests collected" in combined.lower():
            print("SKIP: pytest collect (no tests yet)")
            return True
        print("FAILED: pytest collect")
        print(combined[-500:])
        return False
    count = "?"
    for line in r.stdout.splitlines():
        if "test" in line.lower() and "collected" in line.lower():
            count = line.strip()
            break
    print(f"OK: pytest collect ({count})")
    return True


def main():
    os.chdir(Path(__file__).resolve().parent)

    print("=" * 50)
    print("freelance_search - Code Quality Checks")
    print("=" * 50)

    checks = [
        ("flake8", run_flake8),
        ("mypy", run_mypy),
        ("pylint", run_pylint),
        ("pytest collect", run_pytest_collect),
    ]

    failed = []
    for name, func in checks:
        try:
            if not func():
                failed.append(name)
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            failed.append(name)

    print("\n" + "=" * 50)
    if failed:
        print(f"FAILED ({len(failed)}/{len(checks)}): {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"ALL CHECKS PASSED ({len(checks)}/{len(checks)})")
        sys.exit(0)


if __name__ == "__main__":
    main()
