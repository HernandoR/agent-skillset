---
name: adr-driven-development
description: Use when capturing design discussion that should survive across sessions and contributors (RFC), or when recording/updating the settled design intent a project commits to (ADR). Triggers whenever a design direction is being debated, an architectural choice gets made, an existing decision needs revising, or someone asks "why is it built this way?" or "what is this supposed to do?". Covers the RFC→ADR record lifecycle, not the per-session implementation plan that executes a decision.
---

# ADR-Driven Development

## The Mental Model: Three Sources of Truth

A project carries three different kinds of truth, and confusing them is the
root of most documentation rot. Keep them separate:

| Artifact | Answers | Nature |
|---|---|---|
| **Code** | *How the system behaves **now*** | The ground truth of the present |
| **ADR** | *How the system is **supposed** to be designed* | The committed intent, kept current |
| **RFC** | *How we **arrived** at that intent* | The discussion trail, never rewritten |

Two consequences fall out of this, and they drive everything else in this
skill:

- **The gap between the ADRs and the code is the work that remains.** ADRs
  describe the target; code is the actual. When they disagree, either the code
  hasn't caught up (there's implementation to do) or the ADR is stale (update
  it). An ADR is valid *with or without* a matching implementation — it states
  intent, not status.
- **RFCs and ADRs are maintained in opposite ways.** An RFC is an *append-only
  log*: discussion accumulates, nothing is erased. An ADR is *edited
  atomically*: it always reads as one clean, current statement of intent. More
  on why below.

## What This Skill Does NOT Cover

The **implementation plan** — the per-session, step-by-step ladder that turns
an accepted ADR into committed code — is out of scope here. That is ephemeral
execution state ("external memory"), not a durable design record, and it is
handled by other skills (e.g. `tdd-checkbox-plans`) or task-tracking MCP tools.

The boundary: this skill governs the two *durable records* (RFC and ADR). The
moment you're sequencing tasks, predicting test failures, or tracking
in-progress checkboxes, you've left this skill and entered implementation
planning.

## RFC: The Append-Only Discussion Log

An RFC captures *how a design question was reasoned through* — the problem, the
alternatives weighed, the trade-offs, the dead ends, the open questions. It is
contributed to by whoever is in the room: multiple humans, multiple agents,
across however many sessions the question takes to resolve.

**Why append-only?** The value of an RFC is the reasoning trail. A later
contributor — or an agent opening the file in a fresh session with none of the
original context — needs to reconstruct *why* an option was rejected, not just
that it was. Rewriting or deleting earlier discussion destroys that evidence
and invites re-litigating settled ground. So new findings, revised proposals,
and counter-arguments are **appended** (with a date or author marker), leaving
earlier entries intact. The structure is what separates this from a chat log:
it's an append-only log *with sections*.

Think of an RFC as the lab notebook. You don't erase yesterday's failed
experiment; you write today's entry below it.

### RFC Workflow

1. Identify a design question that benefits from structured, durable
   discussion — especially one likely to span sessions or contributors.
2. Draft the RFC from `references/rfc-template.md`: problem, alternatives,
   risks, open questions.
3. As discussion evolves, **append** new viewpoints, findings, and revised
   proposals rather than overwriting earlier ones. Mark substantial additions
   so the chronology stays legible.
4. When the discussion converges, write or update the ADR that records the
   outcome (see below).
5. Mark the RFC `Resolved` in `docs/rfc/index.md` with a link to the ADR. Do
   not delete it — the resolved RFC is the provenance of the decision.

## ADR: The Atomically-Maintained Design Intent

An ADR is the single source of truth for one settled aspect of *how the system
should be designed*. A reader — human or agent — should be able to open it and
get one coherent answer to "what did we decide, and why?" without
reverse-engineering a thread.

**Why edited atomically?** Because an ADR is a *spec*, not a *log*. Its job is
to state current intent cleanly. When the intent changes, you edit the ADR as a
unit so it keeps reading as one clear statement — or, when a decision is
replaced wholesale, you supersede it with a new ADR and link the two. What you
never do is let an ADR decay into a half-current document where the reader has
to guess which paragraph still applies. (This is the opposite discipline from
the RFC, and that contrast is the point: the RFC preserves history; the ADR
preserves clarity.)

Don't churn an ADR for cosmetic reasons — a new template or a reworded sentence
isn't a decision change. Edit it when the *decision itself* moves.

### ADR Workflow

1. Once a decision is settled, check `docs/plans/index.md` for a related ADR.
2. If one already governs this area, **update it in place** to reflect the new
   intent (atomic edit) — don't scatter the truth across two half-valid
   records. If the decision is wholly replaced, write a new ADR and mark the
   old one `superseded` with a link to the replacement.
3. Otherwise, create the next ADR from `references/adr-template.md`.
4. Set status to `accepted`; capture context, decision, and consequences.
5. Reference the ADR from the implementation commits that bring code in line
   with it.

## File Conventions

```text
docs/rfc/rfc-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md     # RFC discussion logs
docs/plans/adr-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md   # ADR design records
```

Maintain `docs/rfc/index.md` and `docs/plans/index.md` sorted by their
respective IDs. The two ID sequences are independent. Never reuse an ID.

## Templates

- RFC: `references/rfc-template.md`
- ADR: `references/adr-template.md`

## ADR Status Values

- `proposed` — drafted, awaiting final sign-off.
- `accepted` — the decision is the current intent.
- `rejected` — considered but intentionally not adopted (kept for the record).
- `deprecated` — no longer intended, with no direct replacement.
- `superseded` — replaced by a later ADR (link the replacement).

## When NOT to Use This Skill

- Narrow typo fixes, prose edits, or mechanical metadata updates — no design
  intent is changing.
- Trivially reversible choices with zero architectural reach.
- Sequencing or tracking the steps that *implement* a decision — that's
  implementation planning (see "What This Skill Does NOT Cover").

## Common Mistakes

- **Rewriting an RFC's history** instead of appending — it erases the reasoning
  trail the RFC exists to preserve.
- **Letting an ADR go half-stale** — leaving two partly-valid records instead
  of atomically updating the one source of truth.
- Treating an ADR as invalid because the code doesn't match yet — the ADR
  states intent; the mismatch *is* the remaining work.
- Treating an RFC as the decision — it's the discussion; the ADR is the
  decision.
- Writing an ADR before the decision is actually settled.
- Recording every micro-decision instead of architecturally significant ones.
- Putting implementation steps or task checkboxes into an ADR — that's
  execution state, which belongs in external memory / a planning skill.
