---
name: shrink-tests
description: Use when a TDD ladder has gone green and the tests it produced are about to be merged, when a branch diff adds tests that only restate the code they drove, or when the suite blocks refactoring instead of catching regressions. Triggers on "these tests are scaffolding now", "this test breaks every time I rename a field", "drop the redundant tests", "the suite fights every refactor". Not for deleting tests to turn a red suite green.
---

# Shrink Tests

## Overview

A TDD test does two jobs. While the code is red it **specifies** — it states
what the code must do. Once the code is green it **guards** — it catches a later
change that breaks the promise. Many tests stop doing the second job the moment
they finish the first. They stay in the suite as a copy of the implementation,
and every later refactor must update the copy.

Shrinking removes the copies and keeps the guards. The target is a suite that
fails when someone breaks a promise and stays silent when someone rewrites how
the promise is kept.

A shrink run never changes behaviour. It only deletes tests and merges tests.

## Default Scope

Review the tests this branch added or changed:

```bash
git diff --name-only <base>...HEAD -- '*test*' '*spec*'
git diff <base>...HEAD -- <those files>
```

The glob is a starting point, not the definition. The scope is the tests this
branch changed, wherever they live — a Rust `#[cfg(test)] mod tests` block
inside the production file, a Python doctest, a `FooTest.java` that the
lowercase pattern misses. When the pathspec returns nothing, read the whole
branch diff before concluding the branch added no tests.

That set is the scaffolding the ladder just produced, and it is the set whose
intent you still remember. Whole-suite auditing is a different, slower job — see
"Whole-Suite Mode", and only on request.

## The Criterion — Two Layers

### Layer 1 — Coupling count (screen)

Ask: **name every independent place in the code I would have to edit to make
this test fail.**

- **Two or more places → Keep. Stop here.** The test holds an agreement that no
  single location states. Delete it and the agreement has no record left.
- **Exactly one place → candidate.** Continue to Layer 2.

Layer 1 deletes nothing. It only decides what gets examined.

### Layer 2 — Derivation (verdict)

For each one-place candidate, ask: **could I have written this test from the
requirement alone, without reading the implementation?**

Cover the implementation. Read the ADR line, the docstring, the bug report, or
the interface contract. Try to re-derive the test from those.

- **Re-derivable → Keep.** The test is an independent statement of the
  expectation. A boundary test on a pure function couples to one place and is
  still a keep. The test states the expected range from the requirement's
  side. The code states the same range from the other side. Two independent
  descriptions of one range are the reason to keep it.
- **Not re-derivable → Delete or Merge.** The test was transcribed from the
  code. It carries nothing the code does not already carry, so it cannot fail
  for a reason worth knowing.

One-sentence form: **when this test fails, does it tell me anything the diff did
not already tell me?** If the only message is "you changed the line you just
changed", the test is a copy of that line.

## Archetypes

### Delete — mirrors

- **Constant mirror** — `assert MAX_RETRIES == 3`. The constant *is* the code;
  the assertion is a second copy in a second file.
- **Attribute mirror** — a class attribute, a dataclass default, or an enum
  member list compared against its own literal.
- **Transcription set** — one test per branch of one function, named after the
  implementation (`test_returns_early_when_cache_hit`), written by reading that
  function top to bottom.
- **Call-shape mock** — `assert_called_once_with(a, b)` where the argument list
  was copied from the call site. It pins the call, not the outcome.
- **Trivial surface** — getters, setters, `__repr__`, pass-through delegation, a
  constructor that only assigns.
- **Literal twin** — the same behaviour as a neighbouring test with a different
  input value and no new region of behaviour.

### Merge — fold, do not drop

- Several constant or attribute assertions that all serve one invariant become
  one table test of the invariant: *every declared lifecycle value is in
  `LIFECYCLE`*, *every registered crawler name resolves to a settings class*.
  The merged test fails when someone breaks the relationship, not when someone
  changes a number on purpose.
- Several one-method tests of one class become one test that runs a realistic
  sequence and asserts the end state. That version also catches order-dependent
  bugs that none of the single-method tests could reach.
- Overlapping edge cases become one boundary table with the cases as parameters.

A merge is the default answer whenever a delete would remove the last cover of a
real case.

### Keep — never delete without a named replacement

- **Cross-location contracts** — a producer and a consumer that must agree, two
  mirrored copies that must stay in sync, a serialized format another module
  reads, an exit code raised in one place and mapped in another.
- **Multi-method sequences** — state written by one method and read by another.
- **Boundary and range** — empty, `None`, zero, one, maximum, off-by-one,
  timezone, unicode, overflow, duplicate.
- **Regression tests for fixed bugs** — the test records a fact the code cannot
  state, namely that this case was once wrong.
- **Anything whose failure names a broken promise** instead of a changed value.

## Procedure

1. **Start green and clean.** Run the suite. Record the pass count and a
   **per-line coverage artifact** — `coverage xml`, `lcov.info`, or the
   equivalent — not a summary percentage. Never shrink on red and never on a
   dirty tree.
2. **Inventory.** One row per added or changed test: `file:line`, test name, and
   the places it pins.
3. **Screen.** Apply Layer 1 to every row.
4. **Judge.** Apply Layer 2 to the one-place rows only.
5. **Propose and stop.** Present the table with a verdict per row — Delete,
   Merge, or Keep — one sentence of reasoning on every Delete and Merge row, and
   the merged tests written out. Make no edits yet. Wait for approval.
6. **Apply merges first, then deletions.** Re-measure coverage between the two
   passes. A merged table test usually adds cover, because it iterates a whole
   set. Batch the two passes together and that gain can hide a deletion that
   removed the last cover of some other line.
7. **Verify line by line.** The suite is green and the test count is down.
   Compare the new coverage artifact against the Step-1 baseline **per line and
   per branch**: no line that had cover before the shrink may have zero cover
   after it. A summary percentage cannot show this, because the two passes net
   out inside one number. A line that lost its only cover names the row that
   took it — restore that test, or fold its case into a surviving one.
8. **Commit alone.** `test(<scope>): drop scaffolding tests for <feature>`. A
   shrink never shares a commit with a behaviour change, so a later `git revert`
   restores the tests without dragging code back with them.

A `Keep` needs no justification. A `Delete` or a `Merge` needs a sentence.

## Safety Rails

- **Never on red.** A failing test is not a shrink candidate. Deleting it hides
  a real failure and calls the result cleanup. Fix the test, or delete it as its
  own decision with its own stated reason.
- **Never in the same commit as a behaviour change.**
- **Read every candidate to the end.** A test that opens with three mirror
  assertions and closes with a real contract assertion is a Keep, or a Merge
  that preserves the closing assertion.
- **"Annoying" is not a verdict.** A test that breaks on every rename is one of
  two things. It is a mirror, so delete it. Or it is a contract pinned to a
  name, which means the design couples to that name — fix the design and keep
  the test.
- **Stay inside the diff.** In default scope, leave tests the branch did not
  touch alone, even when they look like mirrors.

## Red Flags — STOP

- Coverage dropped and the run continued anyway.
- The suite went from red to green across the shrink.
- The delete list holds the last test of an error path or an exception branch.
- The delete list holds a test whose origin you cannot name.
- "Delete them now and re-add later if needed." Nobody re-adds them.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The test is short, so keeping it costs nothing." | The cost is not runtime. Every mirror is a second place to edit on the next refactor. The edit is mechanical, so it gets made without thought. That is how a suite stops catching anything. |
| "It couples to one place, so the rule says delete." | The rule says *examine*. Layer 2 decides. A boundary test on one function stays. |
| "It covers a public API, so it must be a contract." | Public is not the same as agreed. If no second location depends on the value, the test still mirrors one line. |
| "Coverage drops, but that path is obviously fine." | Then the path has no cover and no reader. Fold the case into a surviving test instead of dropping it. |
| "I'll shrink while I finish the feature." | Shrinking on a dirty tree hides which failure came from which change. Land the feature green, then shrink. |
| "The merged table test is harder to read than five asserts." | The five asserts state a value five times. The table states the relationship once, which is the thing that can actually break. |

## Whole-Suite Mode

On explicit request, the rubric is unchanged and only the sequencing differs.
Do not inventory the whole suite at once. Rank first by the two signals that
predict mirrors:

- test files that changed in lockstep with one production file across history
  (co-change in `git log --name-only`);
- test names that quote implementation details rather than expectations.

Then take one module at a time through the full procedure: propose, apply,
verify, commit. A bulk delete spanning modules cannot be reviewed and cannot be
bisected.

## Related Skills

- `tdd-checkbox-plans` — upstream. The ladder produces these tests; shrinking is
  what happens after the last task goes green.
- `verification-before-completion` — the suite and coverage evidence in Step 7
  is the completion claim for a shrink.
- `finishing-a-development-branch` — shrink before the merge decision, not after.
- `reclaim-code-entropy` — the same evidence-first cut applied to production
  code instead of test code.
