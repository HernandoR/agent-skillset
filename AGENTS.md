# AGENTS.md

Guidance for AI coding agents working in this skills repository. Human-facing
project documentation should stay in tracked docs; `.agents/` is reserved for
metadata about this repository and its agent-facing rule specs, and must not be
used as the installable skill payload location.

## Project Overview

This repository distributes reusable agent skills as a plugin marketplace.
Skills are grouped into **bundles** (plugins) under
`plugins/<bundle>/skills/<skill-name>/`; the root `.claude-plugin/marketplace.json`
lists the bundles. Each skill is independent and must stand alone when loaded by
itself, but related skills may cross-reference each other.

Current bundles: `discuss`, `implement`, `dev-loop`, `fetch-external-knowledge`,
`codex-deepseek-subagent`, `reclaim-code-entropy`.

`reclaim-code-entropy` is vendored verbatim from
[Yevanchen/reclaim-code-entropy](https://github.com/Yevanchen/reclaim-code-entropy)
(MIT, commit `491cbff12cdc6988dfb18dec15b2c3bc4db512f1`); its `LICENSE` sits at the
bundle root. Edit it only to re-sync with upstream, and record the new commit in
`README.md` and here when you do.

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
.agents/                             # repo metadata and rule specs; not installable skills
.agents/spec/                        # agent-facing project rules, mirrored in AGENTS.md
.claude-plugin/marketplace.json      # marketplace manifest listing every bundle
plugins/<bundle>/                    # one installable plugin per bundle
  plugin.json                        #   Agent Plugins 1.0.0 portable manifest
  .claude-plugin/plugin.json         #   Claude Code / Codex bundle manifest
  skills/<skill-name>/               #   the bundle's skills
docs/plans/                          # ADRs (settled decisions)
docs/rfc/                            # RFCs (proposals for discussion)
scripts/                             # validation and maintenance scripts
Justfile                             # repeatable project commands
package.json                         # Pi package manifest (pi.skills); not an npm app
pyproject.toml                       # uv-managed Python tooling metadata
```

No bundle ships hooks. Skills state their rules and let the agent apply them;
this repo does not install hooks that edit a user's global configuration or act
on their repository without being asked (ADR-0010). There is no top-level
`skills/` directory — it moved under `plugins/` in ADR-0007.

## Skill Layout

Each skill must use this shape:

```text
plugins/<bundle>/skills/<skill-name>/
  SKILL.md                # required; frontmatter + body
  agents/openai.yaml      # required; interface descriptor for non-Claude harnesses
  references/             # optional bundled resources
  scripts/                # optional deterministic helpers
  assets/                 # optional output assets
```

`SKILL.md` frontmatter must include `name` and `description`. The folder name
must match the `name`. Descriptions should describe triggering conditions, not
summarize the workflow.

`agents/openai.yaml` must define `interface` with `display_name`,
`short_description`, and `default_prompt`. `just validate` enforces both files.

## Harness Compatibility

The tree is consumed by four ecosystems and must stay loadable by all of them.

| Harness | Reads | Notes |
|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` → `plugins/<bundle>/.claude-plugin/plugin.json` | Primary distribution path. |
| Codex | `plugins/<bundle>/.claude-plugin/plugin.json` | Second entry in Codex's manifest search order, so no Codex-specific manifest is needed. |
| Pi | root `package.json` → `pi.skills` glob | Needs the `pi-package` keyword to be gallery-discoverable. |
| Agent Plugins clients | `plugins/<bundle>/plugin.json` + `skills/` | Agent Plugins 1.0.0: root `plugin.json` (`$schema` + `name` required), skills discovered at fixed `skills/`. Inert to Claude Code and Codex (not in their manifest search orders). |

Rules that follow from this:

- **The skill directory shape is the shared contract.** `SKILL.md` with `name`
  and `description` frontmatter is what all three load; `agents/openai.yaml`,
  `references/`, `scripts/`, and `assets/` match Codex's documented layout.
  Do not introduce a harness-specific skill layout.
- **`plugins/` is the single source of truth.** No mirrored or generated skill
  trees per harness — compatibility is achieved with manifests, not copies.
- **Bundle manifests are restricted to fields Codex recognises**: `name`,
  `version`, `description`, `keywords`, `skills`, `mcpServers`, `apps`,
  `hooks`, `interface`. Notably `author`, `license`, `homepage`, and
  `repository` are *not* among them; developer attribution goes in
  `interface.developerName`. `just validate` rejects anything else.
- **`interface` is required on every bundle manifest** with `displayName`,
  `shortDescription`, `longDescription`, `developerName`, `category`, and
  `capabilities`, plus `defaultPrompt` (at most 3 entries, each ≤ 128
  characters).
- **The root marketplace file stays Claude-format.** Codex's marketplace schema
  wants an object-form `source` plus a `policy` block, which the Claude schema
  does not accept. Codex users install per-bundle instead of via a marketplace;
  do not add a second marketplace file.
- **`pi.skills` must cover every bundle.** `just validate` fails if a bundle's
  `skills/` directory is not matched by a glob in `package.json`.
- **Every bundle ships a root `plugin.json` in Agent Plugins 1.0.0 format.**
  The schema is closed: only `$schema`, `name`, `version`, `description`,
  `author`, `homepage`, `repository`, `license`, `keywords`, `extensions` are
  allowed. `$schema` must be
  `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` and `name` must
  match the Agent Plugins pattern (lowercase alnum, hyphen, period; alnum
  start/end; no `--` or `..`).
- **Bundle names are kebab-case and identical everywhere.** The directory
  name, the root `plugin.json` `name`, the `.claude-plugin/plugin.json` `name`,
  and the marketplace entry `name`/`source` must all agree; the root manifest
  `version` must equal the `.claude-plugin` manifest `version`. `just validate`
  enforces these syncs so the package keeps one identity across ecosystems.

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

Use `plugins/discuss/skills/adr-driven-development` to draft RFC proposals and
to record settled decisions as ADRs. RFC and ADR IDs are independent sequences.

Each directory has its own `index.md`. Existing records are historical
artifacts; do not update old records only because a newer template exists.

## Commands

Prefer `just` recipes over raw tool commands.

```bash
just validate   # skill/plugin manifests + .agents/spec schema and AGENTS.md mirror
just fmt        # ruff format scripts
just lint       # ruff check scripts
just ci         # fmt + lint + validate
```

Python commands in this repo should run through `uv`, for example
`uv run python scripts/validate_skills.py`.

## Versioning

Two manifests carry versions, and both are semver:

- `plugins/<bundle>/.claude-plugin/plugin.json` — bump when that bundle's
  payload changes. Minor for a new or removed skill or a behavioural change to
  an existing one; patch for wording, typo, and reference-file fixes.
- `.claude-plugin/marketplace.json` — bump on every published change, taking
  the highest bump among the bundles touched. Patch for repo-level changes that
  ship no bundle payload (this file, `README.md`, `scripts/`, `Justfile`).

The root `package.json` version must equal the marketplace version — it is the
same release, just the Pi-facing manifest. `just validate` enforces this.

Never publish a payload change without a bump: installed copies are resolved by
version, so an unbumped edit does not reach anyone who already installed the
bundle.

## Git Conventions

- Use short-lived branches when practical.
- Commit each verified logical step.
- Commit subject format: `<type>(<scope>): <subject>`.
- Write commit subjects and bodies in English, per the English-Only Written
  Artifacts rule above. This supersedes the earlier Chinese-subject convention
  inherited from the originating project; existing Chinese subjects in history
  stay as they are.
- Do not skip verification before claiming work is complete.

