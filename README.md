# agent-skillset

Reusable agent skills for engineering workflows, distributed as a plugin marketplace. Loadable by **Claude Code**, **Codex**, and **Pi** from the same tree — every skill is a directory with a `SKILL.md` (`name` + `description` frontmatter), an `agents/openai.yaml` interface descriptor, and optional `references/`, `scripts/`, and `assets/`.

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
claude plugin install dev_loop@agent-skillset
claude plugin install fetch_external_knowledge@agent-skillset
```

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

### dev_loop
The full development loop — git workflow, worktrees, Justfile recipes, TDD plans, best practices, and verification before completion. Includes a session-end hook that warns about uncommitted changes.

Skills: `git-workflow-and-versioning`, `using-git-worktrees`, `finishing-a-development-branch`, `justfile-workflow`, `development-best-practices`, `tdd-checkbox-plans`, `verification-before-completion`

### fetch_external_knowledge
Fetch knowledge from outside the repo — code intelligence via Codegraph and current library docs via Context7.

Skills: `codegraph-usage`, `context7-docs-first`
