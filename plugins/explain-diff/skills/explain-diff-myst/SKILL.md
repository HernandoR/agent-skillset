---
name: explain-diff-myst
description: Use when asked to explain a code change, diff, commit range, branch, or PR to a human reader as a MyST Markdown document with mermaid diagrams, callouts, and a dropdown-based quiz. Trigger on "explain this diff/PR/branch", "write up this change", "onboarding doc for this change", or a request for a rendered/publishable Markdown explanation. Not for writing commit messages, PR descriptions, changelogs, or release notes, and not for reviewing a change for defects.
---

# Explain Diff (MyST)

Produce one MyST Markdown document that teaches a reader the change: what the
system did before, the essential idea of the change, a walkthrough of the code,
and a quiz that checks comprehension. The reader may know nothing about this
codebase, so the document must carry its own background.

## Establish The Change And Its Context

1. Resolve exactly what to explain. If the user named a branch, PR, commit, or
   range, use it; otherwise ask which change, or use the working tree diff when
   that is unambiguous. Record the resolved ref in the frontmatter.
2. Read the full diff, then read the surrounding code the diff touches —
   callers, callees, tests, config, and data formats. The diff alone is never
   enough to explain intent.
3. Recover intent from history and prose: commit messages, PR description,
   linked issues, ADRs/RFCs, and comments added or removed by the change.
4. Mark anything you could not determine as an open question in the document
   rather than inventing a rationale.

## Sections To Produce

Emit these four sections, in this order, as one document.

1. **Background** — the existing system the change acts on. Write two tiers: a
   deep tier for a reader new to this domain, placed in a collapsed admonition
   so a familiar reader can skip it, then a narrow tier covering only the
   components the diff touches.
2. **Intuition** — the essence of the change, not the details. Walk one concrete
   example with toy data from input to observable outcome, and show before and
   after. Diagrams carry most of the weight here.
3. **Code** — a high-level walkthrough of the actual changes, grouped by concern
   and ordered so each group builds on the previous one. Quote only the lines
   that matter and say why each group exists. Name files and symbols exactly.
4. **Quiz** — five multiple-choice questions of medium difficulty: answerable
   only by someone who understood the substance, never trick questions. Each
   option is a dropdown that reveals whether it is correct and explains why.

## Output Format

Write the artifact outside the code repository, in a dated directory so the
files stay time-sorted and out of version control:

```text
/tmp/YYYY-MM-DD-explanation-<slug>/
  myst.yml
  index.md
```

`myst.yml` only needs enough to build:

```yaml
version: 1
project:
  id: explanation-<slug>
  title: <title>
site:
  template: book-theme
```

`index.md` starts with frontmatter naming the change and the ref it explains:

```yaml
---
title: What <change> does and why
subtitle: <repo> · <branch-or-PR> · <commit-sha>
---
```

Report the absolute directory path.

## MyST Constructs To Use

These are the constructs the document is built from. Use them and nothing
exotic; every one below is core `mystmd` syntax.

Callouts for definitions, invariants, and edge cases — `note`, `important`,
`tip`, `warning`, `caution`, `danger`, `hint`, `seealso`, `attention`, `error`:

```markdown
:::{important} One key per queue
The queue never holds two entries for the same key.
:::
```

Collapsed content, for the skippable deep background and for long digressions —
any admonition becomes a `<details>` disclosure with `:class: dropdown`, and
`:open:` starts it expanded:

```markdown
:::{admonition} Deep background: how the router worked before
:class: dropdown
Skip this if you already know the routing layer.
:::
```

Diagrams as mermaid, never ASCII art:

````markdown
```{mermaid}
flowchart LR
  A[client] -->|"key=k1"| B[router]
  B --> C[(store)]
```
````

Quiz questions as a heading per question and one `{dropdown}` per option,
carrying the verdict and its reason:

```markdown
### Q1. Which component collapses duplicate keys?

:::{dropdown} A. The client
❌ The client sends every write; it has no cross-request state.
:::

:::{dropdown} B. The router
✅ `Router.enqueue` replaces an existing entry for the same key before the
store is touched.
:::
```

Code stays in fenced blocks with a language tag. Images, when a screenshot or an
exported figure genuinely helps, use `{figure} <path>` with a caption. Tables use
plain Markdown tables. Do not reach for grids, cards, or tabs for the top-level
structure — they hide the narrative.

## Diagrams

Pick two or three diagram families and reuse them across the document so the
reader learns one visual language instead of five. Families that carry most
changes:

- A flow diagram of data or control between components, annotated with **example
  values**, not just type names.
- A before/after pair using the identical node layout, so the delta is the only
  visual difference.
- A state or sequence diagram when the change is about ordering or lifecycle.

## Style

Write with the clarity and flow of Martin Kleppmann: classic style, concrete
nouns, no filler, each section handing off to the next in one sentence. Explain
the reason a change exists before its mechanics. Prefer a worked example over an
abstract statement of behavior.

## Before Reporting Done

- Build the document and confirm it is clean:
  `cd /tmp/YYYY-MM-DD-explanation-<slug> && npx mystmd build --html`. There must
  be no `unknown directive` or `⛔️` lines; unresolved references are also errors.
- Confirm every mermaid block parses in the rendered page rather than showing as
  raw text.
- Confirm each quiz answer's explanation matches the code as written, not the
  code as you remembered it.
