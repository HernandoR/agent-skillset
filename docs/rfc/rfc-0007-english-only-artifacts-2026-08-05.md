# RFC-0007: English-Only Written Artifacts

- Status: Resolved → [ADR-0008](../plans/adr-0008-english-only-artifacts-2026-08-05.md)
- Date: 2026-08-05
- Owners: HernandoR

## Summary

Separate *interaction language* from *artifact language* across the skillset.
Agents reply in whatever language the user is using, but every durable artifact
— docs, RFCs, ADRs, code comments, docstrings, developer-facing runtime
strings, commit subjects, PR text — is written in English. When a localized
rendering is wanted, English stays authoritative and the translation is
attached as a labelled reading transcript rather than replacing the original.

## Motivation

Sessions are frequently held in Chinese, and the interaction language leaks
into what gets committed: Chinese ADRs, Chinese code comments, Chinese commit
subjects. Three failure modes follow.

- **The reader is not the speaker.** Artifacts are read by a future
  contributor or a fresh agent session that shares neither today's context nor
  today's language. English is the common denominator across the toolchain.
- **Search fragments.** A rule written in Chinese is invisible to an English
  `grep`, so agents fail to find conventions that do exist. Half-translated
  documents leave two half-truths where the repo should have one source of
  truth.
- **Translations drift silently.** Without a designated authoritative
  language, two files both claim to be current and nothing detects the fork.

Nothing in the skillset states the rule today, and `AGENTS.md` actively pushed
the other way (`Use Chinese commit subjects for local consistency`), so the
leak is the documented default rather than an accident.

## Goals

- State the interaction-vs-artifact split once, in a form any harness loads.
- Make the rule reachable from the two skills where the leak actually happens:
  `decision-grilling` (discussion) and `adr-driven-development` (records).
- Define a concrete, checkable shape for localized renderings so "write me a
  Chinese doc" has an unambiguous answer.
- Apply the rule to this repository, not just to consumers of the skillset.

## Non-Goals

- Rewriting existing Chinese commit subjects or documents in history. History
  is a historical artifact; the rule is forward-looking.
- Constraining deliberately localized product copy (i18n resource bundles,
  user-facing UI strings). There the language *is* the requirement.
- Machine-translating quoted non-English source text, error messages, or test
  fixtures. Those are reproduced verbatim.
- Any automated enforcement beyond the existing `.agents/spec` schema linter —
  no CJK-codepoint detector is proposed.

## Proposal

1. New skill `plugins/discuss/skills/english-only-artifacts/` stating the rule,
   the artifact inventory, the exclusions, and the transcript shapes. It ships
   `references/agents-spec/english-only-artifacts.md`, a drop-in spec
   conforming to `agent-spec-convention`'s schema.
2. Self-contained `## Language` sections added to
   `plugins/discuss/skills/decision-grilling/SKILL.md` and
   `plugins/discuss/skills/adr-driven-development/SKILL.md`. Each skill loads
   independently, so each restates the rule rather than only linking to it.
3. Transcript shapes, either of:
   - `## Appendix: 中文译本 (reading transcript)` appended to the English file;
   - a `<name>.<lang>.md` sibling that links back to the English original.

   Both carry an "English is authoritative" note, and `index.md`,
   cross-references, and `superseded_by` pointers always name the English file.
4. This repository adopts the rule: `.agents/spec/english-only-artifacts.md`
   plus an `AGENTS.md` mirror section, with
   `scripts/validate_agent_specs.py` copied in and wired into `just validate`.
5. `AGENTS.md`'s Chinese-commit-subject convention is replaced by an English
   one, noting that it supersedes the inherited convention.

## Alternatives Considered

| Alternative | Why Not |
|---|---|
| Add the rule only to `decision-grilling` and `adr-driven-development` | Code comments, log strings, and commit subjects are written under the `implement` and `dev_loop` skills, which those two never reach. The leak would persist everywhere except RFCs. |
| Add a `## Language` section to every artifact-producing skill (~10 files) | Duplicates the full rule text ten times; each future amendment becomes a ten-file change with drift risk. The shared skill plus two targeted mirrors gets the coverage at a tenth of the maintenance. |
| Put the rule in `CLAUDE.md` only | Not loaded by Codex, Cursor, or Kiro. ADR-0005 already rejected harness-pinned rule locations. |
| Allow a Chinese document to stand alone when explicitly requested | Reintroduces the two-sources-of-truth problem the rule exists to prevent, and the request is almost always about readability rather than authority. Transcript-attachment satisfies the readability need without forking the record. |
| Enforce with a CJK-codepoint pre-commit hook | Too blunt: transcripts, i18n bundles, and quoted fixtures are all legitimate CJK. A detector with that many carve-outs is worse than the written rule. Revisit if violations recur. |

## Risks

- **Rule ignored because it lives in a skill that never loads.** Mitigated by
  the two inline `## Language` sections and the `AGENTS.md` mirror, which load
  unconditionally in this repo.
- **Transcript rot** — the Chinese transcript falls behind the English source.
  Mitigated by the authoritative-version note; accepted otherwise, since a
  stale transcript that says so is strictly better than a stale fork that
  doesn't.
- **Copying `validate_agent_specs.py` forks it from the skill's copy.** Same
  trade-off already accepted for the other spec-shipping skills; the linter is
  stdlib-only and stable.

## Open Questions

Both were raised and settled on 2026-08-05 before acceptance:

- Should the rule be a shared skill, two targeted edits, or a section in every
  skill? **Resolved:** shared skill plus the two named skills, and applied to
  this repo's own `AGENTS.md`.
- Does the rule override `AGENTS.md`'s Chinese-commit-subject convention?
  **Resolved:** yes. Commit messages are durable artifacts read by other
  contributors, and history is already mixed.

## Acceptance Criteria

- [x] `plugins/discuss/skills/english-only-artifacts/` exists with `SKILL.md`,
      `agents/openai.yaml`, and the drop-in `references/agents-spec/` file.
- [x] `decision-grilling` and `adr-driven-development` each carry a
      self-contained `## Language` section.
- [x] `.agents/spec/english-only-artifacts.md` exists and `AGENTS.md` mirrors
      it.
- [x] `AGENTS.md` no longer mandates Chinese commit subjects.
- [x] `just validate` passes, including the mirror check.

## Rollout

Single branch, one commit per step: RFC → skill → skill-level `## Language`
sections → repository adoption (spec, mirror, linter) → ADR. No migration:
existing Chinese records and commit subjects are left alone, and the rule
applies to artifacts written from acceptance onward.
