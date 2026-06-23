---
name: agent-spec-convention
description: Use when adding a project-level rule that AI coding agents should follow (no-print, no-inline-paths, naming conventions, commit format, etc.) and the rule must be discoverable by any harness — Claude Code, Codex, Cursor, Kiro — not pinned to a single editor's hook system.
---

# Agent Spec Convention

## Overview

Project rules belong in either `AGENTS.md` (short rules, ≤ 30 lines) or
`.agents/spec/<rule>.md` (longer rules, full spec). Any harness that loads
`AGENTS.md` / `.agents/` picks them up. The schema-and-linter pair shipped here
keeps the rules consistent and prevents `AGENTS.md` from drifting away from
its `.agents/spec/` body.

## When To Use

- Adding a new project rule that must apply across editor / agent harnesses.
- Reviewing a project where rules live in `docs/` (not loaded by most
  harnesses) or only in `CLAUDE.md` (not loaded by Codex/Cursor).
- Setting up a new project's agent-facing rule layer.

Do not use for rules with no agent-facing implication (e.g. internal
release-process docs aimed at humans).

## Rule Locations

| Rule length | Location |
|---|---|
| ≤ 30 lines, single concept | Inline section under `AGENTS.md` |
| Longer, with examples | `.agents/spec/<rule-name>.md`, summary in `AGENTS.md` |

`docs/` is rejected because it is not loaded by every harness.

## Spec Schema

Every `.agents/spec/<rule>.md` has frontmatter and five required H2 sections in
this order:

```markdown
---
name: <rule-slug>
version: 1
last_updated: YYYY-MM-DD
# optional:
# superseded_by: <other-rule-slug>
---

# <Rule Title>

## Rule
The rule itself, in ≤ 5 sentences.

## Why
Motivation, with the failure mode the rule prevents.

## Where
Allow-list of files where the rule does not apply, plus boundary conditions.

## Examples
At least one BAD/GOOD pair. Use `# BAD` / `# GOOD` (or language-appropriate
comment markers) above each block. Structural rules may use Before/After
trees or YAML snippets in place of code.

## References
Cross-links to ADRs, related specs, external docs.
```

Versioning lives in **frontmatter**, never in the filename. Bump `version`
on substantive changes; set `superseded_by:` on retirement.

## `AGENTS.md` Mirror

Every `.agents/spec/<rule>.md` has a corresponding section in `AGENTS.md`:

```markdown
### <Rule Title>
<one paragraph stating the rule>

Full spec: [.agents/spec/<rule-name>.md](.agents/spec/<rule-name>.md)
```

The summary's first sentence must match the spec's `## Rule` first sentence
verbatim (the linter checks this). No verbatim include — the spec body must
not be duplicated in `AGENTS.md`. No bare links — there must be a paragraph.

## Linter

Copy [scripts/validate_agent_specs.py](scripts/validate_agent_specs.py) into
the project's `scripts/`. It is stdlib-only and:

- walks every file under `.agents/spec/*.md`
- validates frontmatter (`name`, `version`, `last_updated` required)
- asserts the five H2 headings appear in order
- asserts `## Examples` contains at least one `BAD` and one `GOOD` label
- asserts every `AGENTS.md` rule section has a matching spec file and that
  the first-sentence-mirror rule holds
- supports a per-section opt-out: `<!-- agent-spec: skip-section <name> -->`

Wire it into `just validate` or pre-commit.

## Skip-Section Opt-Out

When a section legitimately doesn't apply (e.g. a rule with no good/bad
example because it's purely structural), add the opt-out comment immediately
before the heading:

```markdown
<!-- agent-spec: skip-section Examples -->
## Examples
This rule is structural; see Where for the boundary specification.
```

The linter records the opt-out and skips structural checks for that section.

## Worked Example

[references/example-spec.md](references/example-spec.md) is a complete
schema-conforming spec the linter self-tests against.

## Common Mistakes

- Putting rules in `docs/` and assuming agents will find them.
- Versioning by filename (`no-inline-paths-v2.md`) — frontmatter and
  `superseded_by` carry version history.
- Duplicating spec body into `AGENTS.md` — the body lives in one place; the
  mirror is summary + link.
- Editor-specific hook templates as part of the rule. Hooks are out of
  scope; if the ecosystem converges on a portable hook spec later, that's a
  new ADR.

## Related Skills

- `centralized-path-config` — ships `no-inline-paths.md` conforming to this
  schema.
- `loguru-first-logging` — ships `no-print-no-stdlib-logging.md` conforming
  to this schema.
