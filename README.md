# agent-skillset

Reusable agent skills for engineering workflows, distributed as a plugin marketplace. Loadable by **Claude Code**, **Codex**, **Pi**, and any **Agent Plugins** client from the same tree — every skill is a directory with a `SKILL.md` (`name` + `description` frontmatter), an `agents/openai.yaml` interface descriptor, and optional `references/`, `scripts/`, and `assets/`.

## Installation

### Claude Code

Add the marketplace once:

```
hernandor/agent-skillset
```

Then install the bundles you need:

```
claude plugin install discuss@agent-skillset
claude plugin install implement@agent-skillset
claude plugin install dev-loop@agent-skillset
claude plugin install fetch-external-knowledge@agent-skillset
claude plugin install codex-deepseek-subagent@agent-skillset
claude plugin install reclaim-code-entropy@agent-skillset
claude plugin install explain-diff@agent-skillset
```

### Agent Plugins

Each bundle under `plugins/` is a standalone Agent Plugins 1.0.0 package: a
root `plugin.json` manifest (`$schema` + `name` required, closed schema) with
skills discovered from its `skills/` directory. Point any conformant
Agent Plugins client at a bundle root — `plugins/discuss`, `plugins/implement`,
`plugins/dev-loop`, `plugins/fetch-external-knowledge`,
`plugins/codex-deepseek-subagent`, `plugins/reclaim-code-entropy`,
`plugins/explain-diff` — and it loads the bundle's skills.

### Codex

Codex discovers plugin manifests at `.codex-plugin/plugin.json`, then `.claude-plugin/plugin.json`, then `.cursor-plugin/plugin.json` — so each bundle under `plugins/` loads as-is, no Codex-specific manifest required. Point Codex at a bundle root (`plugins/discuss`, `plugins/implement`, …) and its `skills/` directory is scanned recursively for `SKILL.md`.

To enable or disable individual skills, use `config.toml`:

```toml
[[skills.config]]
name = "decision-grilling"
enabled = true
```

### Pi

The repo is a Pi package — `package.json` carries the `pi-package` keyword and a `pi.skills` glob covering every bundle. Add it to your `.pi/settings.json`:

```json
{
  "packages": ["agent-skillset"]
}
```

Or load specific skills only:

```json
{
  "packages": [
    { "source": "agent-skillset", "skills": ["decision-grilling", "adr-driven-development"] }
  ]
}
```

If you vendor the repo instead of installing it, point at the skill roots directly:

```json
{
  "skills": ["../agent-skillset/plugins/discuss/skills"]
}
```

## Bundles

### discuss
Design-time reasoning — ADRs, RFCs, agent spec conventions, decision grilling, and the English-only artifact rule.

Skills: `adr-driven-development`, `agent-spec-convention`, `decision-grilling`, `english-only-artifacts`

### implement
Python project tooling — uv workflows, pydantic config trees, loguru logging, typed interfaces, and centralized path config.

Skills: `uv-python-workflow`, `pydantic-config-tree`, `loguru-first-logging`, `typed-interfaces`, `centralized-path-config`

### dev-loop
The full development loop — git workflow, worktrees, Justfile recipes, TDD plans, best practices, and verification before completion.

Skills: `git-workflow-and-versioning`, `using-git-worktrees`, `finishing-a-development-branch`, `justfile-workflow`, `development-best-practices`, `tdd-checkbox-plans`, `verification-before-completion`

### fetch-external-knowledge
Fetch knowledge from outside the repo — code intelligence via Codegraph and current library docs via Context7.

Skills: `codegraph-usage`, `context7-docs-first`

### codex-deepseek-subagent
Offline installer for the DeepSeek V4 Flash custom subagent for Codex.

Skills: `install-codex-deepseek-subagent`

### reclaim-code-entropy
Evidence-first simplification — establish the public, persisted, generated, and dynamic contract, survey entropy, prove each cut against its real consumer graph, then apply one cut with proportional verification. Audit mode ranks candidates without editing.

Skills: `reclaim-code-entropy`

Vendored verbatim from [Yevanchen/reclaim-code-entropy](https://github.com/Yevanchen/reclaim-code-entropy) at commit `491cbff12cdc6988dfb18dec15b2c3bc4db512f1`, MIT — see `plugins/reclaim-code-entropy/LICENSE`.

### explain-diff
Turn a diff, commit range, branch, or PR into a teaching artifact — two-tier background, the core intuition worked through toy data, a grouped code walkthrough, and a five-question quiz with per-option feedback. Pick the skill by output format.

Skills: `explain-diff-html` (single self-contained HTML file), `explain-diff-myst` (MyST Markdown with mermaid diagrams, admonitions, and dropdown answers)

Adapted from Geoffrey Litt's [explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524); the Notion variant was retargeted to MyST Markdown.
