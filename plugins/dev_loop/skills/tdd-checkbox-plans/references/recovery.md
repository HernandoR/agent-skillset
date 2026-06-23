# Recovery From Lost External Memory

The TDD ladder is session-scratch. If the session is killed mid-implementation,
reconstruct progress from durable artifacts.

## Step 1: Find The ADR

```bash
git log --oneline | head -20
# look for "feat: implementing ADR-NNNN — <slug>"
ls docs/plans/adr-NNNN-*.md
```

The ADR's Verification section names the validation expected at landing.

## Step 2: Read The Source RFC (If Present)

The RFC carries the why and the alternatives that were rejected. Re-reading
it is faster than re-deriving the rationale from the ADR alone.

## Step 3: Map `git log` Onto Tasks

Each completed Step-5 commit is a task checkpoint. On the feature branch:

```bash
git log <merge-base>..HEAD --oneline
```

The commit subjects map 1:1 to ladder tasks. If a commit message follows
`<type>(<scope>): <subject>` and references the ADR, you can recover the
task list directly.

## Step 4: Audit The Working Tree

For each task already shown in `git log`:

- Check the test file exists and the expected test name is present.
- Run the test to confirm it still passes:

  ```bash
  uv run pytest tests/<path> -v -k "<test-name>"
  ```

- If the test passes, the task is complete; mark it `[x]` in the
  reconstructed ladder.

## Step 5: Re-Derive Remaining Tasks

Walk the ADR's acceptance criteria. For each criterion not yet covered by a
test on disk, write a fresh ladder task using the template at
[task-template.md](task-template.md).

## Step 6: Resume

Pick up at the first `[ ]` task. Step 2 (verify red) is unchanged; the
ladder doesn't lose information by being reconstructed from the ADR plus the
repo.

## What You Lose

- The exact phrasing of failure fragments you predicted earlier — that's
  fine, you can re-predict.
- Notes you took inside the ladder file — those were ephemeral by design.
  If they were load-bearing, they belonged in the ADR Decision section, not
  the ladder.

## What Stays Recoverable

- ADR + RFC + `git log` + test files = enough to rebuild the ladder.
- The Verification section of the ADR records every carve-out and every
  passing test, so the audit trail does not depend on the ladder file
  surviving.
