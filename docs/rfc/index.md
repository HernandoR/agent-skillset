# RFC Proposals

This directory holds RFCs (Requests for Comments) — proposals for design
discussion that have not yet reached a settled decision.

RFCs use the template at `skills/adr-driven-development/references/rfc-template.md`.

## File Naming

```text
rfc-{id}-{kebab-case-title}-{YYYY-MM-DD}.md
```

- `id` is a zero-padded four-digit sequence, independent from ADR IDs.
- `kebab-case-title` is a short slug; prefer six words or fewer.
- `YYYY-MM-DD` is the draft date.

## Current Proposals

| ID | Title | Status |
|---|---|---|
| [RFC-0001](rfc-0001-centralized-path-config-2026-06-03.md) | Centralized Path Config Skill | Resolved → [ADR-0002](../plans/adr-0002-centralized-path-config-2026-06-03.md) |
| [RFC-0002](rfc-0002-pydantic-config-tree-2026-06-03.md) | Pydantic Config Tree Skill | Resolved → [ADR-0003](../plans/adr-0003-pydantic-config-tree-2026-06-03.md) |
| [RFC-0003](rfc-0003-loguru-first-logging-2026-06-03.md) | Loguru-First Logging Skill | Resolved → [ADR-0004](../plans/adr-0004-loguru-first-logging-2026-06-03.md) |
| [RFC-0004](rfc-0004-agent-spec-and-tool-hook-2026-06-03.md) | Agent Spec Convention Skill | Resolved → [ADR-0005](../plans/adr-0005-agent-spec-convention-2026-06-03.md) |
| [RFC-0005](rfc-0005-tdd-checkbox-plans-2026-06-03.md) | TDD Checkbox Plans Skill (Advisory) | Resolved → [ADR-0006](../plans/adr-0006-tdd-checkbox-plans-2026-06-03.md) |
| [RFC-0006](rfc-0006-skill-implementation-deltas-2026-06-03.md) | Implementation Deltas From Skill Authoring | Draft |

## Process

- Use `skills/adr-driven-development` to draft a new proposal (RFC phase).
- Once discussion converges, create an ADR in `docs/plans/` via
  `skills/adr-driven-development`.
- Optionally link the resulting ADR back to the RFC for provenance.
- After the ADR is accepted, mark the RFC as `resolved` (do not delete).
