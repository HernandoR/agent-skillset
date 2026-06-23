#!/usr/bin/env python3
"""Flag inline path-literal concatenation outside the allow-list.

Stdlib-only. Reports `Path(...) / "literal"` and `<name>_path/_dir/_root /
"literal"` patterns. Lines inside files on the allow-list are skipped.

Usage:
    find_inline_paths.py [--allow PATH ...] ROOT [ROOT ...]

Default allow-list (project-relative substrings):
    configs/path_config.py
    config/path_config.py
    paths.py

Use --allow to extend.

Exit codes:
    0   no violations
    1   violations reported
    2   usage error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ALLOW = (
    "path_config.py",
    "paths.py",
)

# An expression yielding a Path, followed by at least one ` / "literal"`.
# The expression is one of:
#   - `Path(...)` call
#   - any identifier (`mount`, `root`, `cfg.output`, `self.workspace`)
# The rule is: literal directory/file names belong in the path-config module,
# so a single trailing string segment is enough to flag.
PATTERN = re.compile(
    r"""
    (?:
        \bPath\s*\([^)]*\)
      | \b[A-Za-z_][A-Za-z0-9_.]*\b
    )
    \s*/\s*['"][^'"]+['"]
    """,
    re.VERBOSE,
)

# Suppress pure string-format false positives: `f"{x}/literal"` is NOT a
# Path operator. We only flag when the slash separates two operands at the
# Python expression level, which the regex above already requires.

# Lines we never want to flag even outside the allow-list:
SKIP_LINE = re.compile(
    r"""
    (^\s*\#)                     # comment
    | (^\s*['"]{3})              # triple-quoted docstring boundary
    """,
    re.VERBOSE,
)


def is_allowed(path: Path, allow: tuple[str, ...]) -> bool:
    posix = path.as_posix()
    name = path.name
    return any(token in posix or token == name for token in allow)


def scan_file(path: Path) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    for lineno, line in enumerate(text.splitlines(), start=1):
        if SKIP_LINE.match(line):
            continue
        if PATTERN.search(line):
            findings.append((lineno, line.rstrip()))
    return findings


def iter_python_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".py" else []
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag inline path-literal concatenation outside the allow-list."
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="PATH",
        help="Additional allow-list substring (repeatable).",
    )
    parser.add_argument(
        "roots", nargs="+", type=Path, help="Files or directories to scan."
    )
    args = parser.parse_args(argv)

    allow = (*DEFAULT_ALLOW, *args.allow)
    violations = 0

    for root in args.roots:
        if not root.exists():
            print(f"find_inline_paths: {root} does not exist", file=sys.stderr)
            return 2
        for file in iter_python_files(root):
            if is_allowed(file, allow):
                continue
            for lineno, line in scan_file(file):
                print(f"{file}:{lineno}: {line.strip()}")
                violations += 1

    if violations:
        print(
            f"\nfind_inline_paths: {violations} inline path concat(s). "
            "Move the literals into the path-config module.",
            file=sys.stderr,
        )
        return 1
    print("find_inline_paths: no inline path concatenations found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
