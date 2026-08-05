# AGENTS.md

Guidance for AI coding agents working in this skills repository. Human-facing
project documentation should stay in tracked docs; `.agents/` is reserved for
metadata about this repository and its agent-facing rule specs, and must not be
used as the installable skill payload location.

## Project Overview

This repository contains reusable Codex skills. Installable skill packages live
under top-level `skills/<skill-name>/`. Each skill is independent, but related
skills may cross-reference each other.

The repository follows conventions learned from `pcl-rustic`:

- Prefer RFCs (Request for Comments) for proposing and discussing substantive
  design changes. Record settled decisions as ADRs (Architecture Decision
  Records). RFCs live in `docs/rfc/`; ADRs live in `docs/plans/`.
- Use Context7 through a subagent for unknown external APIs or APIs without
  local examples.
- Treat public interfaces as typed contracts.
- Prefer `uv` for Python tooling and `just` for repeatable commands.
- Resolve open design questions before implementation.
- Commit each verified step instead of batching unrelated work.
- Write every durable artifact in English, whatever language the session uses.

## Repository Map

```text
.agents/                  # project metadata and rule specs; not installable skills
.agents/spec/             # agent-facing project rules, mirrored in AGENTS.md
.claude-plugin/           # Claude Code plugin manifest (plugin.json)
docs/plans/               # ADRs (settled decisions)
docs/rfc/                 # RFCs (proposals for discussion)
hooks/                    # hook scripts and hooks.json descriptor
scripts/                  # validation and maintenance scripts
skills/                   # installable skill packages
Justfile                  # repeatable project commands
pyproject.toml            # uv-managed Python tooling metadata
```

## Skill Layout

Each skill must use this shape:

```text
skills/<skill-name>/
  SKILL.md
  agents/openai.yaml
  references/             # optional bundled resources
  scripts/                # optional deterministic helpers
  assets/                 # optional output assets
```

`SKILL.md` frontmatter must include `name` and `description`. The folder name
must match the `name`. Descriptions should describe triggering conditions, not
summarize the workflow.

## Project Rules

Rules live in `.agents/spec/<rule>.md` with a summary mirrored below. Run
`just validate` to check the schema and the mirror.

### English-Only Written Artifacts

Every durable written artifact — documentation, code comments, docstrings,
commit messages, PR text, log and error strings — is written in English,
regardless of the language the conversation is being held in. Interaction
language follows the user; artifact language does not. A localized rendering is
attached to the English original as a labelled reading transcript, and indexes
always link the English file.

Full spec: [.agents/spec/english-only-artifacts.md](.agents/spec/english-only-artifacts.md)

## ADR and RFC Workflow

Propose substantive changes via an RFC and record settled decisions via an ADR.
They live in separate directories:

```text
docs/rfc/rfc-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md
docs/plans/adr-{NNNN}-{kebab-title}-{YYYY-MM-DD}.md
```

Use `skills/adr-driven-development` to draft RFC proposals and to record
settled decisions as ADRs. RFC and ADR IDs are independent sequences.

Each directory has its own `index.md`. Existing records are historical
artifacts; do not update old records only because a newer template exists.

## Commands

Prefer `just` recipes over raw tool commands.

```bash
just validate
just fmt
just ci
```

Python commands in this repo should run through `uv`, for example
`uv run python scripts/validate_skills.py`.

## Git Conventions

- Use short-lived branches when practical.
- Commit each verified logical step.
- Commit subject format: `<type>(<scope>): <subject>`.
- Write commit subjects and bodies in English, per the English-Only Written
  Artifacts rule above. This supersedes the earlier Chinese-subject convention
  inherited from the originating project; existing Chinese subjects in history
  stay as they are.
- Do not skip verification before claiming work is complete.

