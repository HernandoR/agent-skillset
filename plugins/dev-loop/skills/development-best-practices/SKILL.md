---
name: development-best-practices
description: Use when starting or organizing development work that may involve design decisions, external APIs, typed public surfaces, Python tooling, repeatable commands, verification, or commits.
---

# Development Best Practices

## Overview

This is the router for the repository's development workflow skills. Keep the
main context small by loading the focused skill that matches the immediate
problem.

## Baseline Checklist

- Resolve design uncertainty before editing behavior.
- Draft an RFC for proposals that need discussion; create an ADR once a
  decision is settled.
- Use Context7 through a subagent when an external API is unknown or lacks a
  local example.
- Treat public interfaces as typed contracts.
- Prefer `uv` for Python projects and scripts.
- Prefer existing `just` recipes for repeatable workflows.
- Verify each logical step before committing it.
- Commit small, reviewed increments instead of batching unrelated work.

## Focused Skills

- `adr-driven-development`: use to propose a design (RFC phase) or record a settled decision (ADR phase).
- `context7-docs-first`: use before implementing against unknown external APIs.
- `typed-interfaces`: use when editing public Python, TypeScript, Rust, or Go
  interfaces.
- `uv-python-workflow`: use when adding or running Python tooling.
- `justfile-workflow`: use when a project has or needs repeatable commands.
- `decision-grilling`: use when open questions can change the implementation.
- `using-git-worktrees`: use before isolated feature work or parallel branches.
- `git-workflow-and-versioning`: use for code changes, commits, and branches.
- `verification-before-completion`: use before claiming completion or committing.
- `finishing-a-development-branch`: use after verified implementation work.

## Common Mistakes

- Loading this umbrella skill and skipping the focused skill.
- Treating "best practice" as vague advice instead of concrete gates.
- Committing work without naming the verification that supports the commit.

