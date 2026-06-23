---
name: context7-docs-first
description: Use when implementing against an external library, framework, SDK, protocol, or public API that is unknown, unstable, undocumented in-repo, or lacks a local example.
---

# Context7 Docs First

## Overview

External APIs drift. Before implementing against an uncertain API, get current
primary documentation without filling the main context with broad docs.

## Required Pattern

Use a subagent for Context7 lookups when:

- The library, SDK, framework, or API is unknown.
- The repo has no local example for the exact API shape.
- The remembered API may have changed.
- You need current options, signatures, configuration, or migration details.

Give the subagent a narrow question and ask for:

- The selected Context7 library ID.
- The exact API facts needed for implementation.
- One concise example when useful.
- Any version assumptions or uncertainty.

Load broad docs into the main context only when exact snippets are needed to
write the change.

## When Not Needed

- Standard library usage.
- Repo-local APIs with clear examples.
- Vendored documentation already present in the repository.
- Mechanical edits that do not depend on external API behavior.

## Prompt Shape

```text
Use Context7 to answer this narrow API question: {question}.
Return the library ID, exact API facts, minimal example, and uncertainty.
Do not implement code.
```

## Common Mistakes

- Guessing current SDK signatures from memory.
- Loading whole documentation pages into the main context.
- Asking a broad research question when a narrow implementation question is
  enough.

