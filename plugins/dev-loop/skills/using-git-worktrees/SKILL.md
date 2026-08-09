---
name: using-git-worktrees
description: Use when starting isolated feature work, parallel development, risky experiments, implementation plans, or any task that should not disturb the current working tree.
---

# Using Git Worktrees

## Overview

Git worktrees isolate branches without switching the current checkout. Use them
when work should proceed independently from the current workspace.

## Directory Selection

Choose a worktree parent in this order:

1. Existing `.worktrees/` in the repo.
2. Existing `worktrees/` in the repo.
3. A repo instruction that names a worktree directory.
4. Ask the user where to create worktrees.

For project-local worktree directories, verify they are ignored before creating
the worktree:

```bash
git check-ignore -q .worktrees
git check-ignore -q worktrees
```

If the chosen local directory is not ignored, add it to `.gitignore`, verify the
change, and commit that setup step before creating worktrees.

## Creation Workflow

1. Name the branch with a short purpose: `feat/<name>`, `fix/<name>`,
   `chore/<name>`, or `refactor/<name>`.
2. Create the worktree:

   ```bash
   git worktree add <path> -b <branch>
   ```

3. Enter the worktree and run project setup. Prefer existing `just` recipes such
   as `just install`; otherwise detect the project toolchain.
4. Run a baseline verification command before editing. Prefer `just ci`,
   `just test`, or the narrow project test command.
5. If the baseline fails, report the failure and ask whether to investigate or
   proceed.

## Tool Detection

- `Justfile`: run `just --list`, then choose the setup/test recipe.
- `pyproject.toml`: use `uv sync` or existing project instructions.
- `Cargo.toml`: use `cargo check` or `cargo test`.
- `package.json`: use the repo's package manager lockfile to choose install and
  test commands.
- `go.mod`: use `go test ./...`.

## Common Mistakes

- Creating a project-local worktree directory that is not ignored.
- Skipping baseline verification and later confusing old failures with new
  regressions.
- Reusing a broad branch for unrelated tasks.

