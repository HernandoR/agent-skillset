# ADR-0016: Four Subagent Tiers

- Status: Accepted
- Date: 2026-10-23
- Amends: [ADR-0012](adr-0012-model-tiered-subagents-bundle-2026-09-07.md) (the agent set only; the bundle shape stays)

## Context

ADR-0012 shipped three agents: `haiku-task`, `opus-dev`, and `fable-review`.
In use, `opus-dev` received two different kinds of work:

- **Well-specified work.** The parent agent already knows what to change: the
  files, the expected behavior, and the verification. The subagent only has to
  implement it correctly. Opus is more expensive than this work needs.
- **Open-ended work.** The parent agent knows the goal but not the change: the
  subagent must find a root cause or choose between approaches. This work
  needs more reasoning effort than `opus-dev` declared (`medium`).

`fable-review` was the only agent on the most expensive model. Its cost limited
how often the parent agent asked for a review.

## Decision

The bundle ships four agents. The parent agent selects an agent by one
question: **who decides what to change?**

| Agent | Model / effort | Use when |
|---|---|---|
| `haiku-task` | haiku / low | No decision is needed: an explicit checklist, a rename, or a command to run and summarize. Unchanged. |
| `sonnet-dev` | sonnet / medium | The parent decided what to change. The task states the files or area, the expected behavior, and the verification. The agent stops and reports when the specification needs a design decision. Replaces `opus-dev`. |
| `opus-highlevel-dev` | opus / high | The parent knows the goal, not the change. The agent finds the cause or chooses the approach, then implements it. It stops before it changes a public interface, a data format, or a recorded design decision. New. |
| `opus-review` | opus / high | Read-only review: bug hunting, plan review, and verification of other agents' output. Replaces `fable-review`. |

- `opus-dev` and `fable-review` are removed without aliases. A caller that
  names them gets an unknown-agent error and must change to the new name.
- The bundle goes 0.2.0 → 0.3.0 (minor: agents added and removed). The
  marketplace and `package.json` go 0.15.0 → 0.16.0.

## Consequences

- Most delegated implementation moves from opus to sonnet, which costs less.
- Open-ended development gets `high` effort, and review becomes less expensive,
  so the parent agent can ask for review more often.
- No agent uses fable. A review that needs the highest model is done by the
  parent session or by an explicit `model` override on the `Agent` call.
- Instruction files that name the old agents (for example a user's shared
  `AGENTS.md`) must change to the new names.
