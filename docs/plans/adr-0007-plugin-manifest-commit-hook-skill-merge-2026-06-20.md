# ADR-0007: Plugin Manifest, Commit-Reminder Hook, and Skill Merge

- Status: Accepted
- Date: 2026-06-20

## Context

The repository was a collection of raw skill directories with no Claude Code
plugin identity and no automated guardrail to remind contributors to commit
meaningful progress. A separate `write-rfc` skill existed alongside
`adr-driven-development`, splitting the RFC→ADR lifecycle into two skills that
users had to know about independently.

Three related decisions were settled together:

1. How to package this repo as a Claude Code plugin.
2. Whether RFC and ADR authoring should live in one skill or two.
3. Whether to add a non-blocking commit reminder for the Stop event.

## Decision

**Plugin manifest.** Add `.claude-plugin/plugin.json` at the repository root.
It declares `name`, `version`, `description`, `author`, `skills_dir`, and
`hooks` pointer. Validation in `scripts/validate_skills.py` enforces that
`plugin.json` and `hooks/hooks.json` are present with required fields.

**Skill merge.** Absorb `skills/write-rfc/` into `skills/adr-driven-development/`.
The merged skill covers the full RFC → ADR lifecycle under one trigger
condition: *"design proposal needing discussion (RFC) or settled decision to
record (ADR)"*. The `rfc-template.md` moves to
`skills/adr-driven-development/references/`. All cross-references in
`AGENTS.md`, `docs/rfc/index.md`, `docs/plans/index.md`, and
`skills/development-best-practices/SKILL.md` are updated.

**Commit-reminder hook.** Add `hooks/hooks.json` (Stop event descriptor) and
`hooks/commit-reminder.sh`. The script runs `git status --porcelain`, filters
to tracked-only changes, and prints a human-readable reminder to stderr.
It always exits 0 (warn-only, never blocks). It is referenced via
`${CLAUDE_PLUGIN_ROOT}` to stay path-independent after installation.

## Consequences

- Contributors invoke one skill (`adr-driven-development`) for both the
  proposal and decision phases; no need to know two separate skill names.
- The plugin can be installed by pointing Claude Code at this directory.
- Validation will fail CI if the plugin manifest or hooks descriptor is
  accidentally deleted.
- The commit reminder surfaces uncommitted work at session end without
  preventing any action — zero friction cost, moderate safety benefit.
- ADR-0001 recorded the original split of `write-rfc` as a separate skill;
  this ADR supersedes that aspect of ADR-0001.
