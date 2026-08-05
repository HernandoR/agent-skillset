from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"
REQUIRED_OPENAI_KEYS = {"display_name", "short_description", "default_prompt"}
REQUIRED_PLUGIN_KEYS = {"name", "version", "description"}
COMPONENT_PATH_FIELDS = {
    "skills",
    "commands",
    "agents",
    "hooks",
    "mcpServers",
    "lspServers",
}


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


def validate_plugin_dir(plugin_dir: Path) -> list[str]:
    errors: list[str] = []
    plugin_file = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_file.exists():
        return [
            f"{plugin_dir.relative_to(REPO_ROOT)}/.claude-plugin/plugin.json missing"
        ]

    try:
        data = json.loads(plugin_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{plugin_file.relative_to(REPO_ROOT)} invalid JSON: {exc}"]

    if not isinstance(data, dict):
        errors.append(f"{plugin_file.relative_to(REPO_ROOT)} must be a JSON object")
    else:
        missing = REQUIRED_PLUGIN_KEYS - set(data)
        if missing:
            errors.append(
                f"{plugin_file.relative_to(REPO_ROOT)} missing keys: "
                f"{', '.join(sorted(missing))}"
            )
        for field in COMPONENT_PATH_FIELDS & set(data):
            value = data[field]
            rel = plugin_file.relative_to(REPO_ROOT)
            if not isinstance(value, str):
                errors.append(f"{rel} {field!r} must be a string path")
            elif not value.startswith("./"):
                errors.append(f"{rel} {field!r} must start with './' (got {value!r})")

    return errors


def validate_marketplace(repo_root: Path) -> list[str]:
    errors: list[str] = []
    marketplace_file = repo_root / ".claude-plugin" / "marketplace.json"

    if not marketplace_file.exists():
        errors.append(".claude-plugin/marketplace.json missing")
        return errors

    try:
        data = json.loads(marketplace_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f".claude-plugin/marketplace.json invalid JSON: {exc}"]

    if not isinstance(data, dict):
        errors.append(".claude-plugin/marketplace.json must be a JSON object")
        return errors

    required = {"name", "owner", "plugins"}
    missing = required - set(data)
    if missing:
        errors.append(
            ".claude-plugin/marketplace.json missing keys: "
            f"{', '.join(sorted(missing))}"
        )

    owner = data.get("owner")
    if not isinstance(owner, dict) or not isinstance(owner.get("name"), str):
        errors.append(
            ".claude-plugin/marketplace.json owner must be an object with 'name'"
        )

    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        errors.append(".claude-plugin/marketplace.json 'plugins' must be an array")
    else:
        for i, plugin in enumerate(plugins):
            if not isinstance(plugin, dict):
                errors.append(
                    f".claude-plugin/marketplace.json plugins[{i}] must be an object"
                )
                continue
            for key in ("name", "source"):
                if key not in plugin:
                    errors.append(
                        f".claude-plugin/marketplace.json plugins[{i}] missing '{key}'"
                    )
            source = plugin.get("source", "")
            if isinstance(source, str) and not source.startswith("./"):
                errors.append(
                    f".claude-plugin/marketplace.json plugins[{i}].source "
                    "must start with './'"
                )

    return errors


def main() -> int:
    if not PLUGINS_DIR.exists():
        print("plugins/ does not exist yet; nothing to validate")
        return 0

    errors: list[str] = []
    errors.extend(validate_marketplace(REPO_ROOT))

    for plugin_dir in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        errors.extend(validate_plugin_dir(plugin_dir))
        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                errors.extend(validate_skill(skill_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
