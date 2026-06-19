# Architecture Decision Records

This directory holds ADRs — settled design decisions recorded for future
reference. Each ADR captures context, the decision made, and its consequences.

ADRs use the template at `skills/adr-driven-development/references/adr-template.md`.

For proposals that are still under discussion, see `docs/rfc/`.

## File Naming

```text
adr-{id}-{kebab-case-title}-{YYYY-MM-DD}.md
```

- `id` is a zero-padded four-digit sequence, independent from RFC IDs.
- `kebab-case-title` is a short slug; prefer six words or fewer.
- `YYYY-MM-DD` is the draft date.

## Current Records

| ID | Title | Status |
|---|---|---|
| [ADR-0001](adr-0001-initial-skill-layout-2026-05-22.md) | Initial Skill Layout | Accepted |
| [ADR-0002](adr-0002-centralized-path-config-2026-06-03.md) | Centralized Path Config Skill | Accepted |
| [ADR-0003](adr-0003-pydantic-config-tree-2026-06-03.md) | Pydantic Config Tree Skill | Accepted |
| [ADR-0004](adr-0004-loguru-first-logging-2026-06-03.md) | Loguru-First Logging Skill | Accepted |
| [ADR-0005](adr-0005-agent-spec-convention-2026-06-03.md) | Agent Spec Convention Skill | Accepted |
| [ADR-0006](adr-0006-tdd-checkbox-plans-2026-06-03.md) | TDD Checkbox Plans Skill (Advisory) | Accepted |

## Process

- Proposals that need discussion belong in `docs/rfc/` — use `skills/adr-driven-development` (RFC phase).
- Once a decision is settled, create an ADR here — use `skills/adr-driven-development` (ADR phase).
- Existing records are historical artifacts and are not updated only to match
  later template changes.
