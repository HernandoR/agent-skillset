#!/usr/bin/env python3
"""Validate a TDD ladder file against the schema.

Stdlib-only.

Walks one or more ladder files (e.g. `.agents/in-progress/<branch>.md`) and
asserts each task has the required steps with the explicit sub-bullets:

- Step 2: `Run:` and `Expected: FAIL — <fragment>`
- Step 4: `Run:` and `Expected: PASS`
- Step 5: `Commit` checkbox present

Exit codes:
    0   clean
    1   schema violations
    2   usage error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TASK_HEADING = re.compile(r"^##\s+Task\s+(\d+)\s*:", re.MULTILINE)
STEP_RE = re.compile(
    r"^- \[[ x]\]\s+\*\*Step\s+(\d+):\s+([^*]+)\*\*\s*$",
    re.MULTILINE,
)
RUN_RE = re.compile(r"^\s+-\s+Run:\s+", re.MULTILINE)
EXPECTED_FAIL_RE = re.compile(
    r"^\s+-\s+Expected:\s+FAIL\s+—\s+\S",
    re.MULTILINE,
)
EXPECTED_PASS_RE = re.compile(r"^\s+-\s+Expected:\s+PASS\s*$", re.MULTILINE)


def split_into_steps(task_body: str) -> list[tuple[int, str, str]]:
    """Yield (step_number, step_label, body_until_next_step) tuples."""
    matches = list(STEP_RE.finditer(task_body))
    out: list[tuple[int, str, str]] = []
    for i, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(task_body)
        out.append(
            (
                int(match.group(1)),
                match.group(2).strip(),
                task_body[body_start:body_end],
            )
        )
    return out


def split_into_tasks(text: str) -> list[tuple[int, str]]:
    """Yield (task_number, body) tuples."""
    matches = list(TASK_HEADING.finditer(text))
    out: list[tuple[int, str]] = []
    for i, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((int(match.group(1)), text[body_start:body_end]))
    return out


def validate_task(task_no: int, body: str, source: Path) -> list[str]:
    errors: list[str] = []
    steps = split_into_steps(body)
    step_numbers = [n for n, _label, _body in steps]
    if step_numbers != [1, 2, 3, 4, 5]:
        return [
            f"{source}: Task {task_no} has steps {step_numbers!r}, "
            "expected [1, 2, 3, 4, 5]"
        ]

    for step_no, step_label, step_body in steps:
        if step_no == 2:
            if not RUN_RE.search(step_body):
                errors.append(
                    f"{source}: Task {task_no} Step 2 missing `Run:` sub-bullet"
                )
            if not EXPECTED_FAIL_RE.search(step_body):
                errors.append(
                    f"{source}: Task {task_no} Step 2 missing "
                    "`Expected: FAIL — <fragment>` sub-bullet"
                )
        elif step_no == 4:
            if not RUN_RE.search(step_body):
                errors.append(
                    f"{source}: Task {task_no} Step 4 missing `Run:` sub-bullet"
                )
            if not EXPECTED_PASS_RE.search(step_body):
                errors.append(
                    f"{source}: Task {task_no} Step 4 missing "
                    "`Expected: PASS` sub-bullet"
                )
        elif step_no == 5:
            if "commit" not in step_label.lower():
                errors.append(
                    f"{source}: Task {task_no} Step 5 label {step_label!r} "
                    "must contain `Commit`"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate TDD ladder files against the schema."
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)

    errors: list[str] = []
    for file in args.files:
        if not file.exists():
            print(f"validate_tdd_plans: {file} does not exist", file=sys.stderr)
            return 2
        text = file.read_text(encoding="utf-8")
        tasks = split_into_tasks(text)
        if not tasks:
            errors.append(f"{file}: no `## Task <n>:` headings found")
            continue
        if len(tasks) > 10:
            errors.append(
                f"{file}: {len(tasks)} tasks exceed soft cap of 10. Split the ladder."
            )
        for task_no, body in tasks:
            errors.extend(validate_task(task_no, body, file))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print("validate_tdd_plans: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
