---
name: tdd-checkbox-plans
description: Use when implementing an accepted ADR through a sequence of red-test-then-implement steps, when a feature must be split into verifiable tasks with explicit failure-fragment prediction, or when previous implementations have skipped the red-test step under deadline pressure.
---

# TDD Checkbox Plans (Advisory)

## Overview

Implement an accepted ADR via a strict per-task ladder: write red test → run
to verify it fails with a *predicted* error fragment → minimal implementation
→ run to verify it passes → commit. The structure forces TDD adoption — you
cannot skip the red-test step without an obvious unchecked checkbox.

The ladder is **external memory** (session scratch, not a tracked plan file).
The project taxonomy is RFC (drafts) / ADR (decisions) / external memory
(ephemeral execution state). When implementation completes, verification
records fold into the ADR's "Verification" section.

This skill is **advisory**, not mandatory. See "Carve-Outs".

## When To Use

- An accepted ADR with non-trivial behavioural changes.
- A bug fix where a regression test should land before the fix.
- Any feature where the cost of writing the red test up front is < the cost
  of debugging a silent skip later.

## Carve-Outs

The ladder is **opt-out per ADR**. Acceptable reasons (recorded in the ADR's
Verification section):

- `trivially-small` — single-line change, mechanical rename, doc edit.
- `shared-state-test` — the test would interfere with a live database, queue,
  or external service; instrument differently.
- `pure-refactor` — no behaviour change; existing tests are the safety net.
- `spike` — exploratory work intentionally not yet committed to a shape.

The skill prompts once per ADR with a verbatim confirmation:

> "Apply the TDD ladder to this ADR's implementation? Recommended: yes.
> Opt-outs (record reason in the ADR's Verification section):
> trivially-small, shared-state-test, pure-refactor, spike."

Within a session, the answer is sticky per ADR.

## Ladder Shape

[references/task-template.md](references/task-template.md) is the canonical
shape. Each task has five steps:

1. Write the red test.
2. Run the test, **verify it fails** with a predicted failure fragment.
   Required sub-bullets:
   - `Run: <command>`
   - `Expected: FAIL — <substring of the failure message>`
3. Minimal implementation.
4. Run the test, **verify it passes**.
   Required sub-bullets:
   - `Run: <command>`
   - `Expected: PASS`
5. Commit (`git commit -m "<type>(<scope>): <subject>"`).

The Step-2 explicit `Run:` and `Expected:` sub-bullets are mandatory. Prose
form ("the test should fail") lets the failure-fragment prediction degrade
into vagueness; the explicit form forces the author to write the substring
they expect to see.

## Soft Cap: ≤ 10 Tasks

A ladder over 10 tasks is the signal to split — not a block. The cap is on
the ladder, not the ADR. An ADR with 25 acceptance criteria is fine; its
ladder splits at ~10 into multiple execution rounds rolling up to the same
ADR.

## Executor Choice

| Ladder | ADR risk | Default executor |
|---|---|---|
| ≤ 5 tasks | low | main loop, no subagents |
| ≤ 5 tasks | high | main loop + `executing-plans` checkpoints |
| 6-10 tasks | low | `subagent-driven-development` (tidy main loop) |
| 6-10 tasks | high | `subagent-driven-development` + `executing-plans` checkpoints |

`subagent-driven-development` keeps the main loop tidy; tidiness pressure
scales **with** ladder length. `executing-plans` is orthogonal — stakes-based,
not length-based. "High-risk" = the ADR's `## Risks` section names
destructive, hard-to-reverse, or breaking-change operations.

## Recovery From Lost External Memory

The ladder lives in session scratch. If the session is killed, recover from:

1. The originating RFC and ADR.
2. Repository state — tests on disk, new symbols, `git log` on the feature
   branch (each completed Step-5 commit is a checkpoint).
3. Re-derive the task template from the ADR's acceptance criteria.

The ADR's Verification section is the durable handle. See
[references/recovery.md](references/recovery.md).

## Red Flags — STOP And Restart

- Implementation written before the red test.
- "I'll add the test after — it'll be the same" — wrong; tests-after answer
  "what does this do?", tests-first answer "what should this do?".
- Step 2's `Expected:` line says only "should fail" — write the substring.
- Skipping Step 5 to "batch commits at the end" — a lost-session recovery
  loses every uncommitted task.
- Ladder grows past 10 and you keep adding — split into rounds.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The test is so obvious I don't need to write it." | The implementation will be obvious after you write the test. Write the test. |
| "It'll fail for the wrong reason — pointless to run." | That's exactly what `Expected: FAIL — <fragment>` catches. Predict the right reason; if it fails for a different reason, the test is wrong. |
| "I'll commit at the end — too noisy otherwise." | Each Step-5 commit is the recovery breadcrumb when the session dies. |
| "The ladder is too long; I'll skip the verify-red step on the easy ones." | Skipping Step 2 is the failure mode the ladder exists to prevent. Split the ladder instead. |
| "The carve-out applies — trivially-small." | Record the carve-out in the ADR's Verification section so future readers know why the verification record is light. |

## Validator

Copy [scripts/validate_tdd_plans.py](scripts/validate_tdd_plans.py) into the
project's `scripts/` if a tracked ladder file is being kept (e.g.
`.agents/in-progress/<branch>.md`). It walks ladder files and asserts:

- Every Step-2 has `Run:` and `Expected: FAIL — <fragment>` sub-bullets.
- Every Step-4 has `Run:` and `Expected: PASS` sub-bullets.
- Every task ends with a Step-5 `Commit` checkbox.

## Related Skills

- `executing-plans` — orthogonal checkpoints for high-risk ADRs.
- `subagent-driven-development` — preferred executor for ladders > 5 tasks.
- `adr-driven-development` — the ADR is the upstream of every ladder; its
  Verification section is the downstream record.
