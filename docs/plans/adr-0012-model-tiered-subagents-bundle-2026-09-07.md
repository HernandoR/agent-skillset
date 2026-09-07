# ADR-0012: Model-Tiered Subagents Bundle

- Status: Accepted
- Date: 2026-09-07

## Context

Three Claude Code subagent definitions lived in the maintainer's user-level
`~/.claude/agents/` directory: `haiku-task` (low-cost mechanical execution),
`opus-dev` (judgment-heavy bounded development), and `fable-review` (read-only
highest-quality review). They encode a delegation policy — pick the model tier
by the judgment a task needs — that is reusable across projects, so they belong
in this distributable tree rather than in one machine's dotfiles.

Every existing bundle is skills-only, and the repo's shared contract across
Claude Code, Codex, Pi, and Agent Plugins clients is the skill directory shape
(ADR-0009, ADR-0011). Subagent definitions are a Claude Code-specific component:
Claude Code auto-discovers `agents/*.md` at a plugin root, while Codex's
manifest loader does not recognise an `agents` field (the validator rejects it)
and Pi and Agent Plugins clients have no equivalent.

## Decision

- **New bundle `subagents`** at `plugins/subagents/`, containing only
  `agents/fable-review.md`, `agents/haiku-task.md`, `agents/opus-dev.md`, copied
  verbatim, plus the usual dual manifests (root Agent Plugins `plugin.json` and
  `.claude-plugin/plugin.json`) and a marketplace entry. Version 0.1.0.
- **Separate bundle, not part of `dev-loop`.** Folding the agents into an
  existing bundle would change that bundle's payload for every installer while
  adding nothing on non-Claude harnesses. A dedicated bundle keeps the agents
  opt-in and leaves the skills-only bundles untouched.
- **No `agents` manifest field.** The `.claude-plugin/plugin.json` stays within
  the Codex-recognised key set; Claude Code finds the default `agents/`
  directory without it. The manifest also omits `skills`, since the bundle has
  no `skills/` directory.
- **Validation.** `scripts/validate_skills.py` now checks every
  `plugins/*/agents/*.md`: parseable frontmatter, `name` equal to the file
  stem, non-empty `description`.
- **Versions.** Marketplace and `package.json` go 0.11.0 → 0.12.0 (minor: new
  bundle).

## Consequences

- Claude Code users install the three agents with
  `claude plugin install subagents@agent-skillset`; they appear under the
  plugin namespace like any plugin agent.
- Codex, Pi, and Agent Plugins clients see an empty bundle. This is documented
  in `README.md` and `AGENTS.md`; adding it there is harmless.
- The repo now has a second component type. New agents follow the
  `agents/<name>.md` shape and bump the bundle version like a skill change.
- The agent prompts reference CodeGraph (`codegraph_explore`); on machines
  without a `.codegraph/` index the agents skip that step as their text
  instructs.
