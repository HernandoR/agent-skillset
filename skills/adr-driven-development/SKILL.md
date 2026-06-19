---
name: adr-driven-development
description: Use when a design proposal needs discussion before a decision (RFC), or when a decision has been made and should be recorded as a lightweight Architecture Decision Record (ADR) that future contributors can reference.
---

# ADR-Driven Development

## Overview

This skill covers the full RFC → ADR lifecycle:

1. **RFC phase** — when a design direction is still open, draft a Request for Comments to surface alternatives, risks, and open questions. An RFC invites discussion; it is not a decision.
2. **ADR phase** — once the RFC discussion converges (or a decision is made directly), record it as an Architecture Decision Record. An ADR is an immutable record of a settled choice.

Follow the conventions at <https://adr.github.io/>.

## When to Use

| Phase | Trigger |
|---|---|
| RFC | Design direction is open, multiple viable approaches exist, or architectural reviewers should see reasoning before implementation starts. |
| ADR | A decision is settled — after RFC convergence, team review, or an individual judgment call. |

Do not use for:

- Narrow typo fixes, internal prose edits, or mechanical metadata updates.
- Decisions that are trivially reversible with zero architectural impact.

## File Conventions

```text
docs/rfc/rfc-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md     # RFC proposals
docs/plans/adr-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md   # ADR records
```

Maintain `docs/rfc/index.md` and `docs/plans/index.md` sorted by their respective IDs. IDs are independent sequences. Never reuse an ID.

## Templates

- RFC: use `references/rfc-template.md`
- ADR: use `references/adr-template.md`

## RFC Workflow

1. Identify a design question that would benefit from structured discussion.
2. Draft the RFC from `references/rfc-template.md`: problem, alternatives, risks, open questions.
3. Share with reviewers; update the document as discussion evolves.
4. Once the discussion converges, create an ADR (see ADR Workflow below) to record the settled outcome.
5. Optionally link the ADR back to the RFC for full provenance.
6. Mark the RFC as `Resolved` in `docs/rfc/index.md` with a link to the ADR (do not delete the file).

## ADR Workflow

1. Once a decision is settled, check `docs/plans/index.md` for related ADRs.
2. If the decision is already recorded, do not duplicate. Amend the existing ADR only if the decision itself changed.
3. Otherwise, create the next ADR file from `references/adr-template.md`.
4. Set the status to `accepted`; capture context, decision, and consequences.
5. Reference the ADR from relevant implementation commits.

## Status Values (ADR)

- `proposed` — drafted but awaiting final sign-off.
- `accepted` — the decision is in effect.
- `rejected` — considered but intentionally not adopted.
- `deprecated` — no longer in effect (superseded or withdrawn).
- `superseded` — replaced by a later ADR (link the replacement).

## RFC vs ADR

| | RFC | ADR |
|---|---|---|
| Purpose | Propose an idea for **discussion** | Record a decision **made** |
| Content | Problem → Alternatives → Open Questions | Context → Decision → Consequences |
| Tone | Exploratory, future or conditional tense | Declarative, past or present tense |
| Contains | Multiple viewpoints, discussion process | One settled choice + rationale |
| When | Before or during the decision process | After the decision is settled |

## Common Mistakes

- Skipping the RFC phase for architecturally significant changes.
- Writing an ADR before the decision is actually settled.
- Recording every micro-decision instead of architecturally significant ones.
- Failing to link a superseded ADR to its replacement.
- Treating an RFC as the final word instead of a discussion artifact.
- Failing to create a follow-up ADR once an RFC converges.
