# ADR-0014: Shrink-Tests Skill

- Status: Accepted
- Date: 2026-09-20

## Context

ADR-0006 put `tdd-checkbox-plans` in the `dev-loop` bundle. The ladder it
prescribes is deliberate about producing tests: every task writes a red test
before any implementation. It says nothing about what happens to those tests
after the last task goes green.

The result is a known failure mode. A TDD test does two jobs — it **specifies**
while the code is red, and it **guards** once the code is green. Many tests only
ever do the first. They are written by transcribing the implementation that is
being built, so after green they are a copy of the code in a second file. The
suite then grows a fraction that cannot fail for a reason worth knowing, and
that fraction makes every later refactor more expensive. A suite in that state
stops preventing regressions and starts preventing change.

The maintainer already carries a narrow version of this rule at user level
("do not test what a constant is"). It covers the smallest archetype — an
assertion that a constant equals its own literal — and leaves the general case
unstated.

The obvious general rule is a coupling count: *if only one place in the code has
to change for a test to fail, the test is one-to-one with that place and is
redundant*. Taken literally that rule over-deletes. A boundary test on a pure
function also couples to exactly one place, and it is one of the most valuable
tests in any suite, because it states the expected range from the requirement's
side while the code states it from the other side.

## Decision

- **Add `shrink-tests` to `dev-loop`**, next to `tdd-checkbox-plans`. The skill
  removes what the ladder leaves behind, so it belongs in the same bundle rather
  than in `reclaim-code-entropy`, which is vendored and scoped to production
  code.
- **The criterion is two layers, and only the second one decides.**
  - *Layer 1, coupling count*, is a screen. Two or more independent code
    locations means Keep, and the examination stops. Exactly one location makes
    the test a candidate. Layer 1 deletes nothing by itself.
  - *Layer 2, derivation*, is the verdict. Cover the implementation and ask
    whether the test could have been written from the requirement alone. A test
    re-derivable from an ADR line, a docstring, a bug report, or an interface
    contract is an independent statement and is kept. A test that could only
    have been written by reading the implementation is a mirror and is deleted
    or merged.

  This ordering is what keeps boundary tests. They fail the coupling screen and
  pass the derivation check, and the derivation check wins.
- **Merge outranks delete.** Several mirror assertions that serve one invariant
  collapse into one table test of the invariant, which fails when the
  relationship breaks rather than when a value changes on purpose. A delete that
  would remove the last cover of a real case is a merge instead.
- **Default scope is the branch diff.** The tests this branch added or changed
  are the mirrors whose intent is still remembered. Whole-suite auditing is
  available on request, one module at a time, ranked by co-change history and by
  test names that quote implementation details. A bulk delete across modules can
  be neither reviewed nor bisected.
- **The skill proposes and waits.** It produces a classified table — Delete,
  Merge, Keep, one sentence of reasoning each — and makes no edits before
  approval. This matches the advisory posture of the rest of the repo, and test
  deletion is not reversible by re-running anything.
- **Coverage is the verification gate, measured line by line.** A shrink must
  leave the suite green and the test count lower, and no line or branch that had
  cover before the shrink may have zero cover after it. A summary percentage is
  not the gate, because a percentage can stay level while one line loses its
  only cover. The Step-1 baseline is therefore a per-line artifact. Merges are
  applied and measured before deletions for a second reason, which is
  attribution: the per-line gate reports the lost line in either order, but only
  a measurement taken between the two passes says which pass removed the cover,
  and so whether to restore a deleted row or to extend the merged table.
- **The shrink is always its own commit**, never shared with a behaviour change
  and never run on red or on a dirty tree, so a later revert restores the tests
  without dragging code back.
- **Versions.** `dev-loop` goes 0.4.0 → 0.5.0 (minor: new skill). The
  marketplace and `package.json` go 0.13.0 → 0.14.0.

## Consequences

- The `dev-loop` bundle now covers the whole life of a test, from the red step in
  `tdd-checkbox-plans` to the shrink before `finishing-a-development-branch`.
- The "do not test what a constant is" rule becomes one archetype under a stated
  general criterion instead of a standalone user-level preference.
- The two-layer criterion needs judgment at Layer 2 and cannot be mechanized, so
  the skill ships no validator script. `tdd-checkbox-plans` ships one because
  its checks are structural; there is no structural signal that separates a
  transcribed test from a derived one.
- Propose-then-apply makes a shrink run slower than an autonomous cleanup. That
  cost is accepted, because a wrongly deleted test is silent until the
  regression it would have caught ships.
- The chain above needs upstream routing to exist, so three artifacts now point
  at the skill: the `development-best-practices` router, the `tdd-checkbox-plans`
  Related Skills handoff, and the `finishing-a-development-branch` precondition.
  Without them an agent reaches the skill only when the user says a trigger
  phrase. The router gains `tdd-checkbox-plans` at the same time, which it had
  omitted.
- ADR-0013 classified no `SKILL.md` body, so this skill raised the question of
  which register binds one. ADR-0015 settles it: a skill body is Strict. This
  skill is written to Strict as the first application of that rule.
