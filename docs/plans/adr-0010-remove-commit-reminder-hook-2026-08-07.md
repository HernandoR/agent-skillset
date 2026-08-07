# ADR-0010: Remove the Commit-Reminder Hook

- Status: Accepted
- Date: 2026-08-07

## Context

ADR-0007 accepted a commit-reminder hook for `dev_loop`: a Stop-event
descriptor plus `hooks/commit-reminder.sh`, which would run `git status
--porcelain` and print a reminder to stderr. It was explicitly warn-only and
always exited 0.

What shipped was something else. `plugins/dev_loop/hooks/hooks.json` registered
a **SessionStart** hook running `install-claude-md.sh`, which appended a rule to
the user's `~/.claude/CLAUDE.md` instructing every agent to "stage them, write
an appropriate commit message, and commit automatically without asking the
user". Two problems, independent of each other:

1. **It was not the accepted decision.** A warn-only reporter became a mutation
   of the user's global agent configuration, performed silently at startup, on
   a file no bundle in this repo owns. The append was idempotent by marker, but
   nothing removed it on uninstall, so the plugin left a permanent instruction
   behind.
2. **The rule it installed is wrong.** Committing without asking takes a
   decision that belongs to the user — what enters history, under what message,
   on which branch. It also contradicts the guidance this repo ships: the
   `git-workflow-and-versioning` and `verification-before-completion` skills
   have the agent commit *verified* steps deliberately, not sweep the worktree
   at session end.

The hook was also broken in practice — the script was committed non-executable
(mode `100644`) and invoked as a bare command, so every session started with a
`Permission denied` error. That surfaced the hook, but is not the reason for
removing it.

## Decision

Delete `plugins/dev_loop/hooks/` entirely — both `hooks.json` and
`install-claude-md.sh`. `dev_loop` ships skills only.

The general rule: **this repo does not ship hooks that write to a user's global
configuration or act on their repository unprompted.** A bundle may state a
convention in a skill and let the agent apply it in context; it may not install
a standing instruction into `~/.claude/CLAUDE.md` on the user's behalf. If a
guardrail genuinely needs to run as a hook, it reports and exits 0 — it does
not mutate files outside the project, and never commits.

`plugins/dev_loop/.claude-plugin/plugin.json` never declared a `hooks` pointer
(Claude Code discovered the directory implicitly), so there is no pointer to
remove — but the deletion is a payload change, so `dev_loop` goes to `0.3.0`
and the marketplace and `package.json` to `0.4.0`. Installed copies resolve by
version; without the bump the deletion never reaches anyone who already
installed the bundle. `hooks` stays in the validator's recognised-key sets,
which mirror Codex's manifest schema and are not a statement that this repo
uses hooks.

This supersedes the commit-reminder hook portion of ADR-0007. The plugin
manifest and skill merge decisions in ADR-0007 stand.

## Consequences

- Installing `dev_loop` no longer modifies anything outside the plugin cache.
- Users who installed an affected version keep a stale
  `<!-- dev_loop-plugin:commit-reminder -->` marker in `~/.claude/CLAUDE.md`.
  Removal is manual; the plugin cannot clean up what it should not have written.
- The commit discipline ADR-0007 wanted is now carried only by skills, which
  the agent applies with judgement. That is weaker enforcement, and it is the
  intended trade: an unasked-for commit is more costly than a missed reminder.
- ADR-0007's consequence "validation will fail CI if the hooks descriptor is
  accidentally deleted" no longer holds — the validator never enforced a hooks
  descriptor, so nothing needed relaxing.
