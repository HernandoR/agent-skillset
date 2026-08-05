<!-- Drop into target project as `.agents/spec/english-only-artifacts.md`
     (remove this comment so the frontmatter starts at line 1). -->

---
name: english-only-artifacts
version: 1
last_updated: 2026-08-05
---

# English-Only Written Artifacts

## Rule

Every durable written artifact — documentation, code comments, docstrings,
commit messages, PR text, log and error strings — is written in English,
regardless of the language the conversation is being held in.

Interaction language and artifact language are independent: replies, questions,
and reasoning follow the user, while anything committed, saved, or pushed stays
English. A request to discuss in another language never changes the artifact
language.

When a non-English document is asked for, the English version remains
authoritative and the other language is attached to it as a labelled reading
transcript — an appendix in the same file, or a `.<lang>.md` sibling that links
back. Indexes and cross-references always point at the English file. Only an
explicit, artifact-specific instruction can make another language authoritative
for a given file.

## Why

Artifacts outlive the conversation that produced them: the next reader is a
future contributor or a fresh agent session with no shared language and none of
today's context, and English is the common denominator across the toolchain.
Mixed-language repositories also fragment search — a rule written in Chinese is
invisible to an English `grep`, and a half-translated document leaves two
half-truths where there should be one source of truth. Pinning one
authoritative language keeps translation drift visible and cheap to fix instead
of silently forking the meaning.

## Where

Applies to: everything under `docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
changelogs, code comments and docstrings, identifiers, developer-facing runtime
strings (logs, exceptions, assertion messages, CLI help, config keys), commit
subjects and bodies, branch names, and PR/issue/review text.

Does not apply to:

- Chat replies, clarifying questions, and narrated reasoning — these follow the
  user's language.
- Deliberately localized product copy: i18n resource bundles and user-facing UI
  strings, where the language is the requirement rather than agent prose.
- Verbatim quotes of non-English source text, existing file content, or test
  fixtures — reproduce as-is and translate alongside, never in place.
- `*.<lang>.md` transcript files and `## Appendix: … (reading transcript)`
  sections, which exist precisely to carry the translation.

## Examples

```python
# BAD: Chinese comment and log string in committed code
def process(item):
    # 处理单个条目并写入缓存
    logger.info("开始处理 {}", item)
```

```python
# GOOD: English comment and log string, whatever language the chat used
def process(item):
    # Process a single item and write it to the cache.
    logger.info("Processing {}", item)
```

```text
# BAD: Chinese-only ADR, no English source of truth
docs/plans/adr-0012-缓存策略-2026-08-05.md

# BAD: English file exists but the index points at the translation
| [ADR-0012](adr-0012-cache-strategy-2026-08-05.zh-CN.md) | 缓存策略 | Accepted |

# GOOD: English authoritative, transcript attached, index points at English
docs/plans/adr-0012-cache-strategy-2026-08-05.md
docs/plans/adr-0012-cache-strategy-2026-08-05.zh-CN.md
| [ADR-0012](adr-0012-cache-strategy-2026-08-05.md) | Cache Strategy | Accepted |
```

```text
# BAD: commit subject in Chinese
feat(cache): 添加分层缓存策略

# GOOD: commit subject in English
feat(cache): add tiered cache strategy
```

## References

- The `english-only-artifacts` skill — full rationale, transcript shapes, and
  the artifact/interaction boundary.
- The `agent-spec-convention` skill — schema this file conforms to, plus
  `validate_agent_specs.py`.
