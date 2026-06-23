#!/usr/bin/env python3
"""Flag stdlib logging usage in business code.

Stdlib-only. Reports `import logging`, `from logging import ...`, and bare
`print(` calls outside the allow-list. The project's `log_setup.py` is the
canonical allowed site for `import logging`.

Usage:
    find_stdlib_logging.py [--allow PATH ...] [--check-print] ROOT [ROOT ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ALLOW = ("log_setup.py",)

IMPORT_LOGGING = re.compile(r"^\s*(?:import\s+logging|from\s+logging\s+import)\b")
GET_LOGGER = re.compile(r"\blogging\.getLogger\s*\(")
PRINT_CALL = re.compile(r"^(?!\s*\#)\s*print\s*\(")  # excludes commented-out


def is_allowed(path: Path, allow: tuple[str, ...]) -> bool:
    name = path.name
    posix = path.as_posix()
    return any(token == name or token in posix for token in allow)


def scan_file(path: Path, *, check_print: bool) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    for lineno, line in enumerate(text.splitlines(), start=1):
        if IMPORT_LOGGING.search(line) or GET_LOGGER.search(line):
            findings.append((lineno, line.rstrip()))
        elif check_print and PRINT_CALL.search(line):
            findings.append((lineno, line.rstrip()))
    return findings


def iter_python_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".py" else []
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag stdlib logging and (optionally) print() calls."
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="PATH",
        help="Additional allow-list substring or basename (repeatable).",
    )
    parser.add_argument(
        "--check-print",
        action="store_true",
        help="Also flag bare `print(...)` calls in business code.",
    )
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args(argv)

    allow = (*DEFAULT_ALLOW, *args.allow)
    violations = 0

    for root in args.roots:
        if not root.exists():
            print(f"find_stdlib_logging: {root} does not exist", file=sys.stderr)
            return 2
        for file in iter_python_files(root):
            if is_allowed(file, allow):
                continue
            for lineno, line in scan_file(file, check_print=args.check_print):
                print(f"{file}:{lineno}: {line.strip()}")
                violations += 1

    if violations:
        print(
            f"\nfind_stdlib_logging: {violations} violation(s). "
            "Use `from loguru import logger` and route stdlib loggers via "
            "InterceptHandler in log_setup.py.",
            file=sys.stderr,
        )
        return 1
    print("find_stdlib_logging: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
