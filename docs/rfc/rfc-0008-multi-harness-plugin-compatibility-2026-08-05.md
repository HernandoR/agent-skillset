# RFC-0008: Multi-Harness Plugin Compatibility (Codex and Pi)

- Status: Resolved → [ADR-0009](../plans/adr-0009-multi-harness-plugin-compatibility-2026-08-05.md)
- Date: 2026-08-05
- Owners: HernandoR

## Summary

Make the bundles installable by OpenAI Codex and by Pi (`earendil-works/pi`) in
addition to Claude Code, without forking the skill tree. Achieved with manifest
metadata only: enrich each bundle's `plugin.json` with the fields Codex reads,
and add a root `package.json` carrying Pi's `pi.skills` manifest. `plugins/`
stays the single source of truth.

## Motivation

The repo is written as if Claude Code were the only consumer, yet the skill
format is already a de-facto cross-harness standard. Investigation of both
upstreams found far more convergence than expected:

- **Codex** (`codex-rs/skills/.../skill-creator/SKILL.md`) documents exactly
  this layout: `SKILL.md` with required `name`/`description` frontmatter,
  a recommended `agents/openai.yaml` for UI metadata, and optional `scripts/`,
  `references/`, `assets/`. That is byte-for-byte what this repo already ships
  — `agents/openai.yaml` exists here for precisely this reason.
- **Codex** further discovers plugin manifests at
  `DISCOVERABLE_PLUGIN_MANIFEST_PATHS = [".codex-plugin/plugin.json",
  ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"]`. The per-bundle
  manifests here already sit at the second path.
- **Pi** (`packages/coding-agent/docs/skills.md`) defines a skill as a
  directory containing `SKILL.md` with `name`/`description` frontmatter, and
  discovers skills from `.pi/skills/`, `.agents/skills/`, a `skills` array in
  `.pi/settings.json`, or a package's `pi.skills` manifest entry.

So compatibility is nearly free, and the cost of *not* claiming it is that
users on two other harnesses have to hand-wire paths that a few manifest fields
would have handled.

## Goals

- Codex loads any bundle with no Codex-specific manifest file.
- Pi installs the repo as a package, with per-skill filtering available.
- One skill tree. No generated mirrors, no per-harness copies.
- `just validate` enforces the cross-harness constraints so they cannot rot.

## Non-Goals

- Self-application: making this repo's own skills active while developing here
  (both Codex and Pi would read `.agents/skills/`, which ADR-0001 forbids as a
  payload location). Deferred — it needs its own ADR revision.
- Cursor support, despite `.cursor-plugin/plugin.json` appearing in Codex's
  search order. Not requested and not investigated.
- Publishing to npm. `package.json` exists as a Pi manifest; git-source install
  is sufficient.
- Pi *extensions* (`.pi/extensions/`), which are executable plugins rather than
  skills, and have no analogue here.

## Proposal

1. **Codex `interface` metadata.** Add `keywords` and an `interface` block to
   each `plugins/<bundle>/.claude-plugin/plugin.json`: `displayName`,
   `shortDescription`, `longDescription`, `developerName`, `category`,
   `capabilities`, `defaultPrompt`. Additive; Claude Code ignores it.
2. **Restrict manifests to Codex-recognised fields.** Codex's
   `RawPluginManifest` accepts only `name`, `version`, `description`,
   `keywords`, `skills`, `mcpServers`, `apps`, `hooks`, `interface`. Notably
   `author`, `license`, `homepage`, `repository` are absent even though Codex's
   own sample `plugin-json-spec.md` shows them — the sample documents the
   hosted-marketplace ingestion schema, not the local loader. Ship only the
   intersection and have the validator reject the rest.
3. **Pi package manifest.** Root `package.json` with
   `keywords: ["pi-package", …]` and `pi.skills: ["./plugins/*/skills"]`
   (Pi supports globs). Enables `packages: ["agent-skillset"]` and the filtered
   `{source, skills}` form.
4. **Validator coverage.** Extend `scripts/validate_skills.py` with: strict
   semver on every manifest version, required non-empty `keywords`, the full
   `interface` schema including `defaultPrompt` limits (≤ 3 entries, ≤ 128
   chars each), rejection of non-Codex top-level fields, a check that
   `pi.skills` globs cover every bundle's `skills/` directory, and equality
   between the `marketplace.json` and `package.json` versions.
5. **Docs.** A Harness Compatibility table in `AGENTS.md` with the rules that
   follow from it; per-harness install sections in `README.md`.

## Alternatives Considered

| Alternative | Why Not |
|---|---|
| Add `.codex-plugin/plugin.json` per bundle | Redundant. Codex already resolves `.claude-plugin/plugin.json`, so this would be a second copy of the same manifest to keep in sync for zero gain. |
| Add a second, Codex-format marketplace file | Codex wants object-form `source` (`{source: "local", path: …}`) plus a `policy` block; Claude wants a plain string `source`. One file cannot satisfy both, and two files listing the same four bundles will drift. Per-bundle install covers the need. |
| Mirror or symlink skills into `.agents/skills/` | Both Codex and Pi would auto-discover it, but ADR-0001 forbids `.agents/` as a payload location, and a mirror reintroduces the two-sources-of-truth problem. Out of scope here (see Non-Goals). |
| Document `.pi/settings.json` paths instead of shipping `package.json` | No package install, no gallery listing, and every consumer wires paths by hand. Kept as a documented fallback for vendored checkouts, not as the primary path. |
| Set `private: true` on `package.json` | Would foreclose npm distribution later for no present benefit. |

## Risks

- **`category` and `capabilities` value sets are undocumented.** Codex's spec
  names the fields but publishes no enum; the only attested values are
  `"Productivity"` and `["Interactive", "Write"]` from the sample manifest.
  Using those verbatim is the conservative choice, at the cost of a category
  that describes these bundles poorly. Revisit when an enum is published.
- **Claude Code may not recognise `interface`.** Unknown manifest keys are
  expected to be ignored, but if Claude's schema tightens, `interface` would
  need relocating. Mitigated by `just validate` pinning the field set, so a
  break surfaces as a test failure rather than a silent install error.
- **A root `package.json` in a uv/Python repo invites confusion** — it looks
  like an npm project. Mitigated by an explicit note in the Repository Map and
  by gitignoring `node_modules/` and `package-lock.json`.
- **Two version fields to keep in step.** Enforced by the validator rather than
  by discipline.

## Open Questions

Settled on 2026-08-05 before acceptance:

- Publish-side compatibility only, or also self-apply this repo's skills?
  **Resolved:** publish-side only.
- How should Pi consume the bundles? **Resolved:** root `package.json` `pi`
  manifest, with the manual `.pi/settings.json` path documented as a fallback.
- Add a Codex-format marketplace file? **Resolved:** no — per-bundle manifests
  plus enriched `interface` metadata.

## Acceptance Criteria

- [x] Every bundle manifest carries `keywords` and a complete `interface` block.
- [x] No bundle manifest contains a field outside Codex's recognised set.
- [x] Root `package.json` exists with the `pi-package` keyword and a
      `pi.skills` glob covering all four bundles.
- [x] `just validate` fails when `interface` is missing, a version is not
      semver, an unrecognised field is present, `pi.skills` misses a bundle, or
      the two release versions disagree. Verified by mutation.
- [x] `README.md` documents Claude Code, Codex, and Pi installation.
- [x] `AGENTS.md` carries the Harness Compatibility table and its rules.

## Rollout

One commit per step on the existing branch: manifests → Pi package → validator
→ docs → ADR. All four bundles take a minor bump (additive manifest surface),
marketplace and `package.json` go to 0.3.0. No consumer migration: existing
Claude Code installs see only new, ignored metadata.
