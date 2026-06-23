---
name: git-workflow-and-versioning
description: Use when making code, documentation, tooling, or skill changes that should be committed, branched, reviewed, merged, reverted, or split into versioned steps.
---

# Git Workflow And Versioning

## Overview

Git history is the reviewable record of the work. Keep branches short-lived and
commits small enough to verify and revert independently.

## Default Workflow

1. Check status before editing.
2. Make one logical change.
3. Run the verification command that proves that change.
4. Review the diff.
5. Commit the verified step.
6. Repeat for the next logical change.

## Commit Discipline

- One commit should do one thing.
- Separate behavior, refactors, formatting, docs, and tooling when practical.
- Include the verification command in the commit body when the subject does not
  make the evidence obvious.
- Do not claim performance, correctness, or compatibility without an artifact or
  command output that supports it.

## Branching

Prefer short-lived feature branches from the default branch:

```text
feat/<short-name>
fix/<short-name>
chore/<short-name>
refactor/<short-name>
```

Use worktrees for parallel or risky branches.

## Commit Messages

Use local repository instructions first. When none exist, use:

```text
<type>(<scope>): <subject>
```

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

## Common Mistakes

- Giant commits that mix unrelated changes.
- Formatting a large area in the same commit as a behavior change.
- Committing before reading the staged diff.
- Reverting or overwriting user changes that are unrelated to the task.

