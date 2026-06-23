---
name: finishing-a-development-branch
description: Use after implementation work is verified and the branch needs a merge, pull request, preservation, cleanup, or discard decision.
---

# Finishing A Development Branch

## Overview

End branch work deliberately: verify, present integration choices, execute the
chosen path, and clean up only when appropriate.

## Required Precondition

Run the project verification command before offering finish options. Prefer
`just ci` when available. If verification fails, stop and report the failure.

## Determine The Base

Find the likely base branch:

```bash
git merge-base HEAD main
git merge-base HEAD master
```

If ambiguous, ask which base branch to use.

## Present Options

After verification passes, present these choices:

```text
Implementation verified. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a pull request
3. Keep the branch as-is
4. Discard this work
```

Do not discard work without exact confirmation from the user.

## Cleanup Rules

- Merge locally: verify again after merge, then delete the feature branch if the
  merge is complete.
- Pull request: push the branch and keep the worktree unless the user asks for
  cleanup.
- Keep as-is: preserve branch and worktree.
- Discard: require typed confirmation and list what will be removed.

## Common Mistakes

- Offering merge or PR options while verification is failing.
- Deleting a worktree after creating a PR when the user may still need it.
- Force-deleting a branch without explicit confirmation.

