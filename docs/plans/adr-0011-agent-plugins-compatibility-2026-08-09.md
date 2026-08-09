# ADR-0011: Agent Plugins Compatibility

- Status: Accepted
- Date: 2026-08-09

## Context

The repository distributes five skill bundles that must stay loadable by Claude
Code, Codex, and Pi from one tree (ADR-0009). A fourth ecosystem appeared:
[agent-plugins.org](https://agent-plugins.org/), an open, vendor-neutral 1.0.0
specification for portable plugin packages, backed by maintainers from Amazon,
Cursor, Microsoft, OpenAI, and Vercel. Its clients discover skills from a fixed
`skills/` directory and read a portable manifest from root `plugin.json` with a
closed top-level schema (`$schema`, `name`, `version`, `description`, `author`,
`homepage`, `repository`, `license`, `keywords`, `extensions`).

Two incompatibilities stood between the repo and that spec:

1. **Manifest location and shape.** Claude Code and Codex read
   `.claude-plugin/plugin.json` (verified: Codex's
   `DISCOVERABLE_PLUGIN_MANIFEST_PATHS` is `.codex-plugin/plugin.json`,
   `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`; root
   `plugin.json` is not in either harness's search order). Agent Plugins
   requires root `plugin.json` with `$schema`. One file cannot serve both.
2. **Bundle names.** The Agent Plugins name pattern rejects underscores
   (`^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$`). Three bundles —
   `dev_loop`, `fetch_external_knowledge`, `codex_deepseek_subagent` — violated
   it, and also Claude Code's documented kebab-case marketplace identifier.

The Agent Skills spec (agentskills.io) already aligned with the repo's skill
layout: `SKILL.md` at the skill root with `name`/`description` frontmatter,
optional `scripts/`/`references/`/`assets/`, and frontmatter `name` matching the
parent directory. No skill changes were needed.

## Decision

Every bundle directory under `plugins/` is now a standalone Agent Plugins
1.0.0 package, in addition to being a Claude/Codex plugin and a Pi skill root:

- **Dual manifests per bundle.** `.claude-plugin/plugin.json` remains the
  Claude Code / Codex manifest. A new root `plugin.json` carries the portable
  Agent Plugins manifest: `$schema` pointing at
  `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, plus `name`,
  `version`, `description`, `author`, `homepage`, `repository`, `keywords`.
  `license` is omitted (the repo declares no license file).
- **Kebab-case bundle names, adopted directly.** `dev_loop` → `dev-loop`,
  `fetch_external_knowledge` → `fetch-external-knowledge`,
  `codex_deepseek_subagent` → `codex-deepseek-subagent`, applied to the
  directory, the `.claude-plugin/plugin.json` `name`, the root `plugin.json`
  `name`, and the marketplace entry `name` + `source`. The rename is a breaking
  change for installed Claude marketplace users (skill namespace
  `/dev_loop:…` → `/dev-loop:…`); it ships as a plain rename with version bumps,
  **without** a marketplace `renames` migration map — breaking changes are
  acceptable and the old identifiers are not aliased.
- **Version bumps.** Every bundle gained a payload change (new root
  `plugin.json`, renames), so each bundle bumps minor: discuss 0.3.0→0.4.0,
  implement 0.2.0→0.3.0, dev-loop 0.3.0→0.4.0, fetch-external-knowledge
  0.2.0→0.3.0, codex-deepseek-subagent 0.3.0→0.4.0. Marketplace and
  `package.json` go 0.7.0→0.8.0 (highest bundle bump).
- **Validation.** `scripts/validate_skills.py` now checks each root
  `plugin.json` against the Agent Plugins closed schema (allowed fields,
  `$schema` value, name pattern, strict semver, author shape, keywords) and
  enforces identity sync: root manifest `name`/`version` must equal
  `.claude-plugin/plugin.json` `name`/`version`, and each marketplace entry
  `name` must equal its bundle manifest `name`.

No `mcp.json` is shipped (the bundles have no MCP servers; a missing fixed
location is not an error under the spec).

## Consequences

- Each bundle loads in any conformant Agent Plugins client (skills discovered
  from `skills/`), in Claude Code via the marketplace, in Codex via
  `.claude-plugin/plugin.json`, and in Pi via the `package.json` glob — one
  tree, four ecosystems.
- The root `plugin.json` is inert to Claude Code and Codex (not in their
  manifest search orders), so dual manifests add no shadowing risk.
- Two manifests per bundle must stay in sync; the validator enforces
  `name`/`version` equality and will fail CI on drift. `description`,
  `author`, and `keywords` are intentionally not cross-checked to avoid
  coupling presentation metadata between ecosystems.
- Installed Claude marketplace users of the three renamed bundles see their
  plugin namespace change (`dev_loop` → `dev-loop`, etc.) and must re-install
  or accept the new identifier; no migration alias is provided.
- The repo now tracks two manifest schemas (Codex's and Agent Plugins'), each
  with a closed field set. New bundle-level fields must be added to both
  manifests and to the validator's allowlists, or CI fails.
