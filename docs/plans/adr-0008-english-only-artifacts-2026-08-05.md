# ADR-0008: English-Only Written Artifacts

- Status: Accepted
- Date: 2026-08-05

## Context

Sessions with this skillset are often held in Chinese, and the interaction
language has been leaking into committed output: Chinese ADRs, Chinese code
comments, Chinese commit subjects. `AGENTS.md` documented that leak as policy
(`Use Chinese commit subjects for local consistency with the originating
project conventions`), so it was the default rather than an accident.

The cost is borne by readers who are not in the conversation. An artifact's
audience is a future contributor or a fresh agent session sharing neither
today's context nor today's language, and English is the common denominator
across the toolchain. Mixed-language repositories also fragment search — a
convention written in Chinese is invisible to an English `grep`, so agents
re-decide things the repo has already settled — and without a designated
authoritative language, two renderings of the same document both claim to be
current with nothing detecting the fork.

RFC-0007 worked the question through. ADR-0005 had already established that
cross-harness agent rules belong in `AGENTS.md` / `.agents/spec/`, which
determines where this rule lives.

## Decision

> In the context of agents that converse in one language and commit in another,
> facing durable artifacts becoming unreadable and unsearchable for everyone
> outside the original session,
> we decided for a hard split between interaction language and artifact
> language, with English fixed as the artifact language and localized
> renderings attached as transcripts,
> and against per-skill duplication of the rule, a `CLAUDE.md`-only home, and
> letting an explicitly-requested Chinese document stand alone,
> to achieve one searchable source of truth per record,
> accepting that a session held entirely in Chinese produces output its
> participants cannot skim without the attached transcript.

Concretely:

1. **The split.** Interaction language — chat replies, clarifying questions,
   narrated reasoning — follows the user. Artifact language is always English:
   everything under `docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
   changelogs, code comments and docstrings, identifiers, developer-facing
   runtime strings (logs, exceptions, assertion messages, CLI help, config
   keys), commit subjects and bodies, branch names, and PR/issue/review text.
   A request to discuss in Chinese addresses only the first category.

2. **Exclusions.** Deliberately localized product copy (i18n resource bundles,
   user-facing UI strings) is out of scope — there the language is the
   requirement. Verbatim quotes of non-English source text, file content, or
   test fixtures are reproduced as-is and translated alongside, never in place.

3. **Localized renderings attach, they do not replace.** A Chinese rendering is
   either an `## Appendix: 中文译本 (reading transcript)` section in the English
   file or a `<name>.<lang>.md` sibling linking back to it. Both state that
   English wins on disagreement. `index.md` entries, cross-references, and
   `superseded_by` pointers always name the English file. "Write me a Chinese
   ADR" is therefore satisfied by *English ADR + attached Chinese transcript*.
   Only an explicit, artifact-specific instruction can make another language
   authoritative for one file.

4. **Where the rule lives.** A new `english-only-artifacts` skill in the
   `discuss` plugin states it once and ships
   `references/agents-spec/english-only-artifacts.md` as a drop-in conforming
   to ADR-0005's schema. Because skills load independently,
   `decision-grilling` and `adr-driven-development` each carry a
   self-contained `## Language` section rather than only a cross-link — those
   are the two skills where the leak occurs.

5. **This repository adopts it.** `.agents/spec/english-only-artifacts.md`
   plus an `AGENTS.md` mirror section; `scripts/validate_agent_specs.py`
   copied in from the `agent-spec-convention` skill and wired into
   `just validate`. `AGENTS.md`'s Chinese-commit-subject rule is replaced by an
   English one; existing Chinese subjects in history stay as they are.

6. **No automated language detector.** A CJK-codepoint check would have to
   carve out transcripts, i18n bundles, and quoted fixtures, which makes it
   less reliable than the written rule. Revisit only if violations recur.

## Consequences

Easier:

- Any contributor or agent can read and `grep` the whole repository without a
  language barrier, and conventions written down are conventions that get
  found.
- "Should this be in Chinese?" has a mechanical answer, so it stops being
  re-litigated per document.
- The rule travels with the plugin: installing `discuss@agent-skillset` carries
  it into consumer projects, and `references/agents-spec/` makes it a
  three-file adoption there.

Harder or more expensive:

- A Chinese-speaking user who asked for a Chinese document now gets two
  artifacts, and someone has to write the transcript.
- Transcripts can fall behind their English source. Accepted: a stale
  transcript that declares English authoritative is better than a silent fork.
- The rule is stated in four places (skill, two `## Language` sections, spec
  file), so amendments touch four files. Chosen over ten-file duplication and
  over a link-only approach that would break when a skill loads alone.
- `scripts/validate_agent_specs.py` is now a second copy of the skill's
  linter and can drift from it — the same trade-off ADR-0002 and ADR-0004
  already accepted for their shipped specs.
- Commit-subject language changes mid-history, so `git log` reads as mixed.
  Preferred over rewriting history.

## References

- [RFC-0007](../rfc/rfc-0007-english-only-artifacts-2026-08-05.md) — the
  discussion, alternatives, and the two questions settled before acceptance.
- [ADR-0005](adr-0005-agent-spec-convention-2026-06-03.md) — the
  `.agents/spec/` + `AGENTS.md` mirror convention this rule uses.
