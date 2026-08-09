---
name: justfile-workflow
description: Use when a project has a Justfile, needs repeatable command recipes, or has multi-step build, test, lint, docs, benchmark, or release workflows.
---

# Justfile Workflow

## Overview

`just` records the commands humans and agents should actually run. Prefer the
project's recipes over raw underlying tools because recipes encode local flags,
paths, and policy.

## Use Existing Recipes First

Before running build, test, lint, format, docs, or benchmark commands:

```bash
just --list
```

Then choose the narrowest recipe that proves the claim.

## Adding A Justfile

Do not add a `Justfile` automatically to every project. Add one when:

- Commands are repeated across agents or contributors.
- A workflow has multiple steps or non-obvious flags.
- Onboarding requires remembering tool-specific incantations.
- Validation should be standardized before commits or PRs.

Keep recipes small and named by outcome: `fmt`, `lint`, `test`, `validate`,
`ci`, `docs-build`, `benchmark`.

## Recipe Rules

- Prefer recipes that call project-native tools.
- Keep generated outputs and caches ignored.
- Make `ci` compose narrower recipes instead of duplicating commands.
- Document required arguments with defaults when practical.

## Common Mistakes

- Bypassing a recipe and missing local flags.
- Creating a large shell program inside a recipe.
- Adding `just` to a project for a single obvious command.

