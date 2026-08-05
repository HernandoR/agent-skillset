# ADR-0009: Multi-Harness Plugin Compatibility (Codex and Pi)

- Status: Accepted
- Date: 2026-08-05

## Context

ADR-0007 packaged the skills as a Claude Code plugin marketplace, and everything
since has assumed Claude Code is the only consumer. It is not: the skill format
this repo already uses is a de-facto cross-harness standard.

Codex documents the identical skill layout — `SKILL.md` with required
`name`/`description` frontmatter, a recommended `agents/openai.yaml` for UI
metadata, and optional `scripts/`, `references/`, `assets/` — and resolves
plugin manifests through
`[".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
".cursor-plugin/plugin.json"]`, so this repo's per-bundle manifests are already
on its search path. Pi defines a skill the same way and discovers skills from
`.pi/skills/`, `.agents/skills/`, a `skills` array in `.pi/settings.json`, or a
package's `pi.skills` manifest entry.

The gap is therefore metadata, not structure. What was missing: the `interface`
block Codex uses to present a plugin, and any Pi-facing manifest at all.
RFC-0008 worked the options through.

## Decision

> In the context of a skill tree whose layout already satisfies three harnesses,
> facing users on Codex and Pi having to hand-wire paths that manifest fields
> would handle,
> we decided for manifest-only compatibility with `plugins/` as the single
> source of truth,
> and against per-harness manifest copies, a second marketplace file, and
> mirroring skills into `.agents/skills/`,
> to achieve installability on all three harnesses with one tree,
> accepting two release-version fields to keep in step and a `category` value
> chosen from an undocumented set.

Concretely:

1. **The skill directory shape is the shared contract.** `SKILL.md` with `name`
   and `description` frontmatter is what all three harnesses load;
   `agents/openai.yaml`, `references/`, `scripts/`, `assets/` match Codex's
   documented layout. No harness-specific skill layout may be introduced.

2. **Codex loads the existing per-bundle manifests.** No
   `.codex-plugin/plugin.json` is added — it would duplicate
   `.claude-plugin/plugin.json`, which Codex already resolves.

3. **Every bundle manifest carries `keywords` and a complete `interface`
   block**: `displayName`, `shortDescription`, `longDescription`,
   `developerName`, `category`, `capabilities`, and `defaultPrompt` (at most 3
   entries, each ≤ 128 characters). Additive; Claude Code ignores it.

4. **Manifests are restricted to Codex's recognised field set**: `name`,
   `version`, `description`, `keywords`, `skills`, `mcpServers`, `apps`,
   `hooks`, `interface`. `author`, `license`, `homepage`, and `repository` are
   excluded — they appear in Codex's sample spec but not in its local
   `RawPluginManifest`, because the sample documents hosted-marketplace
   ingestion. Attribution goes in `interface.developerName`.

5. **Pi consumes the repo as a package.** Root `package.json` carries
   `keywords: ["pi-package", …]` and `pi.skills: ["./plugins/*/skills"]`,
   enabling `packages: ["agent-skillset"]` and the filtered `{source, skills}`
   form. The manual `.pi/settings.json` `skills` array is documented as a
   fallback for vendored checkouts. `package.json` is a manifest only — not an
   npm application, and not published to npm.

6. **The root marketplace file stays Claude-format.** Codex's marketplace schema
   requires object-form `source` plus a `policy` block, which the Claude schema
   does not accept; no second marketplace file is added. Codex users install
   per-bundle.

7. **The constraints are enforced, not documented.** `just validate` checks
   strict semver on every version, non-empty `keywords`, the full `interface`
   schema and `defaultPrompt` limits, absence of non-Codex fields, `pi.skills`
   coverage of every bundle's `skills/` directory, and equality of the
   `marketplace.json` and `package.json` versions.

8. **`category` is `"Productivity"` and `capabilities` are drawn from
   `["Interactive", "Write"]`** — the only values attested in Codex's sample
   manifest, since no enum is published. Deliberately conservative even though
   `"Productivity"` describes these bundles poorly.

Self-application — making this repo's own skills active while developing here —
is explicitly **not** decided by this ADR. Both Codex and Pi would read
`.agents/skills/`, which ADR-0001 forbids as a payload location; resolving that
requires revising ADR-0001.

## Consequences

Easier:

- Codex and Pi users install without hand-wiring paths, and Pi users can pull
  individual skills rather than whole bundles.
- Bundles now present properly in plugin lists on Codex (display name, subtitle,
  starter prompts) instead of showing bare manifest text.
- Cross-harness constraints fail `just validate` instead of surfacing as a
  broken install on a harness nobody tested.

Harder or more expensive:

- Four manifests now carry ~15 lines of presentation metadata each, all of it
  hand-maintained and none of it exercised by the Claude Code path — so drift is
  invisible locally. The validator checks shape, not accuracy.
- Two release versions (`marketplace.json`, `package.json`) must move together.
- A `package.json` in a uv/Python repo reads as an npm project to newcomers.
  Mitigated by a Repository Map note and by gitignoring `node_modules/` and
  `package-lock.json`.
- `category`/`capabilities` are guesses against an undocumented value set and
  may need correcting once Codex publishes an enum.
- Codex is now a supported consumer without any automated verification against
  it — nothing in CI proves a bundle actually loads there.

## References

- [RFC-0008](../rfc/rfc-0008-multi-harness-plugin-compatibility-2026-08-05.md) —
  upstream findings, alternatives, and the three questions settled before
  acceptance.
- [ADR-0007](adr-0007-plugin-manifest-commit-hook-skill-merge-2026-06-20.md) —
  the plugin/marketplace packaging this extends.
- [ADR-0001](adr-0001-initial-skill-layout-2026-05-22.md) — the `.agents/`
  payload prohibition that blocks self-application.
