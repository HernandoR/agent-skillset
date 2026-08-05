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
- Ask in whatever language the user is using; write every settled answer down
  in English (see Language).
- Stop when the remaining work can be implemented without guessing.

## Question Shape

```text
Question N: {specific decision}

Recommended answer: {default with reasoning and consequence}
```

## Language

Grilling is a conversation, so **ask** in the user's language — including
Chinese if that is what they are using. The **record** of what was decided is
an artifact, so write it in English: the RFC or ADR entry, the plan, the task
list, the code comment that captures a resolved constraint.

Being asked to grill in Chinese is not permission to write the outcome in
Chinese. If a Chinese rendering of the decision record is wanted, the English
version stays authoritative and the translation is attached to it as a labelled
transcript. See the `english-only-artifacts` skill for the full rule.

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
- Writing the decision record in the language of the discussion instead of
  English.

