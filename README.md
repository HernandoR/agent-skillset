# agent-skillset

Reusable Claude Code skills for engineering workflows, distributed as a plugin marketplace.

## Installation

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
