---
name: explain-diff-html
description: Use when asked to explain a code change, diff, commit range, branch, or PR to a human reader as a rich, self-contained HTML page with diagrams and an interactive quiz. Trigger on "explain this diff/PR/branch", "write up this change", "onboarding doc for this change", or a request for a shareable single-file explanation. Not for writing commit messages, PR descriptions, changelogs, or release notes, and not for reviewing a change for defects.
---

# Explain Diff (HTML)

Produce one self-contained HTML file that teaches a reader the change: what the
system did before, the essential idea of the change, a walkthrough of the code,
and a quiz that checks comprehension. The reader may know nothing about this
codebase, so the page must carry its own background.

## Establish The Change And Its Context

1. Resolve exactly what to explain. If the user named a branch, PR, commit, or
   range, use it; otherwise ask which change, or use the working tree diff when
   that is unambiguous. Record the resolved ref in the page.
2. Read the full diff, then read the surrounding code the diff touches —
   callers, callees, tests, config, and data formats. The diff alone is never
   enough to explain intent.
3. Recover intent from history and prose: commit messages, PR description,
   linked issues, ADRs/RFCs, and comments added or removed by the change.
4. Mark anything you could not determine as an open question in the page rather
   than inventing a rationale.

## Sections To Produce

Emit these four sections, in this order, as one long page.

1. **Background** — the existing system the change acts on. Write two tiers: a
   deep tier for a reader new to this domain, explicitly labelled as skippable,
   then a narrow tier covering only the components the diff touches.
2. **Intuition** — the essence of the change, not the details. Walk one concrete
   example with toy data from input to observable outcome, and show the before
   and after side by side. Diagrams carry most of the weight here.
3. **Code** — a high-level walkthrough of the actual changes, grouped by concern
   and ordered so each group builds on the previous one. Quote only the lines
   that matter and say why each group exists. Name files and symbols exactly.
4. **Quiz** — five multiple-choice questions of medium difficulty: answerable
   only by someone who understood the substance, never trick questions. Each
   option, when clicked, reveals whether it is correct and explains why.

## Output Format

- One HTML file with all CSS and JavaScript inlined. No build step, no external
  assets, no network dependency at view time.
- Write the file outside the code repository, with a filename starting with
  today's date so the files stay time-sorted and out of version control:
  `/tmp/YYYY-MM-DD-explanation-<slug>.html`. Report the absolute path.
- One long scrolling page with a table of contents linking to section anchors.
  Do not put the top-level structure behind tabs — tabs hide the narrative.
- Responsive enough to read on a phone: fluid width, no fixed pixel layout, no
  horizontal scrolling outside code blocks.
- Code blocks go in `<pre>` tags. If a styled `<div>` is used instead, its CSS
  **must** set `white-space: pre` or `pre-wrap`, or the browser collapses every
  newline into one line. Before saving, scan every code block in the source and
  confirm this holds.
- Callouts (a styled `<aside>` or `<div>`) for key definitions, invariants, and
  edge cases. Keep them short; a page of callouts is a page of noise.
- Never draw ASCII diagrams. Use plain HTML and CSS: boxes, arrows built from
  borders, inline SVG, HTML lists for enumerations, and HTML tables for matrices.

## Diagrams

Pick two or three diagram families and reuse them across the page so the reader
learns one visual language instead of five. Families that carry most changes:

- A simplified rendering of the UI the user sees, for changes with visible
  surface.
- A component diagram showing data or control flow between parts, annotated with
  **example values**, not just type names.
- A before/after pair using the identical layout, so the delta is the only
  visual difference.

## Style

Write with the clarity and flow of Martin Kleppmann: classic style, concrete
nouns, no filler, each section handing off to the next in one sentence. Explain
the reason a change exists before its mechanics. Prefer a worked example over an
abstract statement of behavior.

## Before Reporting Done

- Open the file in a browser and check it renders: TOC anchors jump, quiz
  options respond to clicks and show feedback, no console errors.
- Confirm every code block preserves newlines.
- Confirm each quiz answer's explanation matches the code as written, not the
  code as you remembered it.
