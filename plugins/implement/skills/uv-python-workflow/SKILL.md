---
name: uv-python-workflow
description: Use when setting up, running, validating, or modifying Python projects, Python scripts, virtual environments, dependency files, or Python command workflows.
---

# UV Python Workflow

## Overview

Use `uv` for Python environments and commands when a project has Python code or
Python tooling. Prefer existing project commands first, then add `uv` where new
Python tooling is needed.

## Default Commands

- Run scripts: `uv run python path/to/script.py`
- Run tools: `uv run ruff check .`
- Sync dependencies: `uv sync`
- Add dependencies: `uv add <package>`
- Add development dependencies: `uv add --dev <package>`

## Project Rules

- If the project already has a `pyproject.toml`, use it as the source of truth.
- Keep lockfiles tracked when the project uses them for repeatability.
- Do not introduce a second environment manager without a clear reason.
- Put repeatable Python commands behind `just` when the repo uses a `Justfile`.

## When Adding Python Tooling

1. Add the smallest dependency set that supports the workflow.
2. Expose the command through `just` if it will be repeated.
3. Run the command through `uv run`.
4. Commit dependency metadata and lockfile changes with the tooling slice.

## Common Mistakes

- Running global `python` or `pip` in a uv-managed repo.
- Adding ad hoc shell scripts when `uv run` plus `just` would be clearer.
- Forgetting that generated virtual environments must stay ignored.

