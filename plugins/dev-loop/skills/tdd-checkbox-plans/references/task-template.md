# TDD Ladder — Task Template

External memory only. Live in session scratch, or for cross-session work
under `.agents/in-progress/<branch>.md` (never merged to main). When the
implementation lands, verification records fold into the ADR's Verification
section.

## Header

```markdown
# Ladder for ADR-NNNN — <title>

- ADR: docs/plans/adr-NNNN-...md
- Branch: <branch-name>
- Carve-out: none | trivially-small | shared-state-test | pure-refactor | spike
- Tasks: <N> (cap 10; split if larger)
```

## Per-Task Block

```markdown
## Task <k>: <one-line goal>

- [ ] **Step 1: Red test**
  Add a failing test exercising the new behaviour. Edit the file and content
  here so the diff is unambiguous.

- [ ] **Step 2: Verify red**
  - Run: `uv run pytest tests/<path> -v -k "<test-name>"`
  - Expected: FAIL — `<substring of the failure message>`

- [ ] **Step 3: Implementation**
  Make the minimal change required to satisfy the test. Note any structure
  the change forces (new module, new dependency).

- [ ] **Step 4: Verify green**
  - Run: `uv run pytest tests/<path> -v -k "<test-name>"`
  - Expected: PASS

- [ ] **Step 5: Commit**
  - Run: `git add <files> && git commit -m "<type>(<scope>): <subject>"`
  - Expected: clean working tree
```

## Anti-Patterns

```markdown
# BAD: Step 2 prose form
- [ ] **Step 2: Verify red**
  Run the test; it should fail.

# BAD: vague expected
- [ ] **Step 2: Verify red**
  - Run: `uv run pytest`
  - Expected: FAIL  ← which test? what fragment?

# BAD: combined steps
- [ ] Add test and implementation, run pytest, commit.

# GOOD: explicit sub-bullets
- [ ] **Step 2: Verify red**
  - Run: `uv run pytest tests/foo/test_bar.py::test_x -v`
  - Expected: FAIL — AttributeError: 'Foo' object has no attribute 'x'
```

## Soft Cap

If the task count is creeping past 10, stop adding. Split into rounds:

- Round 1 (this ladder): tasks 1-7. Goal: <…>.
- Round 2 (separate ladder, same ADR): tasks 8-14. Goal: <…>.

Each round commits to a clean intermediate state with passing tests. Recovery
works the same way per round.
