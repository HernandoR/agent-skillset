---
name: verification-before-completion
description: Use before claiming work is complete, fixed, passing, validated, ready to commit, ready to merge, or safe to hand off.
---

# Verification Before Completion

## Overview

Evidence comes before completion claims. If the verification command has not
run in this work session, do not imply the work is complete.

## Gate

Before any success claim:

1. Identify the command or artifact that proves the claim.
2. Run the complete command, not a convenient subset.
3. Read the output and exit code.
4. State the result with the evidence.

If the command fails, report the actual failure and keep working or ask for the
next decision.

## Claim-To-Evidence Map

| Claim | Evidence |
|---|---|
| Tests pass | Test command exits 0 with failures read |
| Lint clean | Lint command exits 0 |
| Build succeeds | Build command exits 0 |
| Skill metadata valid | Skill validator exits 0 |
| Bug fixed | Reproduction or regression test passes |
| Requirements met | Checklist reviewed against implementation |

## Project Commands

Prefer existing `just` recipes when available:

```bash
just validate
just test
just lint
just ci
```

Use the narrowest command that proves the immediate claim, then run broader
checks before final handoff.

## Common Mistakes

- Saying "should pass" after editing.
- Treating a formatter as a build.
- Trusting a subagent's completion report without checking the diff.
- Committing without fresh verification.

