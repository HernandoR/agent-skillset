---
name: decision-grilling
description: Use when a plan, feature, design, or implementation direction has unresolved questions, hidden assumptions, or branching decisions that can change the work.
---

# Decision Grilling

## Overview

Resolve design uncertainty before implementation. Ask one question at a time,
walk the decision tree, and provide a recommended answer for each question.

## Rules

- Ask exactly one question at a time.
- Include a recommended answer with the question.
- If the answer can be discovered from the repository, inspect the repository
  instead of asking the user.
- Resolve dependencies in order: a downstream question waits until its upstream
  decision is settled.
- Stop when the remaining work can be implemented without guessing.

## Question Shape

```text
Question N: {specific decision}

Recommended answer: {default with reasoning and consequence}
```

## Exploration Before Asking

Search existing docs, RFCs, tests, type stubs, package metadata, and agent
instructions before asking about:

- Existing conventions.
- Tool choices.
- File layout.
- Test commands.
- Naming patterns.
- Public API constraints.

## Common Mistakes

- Asking bundles of questions that hide dependencies.
- Treating "sounds good" as agreement to unrelated decisions.
- Asking the user to answer things the codebase already states.

