---
name: shrink-tests
description: Use when a TDD ladder has reached green and its tests are about to merge, when a branch diff adds tests that only restate the code they drove, or when the test suite prevents refactoring instead of catching regressions. Triggers on "these tests only repeat the code", "this test fails after every rename", "drop the redundant tests", "the suite blocks every refactor". Do not use it to delete failing tests and make a red suite green.
---

# Shrink Tests

## Overview

A TDD test does two jobs. While the code is red, the test **specifies**: it
states what the code must do. After the code is green, the test **guards**: it
catches a later change that breaks the required behaviour.

Many tests stop after the first job. The author writes such a test while reading
the implementation, so the test holds a copy of that implementation. This skill
calls that test a **mirror**. A mirror cannot fail for a reason worth knowing,
and every later refactor must still update it.

Shrinking deletes the mirrors and keeps the guards. A shrunk suite fails when a
change breaks the required behaviour. It stays silent when a change only
rewrites how the code supplies that behaviour.

A shrink run never changes behaviour. It only deletes tests and merges tests.

## Default Scope

Review the tests that this branch added or changed:

```bash
git diff --name-only <base>...HEAD -- '*test*' '*spec*'
git diff <base>...HEAD -- <those files>
```

The glob is a start, not the definition of the scope. The scope is every test
that this branch changed, at any location. The glob misses three common cases:
a Rust `#[cfg(test)] mod tests` block inside the production file, a Python
doctest, and a `FooTest.java` that the lowercase pattern does not match. If the
pathspec returns no file, read the full branch diff. Do not report that the
branch added no test until you do this.

This set is the output of the most recent ladder, and you still know the intent
of each test in it. A review of the full suite is a different task. Do that task
only on request. See "Whole-Suite Mode".

## The Criterion — Two Layers

### Layer 1 — Coupling count (screen)

For each test, ask this question: **which independent places in the code must I
edit to make this test fail?** Name each place.

- **Two or more places → Keep. Stop here.** The test holds an agreement that no
  single place states. If you delete the test, no record of the agreement
  remains.
- **Exactly one place → candidate.** Go to Layer 2.

Layer 1 deletes no test. Layer 1 only selects the tests to examine.

### Layer 2 — Derivation (verdict)

For each candidate from Layer 1, ask this question: **can I write this test from
the requirement alone, without reading the implementation?**

Hide the implementation. Read the ADR line, the docstring, the defect report, or
the interface contract. Then write the test again from those sources.

- **You can write it again → Keep.** The test is an independent statement of the
  requirement. A boundary test on a pure function couples to one place, and it
  is still a Keep. The test states the permitted range from the requirement
  side. The code states the same range from the other side. Two independent
  statements of one range are the reason to keep the test.
- **You cannot write it again → Delete or Merge.** The author copied the test
  from the code. The test holds no information that the code does not hold, so
  it cannot fail for a reason worth knowing.

The same question in short form: **if this test fails, does it tell me anything
that the diff does not tell me?** If the only message is "you changed the line
that you just changed", the test is a mirror of that line.

## Archetypes

### Delete — mirrors

- **Constant mirror** — `assert MAX_RETRIES == 3`. The constant is the code. The
  assertion is a second copy of the constant in a second file.
- **Attribute mirror** — a class attribute, a dataclass default, or an enum
  member list, compared against its own literal.
- **Transcription set** — one test for each branch of one function. The name
  quotes the implementation, for example `test_returns_early_when_cache_hit`.
  The author wrote the set while reading the function.
- **Call-shape mock** — `assert_called_once_with(a, b)`, where the author copied
  the argument list from the call site. The test pins the call, not the result.
- **Trivial surface** — a getter, a setter, `__repr__`, a delegation that holds
  no logic, or a constructor that only assigns.
- **Literal twin** — the same behaviour as an adjacent test, with a different
  input value and no new region of behaviour.

### Merge — keep the case, delete the duplication

- Several constant assertions or attribute assertions serve one invariant.
  Replace them with one table test of that invariant. Examples: *every declared
  lifecycle value is in `LIFECYCLE`*, *every registered crawler name resolves to
  a settings class*. The table test fails when a change breaks the relationship.
  It does not fail when a person changes a number on purpose.
- Several one-method tests cover one class. Replace them with one test that runs
  a realistic sequence of calls and asserts the final state. The replacement
  also catches order-dependent defects that no single-method test can reach.
- Several edge-case tests overlap. Replace them with one boundary table that
  holds the cases as parameters.

Select Merge, not Delete, whenever a Delete removes the last cover of a real
case.

### Keep — delete none of these without a named replacement

- **Cross-location contracts** — a producer and a consumer that must agree, two
  mirrored copies that must stay equal, a serialized format that another module
  reads, or an exit code that one place raises and another place maps.
- **Multi-method sequences** — one method writes the state, and another method
  reads it.
- **Boundary and range** — empty, `None`, zero, one, maximum, off-by-one,
  timezone, unicode, overflow, and duplicate.
- **Regression tests for fixed defects** — the test records a fact that the code
  cannot state, which is that this case was wrong before.
- Any test whose failure reports a broken requirement, not a changed value.

## Procedure

1. **Start green and clean.** Run the suite. Record the count of passing tests.
   Record a **per-line coverage artifact**: `coverage xml`, `lcov.info`, or the
   equivalent. Do not record only a summary percentage. Never shrink while the
   suite is red. Never shrink while the tree is dirty.
2. **Inventory.** Make one row for each added test and each changed test. Each
   row holds `file:line`, the test name, and the places that the test pins.
3. **Screen.** Apply Layer 1 to every row.
4. **Judge.** Apply Layer 2 to the one-place rows only.
5. **Propose, then stop.** Show the table. Give each row a verdict: Delete,
   Merge, or Keep. Give one sentence of reasoning for each Delete row and each
   Merge row. Write out each merged test in full. Make no edit yet. Wait for
   approval.
6. **Apply the merges first. Apply the deletions second.** Measure coverage
   again between the two passes. A merged table test usually adds cover, because
   it iterates a full set. In one combined pass, that added cover can hide a
   deletion that removed the last cover of a different line.
7. **Verify line by line.** Confirm that the suite is green and that the test
   count is lower. Compare the new coverage artifact against the Step-1 baseline
   **for each line and each branch**. No line that had cover before the shrink
   may have zero cover after it. A summary percentage cannot show this, because
   the two passes cancel inside one number. When a line loses its only cover,
   the comparison names the row that removed it. Restore that test, or add its
   case to a test that remains.
8. **Commit the shrink alone.** Use `test(<scope>): drop mirror tests for
   <feature>`. A shrink never shares a commit with a behaviour change. A later
   `git revert` then restores the tests and changes no production code.

A Keep row needs no reasoning. A Delete row and a Merge row each need one
sentence.

## Safety Rails

- **Never shrink while the suite is red.** A failing test is not a shrink
  candidate. If you delete it, you hide a real failure and record the result as
  cleanup. Repair the test instead. If the test must go, delete it as a separate
  decision and state the reason.
- **Never put a shrink and a behaviour change in one commit.**
- **Read every candidate to its last line.** A test can open with three mirror
  assertions and close with a real contract assertion. That test is a Keep, or a
  Merge that retains the closing assertion.
- **"Annoying" is not a verdict.** A test that fails after every rename is one
  of two things. It is a mirror, so delete it. Or it is a contract that is
  pinned to a name, which means the design couples to that name. In the second
  case, repair the design and keep the test.
- **Stay inside the diff.** In the default scope, do not touch a test that the
  branch did not change, even when that test looks like a mirror.

## Red Flags — STOP

- Coverage decreased, and the run continued.
- The suite changed from red to green across the shrink.
- The delete list holds the last test of an error path or an exception branch.
- The delete list holds a test whose origin you cannot name.
- You plan to delete tests now and to add them again later if they are needed.
  Nobody adds them again.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The test is short, so it costs nothing to keep." | The cost is not run time. Each mirror is a second place to edit at the next refactor. The edit is mechanical, so the author makes it without thought. A suite in that state stops catching defects. |
| "It couples to one place, so the rule says delete it." | The rule says examine it. Layer 2 gives the verdict. A boundary test on one function stays. |
| "It covers a public API, so it must be a contract." | Public and agreed are not the same. If no second place depends on the value, the test still mirrors one line. |
| "Coverage decreases, but that path is clearly correct." | Then the path has no cover and no reader. Add its case to a test that remains, instead of deleting the case. |
| "I will shrink while I finish the feature." | A shrink on a dirty tree hides which change caused which failure. Complete the feature, reach green, then shrink. |
| "The merged table test is harder to read than five assertions." | The five assertions state a value five times. The table states the relationship once, and the relationship is the part that can break. |

## Whole-Suite Mode

Use this mode only on an explicit request. The criterion does not change. Only
the sequence changes.

Do not inventory the full suite in one pass. Rank the modules first, by two
signals that predict mirrors:

- a test file that changed together with one production file across the history
  (co-change in `git log --name-only`)
- test names that quote implementation details instead of requirements

Then take one module at a time through the full procedure: propose, apply,
verify, commit. Nobody can review a bulk delete that spans modules, and
`git bisect` cannot isolate it.

## Related Skills

- `tdd-checkbox-plans` — the upstream skill. The ladder writes these tests.
  Shrink them after the last task reaches green.
- `verification-before-completion` — the suite result and the coverage
  comparison in Step 7 are the completion evidence for a shrink.
- `finishing-a-development-branch` — shrink before the merge decision, not after
  it.
- `reclaim-code-entropy` — the same evidence-first method, applied to production
  code instead of test code.
