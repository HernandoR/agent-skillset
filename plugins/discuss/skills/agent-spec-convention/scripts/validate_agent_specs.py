#!/usr/bin/env python3
"""Validate `.agents/spec/*.md` files against the agent-spec schema.

Stdlib-only.

Checks:
- YAML-ish frontmatter (only `name`, `version`, `last_updated`,
  `superseded_by` recognised; all but the last are required)
- Five required H2 headings in order: Rule, Why, Where, Examples, References
- `## Examples` contains at least one `BAD` and one `GOOD` marker
- Per-section opt-out: `<!-- agent-spec: skip-section <name> -->` immediately
  before the heading

If `--check-mirror` is passed and `AGENTS.md` exists in the project root, the
linter additionally verifies:
- every `.agents/spec/<name>.md` has a matching section in `AGENTS.md`
- the section contains a paragraph (not a bare link)
- the section's first sentence matches the spec's first `## Rule` sentence

Usage:
    validate_agent_specs.py [--check-mirror] [SPEC_DIR] [AGENTS_MD]

Defaults: SPEC_DIR=.agents/spec, AGENTS_MD=AGENTS.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = ("name", "version", "last_updated")
OPTIONAL_FRONTMATTER = ("superseded_by",)
REQUIRED_HEADINGS = ("Rule", "Why", "Where", "Examples", "References")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SKIP_SECTION_RE = re.compile(
    r"<!--\s*agent-spec:\s*skip-section\s+(\w+)\s*-->", re.IGNORECASE
)
RULE_FIRST_SENTENCE_RE = re.compile(
    r"##\s+Rule\s*\n+([^\n]+(?:\n[^\n#]+)*?)(?=\n\n|\Z)"
)
AGENTS_SECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    body = text[match.end() :]
    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, body


def find_skip_sections(text: str) -> set[str]:
    skips: set[str] = set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = SKIP_SECTION_RE.search(line)
        if not match:
            continue
        # Must be on the line directly preceding an H2.
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        if next_line.startswith("## "):
            skips.add(match.group(1))
    return skips


def first_rule_sentence(text: str) -> str | None:
    match = RULE_FIRST_SENTENCE_RE.search(text)
    if not match:
        return None
    paragraph = " ".join(match.group(1).split())
    # Take the first sentence terminated by `.`, `!`, or `?`.
    sentence = re.split(r"(?<=[.!?])\s+", paragraph, maxsplit=1)[0]
    return sentence.strip()


def validate_spec(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if not fm:
        return [f"{path}: missing or malformed frontmatter"]

    for key in REQUIRED_FRONTMATTER:
        if key not in fm or not fm[key]:
            errors.append(f"{path}: frontmatter missing `{key}`")
    for key in fm:
        if key not in REQUIRED_FRONTMATTER and key not in OPTIONAL_FRONTMATTER:
            errors.append(f"{path}: frontmatter has unrecognised key `{key}`")

    skips = find_skip_sections(body)
    headings = [m.group(1) for m in H2_RE.finditer(body)]

    expected_headings = [h for h in REQUIRED_HEADINGS if h not in skips]
    if headings != expected_headings:
        errors.append(
            f"{path}: H2 headings are {headings!r}, expected {expected_headings!r} "
            "(use `<!-- agent-spec: skip-section <name> -->` to opt out)"
        )

    if "Examples" not in skips:
        examples_block = _section_body(body, "Examples")
        if examples_block is not None:
            if "BAD" not in examples_block:
                errors.append(f"{path}: ## Examples missing a BAD label")
            if "GOOD" not in examples_block:
                errors.append(f"{path}: ## Examples missing a GOOD label")

    return errors


def _section_body(body: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1) if match else None


def validate_mirror(spec_dir: Path, agents_md: Path) -> list[str]:
    if not agents_md.exists():
        return [f"{agents_md}: not found (skip --check-mirror or create the file)"]

    agents_text = agents_md.read_text(encoding="utf-8")
    sections = {
        m.group(1).strip(): _section_body_from_h3(agents_text, m.group(1))
        for m in AGENTS_SECTION_RE.finditer(agents_text)
    }

    errors: list[str] = []
    for spec_path in sorted(spec_dir.glob("*.md")):
        spec_text = spec_path.read_text(encoding="utf-8")
        _, spec_body = parse_frontmatter(spec_text)
        spec_first = first_rule_sentence(spec_body) or ""

        # Match a section by spec filename slug or spec H1 title.
        slug = spec_path.stem
        title = _h1_title(spec_body) or slug

        section_body = sections.get(title)
        if section_body is None:
            errors.append(
                f"{agents_md}: missing section `### {title}` "
                f"(or matching slug `{slug}`)"
            )
            continue

        if not _has_paragraph(section_body):
            errors.append(f"{agents_md} section {title!r}: must contain a paragraph")
            continue

        first_summary_sentence = _first_paragraph_first_sentence(section_body)
        if first_summary_sentence != spec_first:
            errors.append(
                f"{agents_md} section {title!r}: first sentence mismatch.\n"
                f"  spec  : {spec_first!r}\n"
                f"  mirror: {first_summary_sentence!r}"
            )

    return errors


def _section_body_from_h3(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^###\s+{re.escape(heading)}\s*$(.*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def _h1_title(body: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def _has_paragraph(section_body: str) -> bool:
    for line in section_body.splitlines():
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("#")
            and not stripped.startswith("Full spec")
        ):
            return True
    return False


def _first_paragraph_first_sentence(section_body: str) -> str:
    paragraph_lines: list[str] = []
    for line in section_body.splitlines():
        stripped = line.strip()
        if not stripped:
            if paragraph_lines:
                break
            continue
        if stripped.startswith("Full spec"):
            break
        paragraph_lines.append(stripped)
    paragraph = " ".join(paragraph_lines)
    sentence = re.split(r"(?<=[.!?])\s+", paragraph, maxsplit=1)[0]
    return sentence.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate .agents/spec/*.md files against the schema."
    )
    parser.add_argument(
        "spec_dir",
        nargs="?",
        type=Path,
        default=Path(".agents/spec"),
    )
    parser.add_argument(
        "agents_md",
        nargs="?",
        type=Path,
        default=Path("AGENTS.md"),
    )
    parser.add_argument(
        "--check-mirror",
        action="store_true",
        help="Also validate AGENTS.md mirror sections.",
    )
    args = parser.parse_args(argv)

    if not args.spec_dir.exists():
        print(f"validate_agent_specs: {args.spec_dir} does not exist")
        return 0

    errors: list[str] = []
    for path in sorted(args.spec_dir.glob("*.md")):
        errors.extend(validate_spec(path))

    if args.check_mirror:
        errors.extend(validate_mirror(args.spec_dir, args.agents_md))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print("validate_agent_specs: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
