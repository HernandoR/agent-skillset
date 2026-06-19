from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
REQUIRED_OPENAI_KEYS = {"display_name", "short_description", "default_prompt"}


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")

    try:
        _, frontmatter, _body = text.split("---", 2)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter") from exc

    data = yaml.safe_load(frontmatter)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def validate_openai_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{path.relative_to(REPO_ROOT)} missing"]

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [f"{path.relative_to(REPO_ROOT)} must be a mapping"]

    interface = data.get("interface")
    if not isinstance(interface, dict):
        return [f"{path.relative_to(REPO_ROOT)} missing interface mapping"]

    missing = REQUIRED_OPENAI_KEYS - set(interface)
    if missing:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} interface missing keys: "
            f"{', '.join(sorted(missing))}"
        )

    for key in REQUIRED_OPENAI_KEYS:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"{path.relative_to(REPO_ROOT)} interface.{key} must be non-empty text"
            )

    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"{skill_dir.relative_to(REPO_ROOT)} missing SKILL.md"]

    try:
        metadata = load_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{skill_file.relative_to(REPO_ROOT)}: {exc}"]

    name = metadata.get("name")
    description = metadata.get("description")
    if name != skill_dir.name:
        errors.append(
            f"{skill_file.relative_to(REPO_ROOT)} name {name!r} "
            f"does not match folder {skill_dir.name!r}"
        )
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file.relative_to(REPO_ROOT)} missing description")

    errors.extend(validate_openai_yaml(skill_dir / "agents" / "openai.yaml"))
    return errors


REQUIRED_PLUGIN_KEYS = {"name", "version", "description"}


def validate_plugin(repo_root: Path) -> list[str]:
    errors: list[str] = []
    plugin_file = repo_root / ".claude-plugin" / "plugin.json"
    hooks_file = repo_root / "hooks" / "hooks.json"

    if not plugin_file.exists():
        errors.append(".claude-plugin/plugin.json missing")
    else:
        import json

        try:
            data = json.loads(plugin_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f".claude-plugin/plugin.json invalid JSON: {exc}"]

        if not isinstance(data, dict):
            errors.append(".claude-plugin/plugin.json must be a JSON object")
        else:
            missing = REQUIRED_PLUGIN_KEYS - set(data)
            if missing:
                errors.append(
                    f".claude-plugin/plugin.json missing keys: "
                    f"{', '.join(sorted(missing))}"
                )

    if not hooks_file.exists():
        errors.append("hooks/hooks.json missing")
    else:
        import json

        try:
            data = json.loads(hooks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"hooks/hooks.json invalid JSON: {exc}"]

        if not isinstance(data, dict) or not isinstance(data.get("hooks"), list):
            errors.append("hooks/hooks.json must be a JSON object with a 'hooks' array")

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print("skills/ does not exist yet; nothing to validate")
        return 0

    errors: list[str] = []
    errors.extend(validate_plugin(REPO_ROOT))
    for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        errors.extend(validate_skill(skill_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
