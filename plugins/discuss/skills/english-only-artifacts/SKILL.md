---
name: english-only-artifacts
description: Use whenever writing something that persists — docs, RFCs, ADRs, plans, specs, code comments, docstrings, identifiers, log and error strings, commit subjects, PR and issue text. Load it especially when the conversation is being held in Chinese or another non-English language, when the user asks for the discussion in that language, or when a Chinese/localized document is requested. Prevents the interaction language from leaking into durable artifacts.
---

# English-Only Written Artifacts

## The Rule

Every durable written artifact — documentation, code comments, docstrings,
commit messages, PR text, log and error strings — is written in English,
regardless of the language the conversation is being held in.

Two languages are in play in any session, and they are **independent**:

| | Language |
|---|---|
| **Interaction** — chat replies, questions, spoken reasoning | Follows the user |
| **Artifacts** — anything committed, saved, or pushed | Always English |

A request to talk in Chinese is a request about the *first* row only. It never
changes the second. "用中文讨论" means reply in Chinese and keep writing the ADR
in English.

## When A Non-English Document Is Asked For

English stays the source of truth. The other language is **attached to** the
English version as a clearly-labelled reading transcript — never a
replacement, never the only copy, and never the version other artifacts link
to.

Two acceptable shapes:

```markdown
<!-- Shape A: appended appendix, single file -->
## Appendix: 中文译本 (reading transcript)

> Transcript of the English text above, for reading convenience. The English
> version is authoritative; where the two disagree, the English text wins.
```

```text
# Shape B: sibling file with a language suffix
docs/plans/adr-0008-english-only-artifacts-2026-08-05.md          # authoritative
docs/plans/adr-0008-english-only-artifacts-2026-08-05.zh-CN.md    # transcript
```

Shape B's transcript opens with a link back to the English file and the same
authoritative-version note. Indexes, cross-references, and `superseded_by`
pointers always name the English file.

So "write me a Chinese ADR" is satisfied by *English ADR + attached Chinese
transcript*, not by a Chinese ADR. The only thing that overrides this is an
explicit, artifact-specific instruction making another language authoritative
for that one file.

## What Counts As An Artifact

Always English:

- Markdown under `docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md`, RFCs, ADRs,
  plans, specs, changelogs.
- Code comments, docstrings, type-stub annotations, TODO/FIXME notes.
- Identifiers: modules, functions, variables, fixtures, test names.
- Runtime strings a developer reads: log messages, exception text, assertion
  messages, CLI `--help` text, config keys and their comments.
- Commit subjects and bodies, branch names, PR and issue titles and
  descriptions, code-review comments.

Follows the user's language instead:

- Chat replies, clarifying questions, decision-grilling prompts, and any
  narration of your reasoning.
- Deliberately localized product copy — i18n resource bundles, user-facing UI
  strings, translated marketing content. That is product content whose
  language *is* the requirement, not agent prose.
- Verbatim quotes. Non-English source text, existing file content, and test
  fixtures are reproduced as-is; translate in a parenthetical or footnote if
  the meaning matters, but never silently rewrite the quote.

## Why

- **Artifacts outlive the conversation.** The reader is a future contributor
  or a fresh agent session with no shared language and none of today's
  context. English is the common denominator across the toolchain.
- **Mixed-language repos fragment search.** A rule written in Chinese is
  invisible to an English `grep`, and a half-translated doc leaves two
  half-truths where there should be one source of truth.
- **Translations drift.** Pinning one authoritative language and attaching the
  transcript keeps drift visible and cheap to fix, instead of silently forking
  the meaning across two files that both claim to be current.

## Portable Project Rule

To make this binding on a project rather than on one session, drop
[references/agents-spec/english-only-artifacts.md](references/agents-spec/english-only-artifacts.md)
into the project's `.agents/spec/` and mirror it in `AGENTS.md`. See the
`agent-spec-convention` skill for the schema and its linter.

## Common Mistakes

- Answering in Chinese and then writing the RFC in Chinese too, because the
  session "is in Chinese".
- Treating "write a Chinese doc" as permission to skip the English version,
  leaving the transcript as the only copy.
- Linking the transcript from `index.md` instead of the English original.
- English prose with Chinese code comments, log strings, or commit subjects —
  the rule covers the whole artifact, not just its paragraphs.
- Translating a quoted non-English error message or fixture and presenting it
  as the original.

## Related Skills

- `agent-spec-convention` — schema and linter for making this a project rule.
- `decision-grilling` — the discussion may be in any language; its written
  output is not.
- `adr-driven-development` — RFCs and ADRs are artifacts, so always English.
