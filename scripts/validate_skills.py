from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"
REQUIRED_OPENAI_KEYS = {"display_name", "short_description", "default_prompt"}
REQUIRED_PLUGIN_KEYS = {"name", "version", "description"}

# Agent Plugins 1.0.0 (https://agent-plugins.org) closed root plugin.json schema.
AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGIN_KEYS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
AGENT_PLUGIN_NAME_RE = re.compile(
    r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$"
)
COMPONENT_PATH_FIELDS = {
    "skills",
    "commands",
    "agents",
    "hooks",
    "mcpServers",
    "lspServers",
}

# Top-level fields Codex's plugin-manifest loader recognises. Anything else is
# silently dropped there, so reject it here rather than let it look supported.
CODEX_PLUGIN_KEYS = {
    "name",
    "version",
    "description",
    "keywords",
    "skills",
    "mcpServers",
    "apps",
    "hooks",
    "interface",
}
REQUIRED_INTERFACE_KEYS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
}
MAX_DEFAULT_PROMPTS = 3
MAX_DEFAULT_PROMPT_CHARS = 128
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


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


def validate_agent_plugin_manifest(plugin_dir: Path) -> list[str]:
    """Validate the root plugin.json as an Agent Plugins 1.0.0 manifest.

    Agent Plugins requires the portable manifest at the plugin root with a
    closed top-level schema and a restricted name. The root manifest must also
    stay in sync with the Claude/Codex manifest (``.claude-plugin/plugin.json``)
    so the package keeps one identity and one version across ecosystems.
    """
    errors: list[str] = []
    manifest_file = plugin_dir / "plugin.json"
    rel = manifest_file.relative_to(REPO_ROOT)

    if not manifest_file.exists():
        return [f"{rel} missing (required by Agent Plugins 1.0.0)"]

    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel} invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return [f"{rel} must be a JSON object"]

    if data.get("$schema") != AGENT_PLUGIN_SCHEMA:
        errors.append(f"{rel} $schema must be {AGENT_PLUGIN_SCHEMA!r}")

    name = data.get("name")
    if not isinstance(name, str) or not AGENT_PLUGIN_NAME_RE.match(name):
        errors.append(
            f"{rel} name {name!r} must match the Agent Plugins pattern "
            "(lowercase alnum, hyphen, period; alnum start/end; no '--' or '..')"
        )

    unsupported = {str(key) for key in data} - AGENT_PLUGIN_KEYS
    if unsupported:
        errors.append(
            f"{rel} has fields outside the Agent Plugins closed schema: "
            f"{', '.join(sorted(unsupported))}"
        )

    version = data.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append(f"{rel} version {version!r} must be strict semver (X.Y.Z)")

    author = data.get("author")
    if author is not None:
        if not isinstance(author, dict):
            errors.append(f"{rel} 'author' must be an object")
        else:
            extra = set(author) - {"name", "email", "url"}
            if extra:
                errors.append(
                    f"{rel} author has fields outside name/email/url: "
                    f"{', '.join(sorted(extra))}"
                )

    keywords = data.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list)
        or any(not isinstance(k, str) or not k.strip() for k in keywords)
    ):
        errors.append(f"{rel} 'keywords' must be an array of non-empty text")

    claude_file = plugin_dir / ".claude-plugin" / "plugin.json"
    try:
        claude = json.loads(claude_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return errors  # reported by validate_plugin_dir

    if not isinstance(claude, dict):
        return errors

    if claude.get("name") != name:
        errors.append(
            f"{rel} name {name!r} != .claude-plugin/plugin.json name "
            f"{claude.get('name')!r}"
        )
    if claude.get("version") != version:
        errors.append(
            f"{rel} version {version!r} != .claude-plugin/plugin.json version "
            f"{claude.get('version')!r}"
        )

    return errors


def validate_plugin_interface(rel: Path, data: dict[str, Any]) -> list[str]:
    """Validate the Codex `interface` block used for plugin presentation."""
    errors: list[str] = []
    interface = data.get("interface")
    if interface is None:
        return [f"{rel} missing 'interface' block (required by Codex)"]
    if not isinstance(interface, dict):
        return [f"{rel} 'interface' must be an object"]

    missing = REQUIRED_INTERFACE_KEYS - set(interface)
    if missing:
        errors.append(f"{rel} interface missing keys: {', '.join(sorted(missing))}")

    for key in REQUIRED_INTERFACE_KEYS & set(interface):
        value = interface[key]
        if key in {"capabilities", "defaultPrompt"}:
            if not isinstance(value, list) or not value:
                errors.append(f"{rel} interface.{key} must be a non-empty array")
                continue
            if any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"{rel} interface.{key} entries must be non-empty text")
        elif not isinstance(value, str) or not value.strip():
            errors.append(f"{rel} interface.{key} must be non-empty text")

    prompts = interface.get("defaultPrompt")
    if isinstance(prompts, list):
        if len(prompts) > MAX_DEFAULT_PROMPTS:
            errors.append(
                f"{rel} interface.defaultPrompt has {len(prompts)} entries; "
                f"Codex allows at most {MAX_DEFAULT_PROMPTS}"
            )
        for prompt in prompts:
            if isinstance(prompt, str) and len(prompt) > MAX_DEFAULT_PROMPT_CHARS:
                errors.append(
                    f"{rel} interface.defaultPrompt entry exceeds "
                    f"{MAX_DEFAULT_PROMPT_CHARS} chars: {prompt[:40]!r}..."
                )

    return errors


def validate_plugin_dir(plugin_dir: Path) -> list[str]:
    errors: list[str] = []
    plugin_file = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_file.exists():
        return [
            f"{plugin_dir.relative_to(REPO_ROOT)}/.claude-plugin/plugin.json missing"
        ]

    rel = plugin_file.relative_to(REPO_ROOT)

    try:
        data = json.loads(plugin_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel} invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return [f"{rel} must be a JSON object"]

    missing = REQUIRED_PLUGIN_KEYS - set(data)
    if missing:
        errors.append(f"{rel} missing keys: {', '.join(sorted(missing))}")

    unsupported = {str(key) for key in data} - CODEX_PLUGIN_KEYS
    if unsupported:
        errors.append(
            f"{rel} has fields Codex does not recognise: "
            f"{', '.join(sorted(unsupported))}"
        )

    version = data.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append(f"{rel} version {version!r} must be strict semver (X.Y.Z)")

    keywords = data.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        errors.append(f"{rel} 'keywords' must be a non-empty array")
    elif any(not isinstance(k, str) or not k.strip() for k in keywords):
        errors.append(f"{rel} 'keywords' entries must be non-empty text")

    for field in COMPONENT_PATH_FIELDS & set(data):
        value = data[field]
        if not isinstance(value, str):
            errors.append(f"{rel} {field!r} must be a string path")
        elif not value.startswith("./"):
            errors.append(f"{rel} {field!r} must start with './' (got {value!r})")

    errors.extend(validate_plugin_interface(rel, data))
    return errors


def validate_pi_package(repo_root: Path, skill_roots: list[Path]) -> list[str]:
    """Validate the root package.json that makes this repo a Pi package."""
    package_file = repo_root / "package.json"
    if not package_file.exists():
        return ["package.json missing (required for Pi package discovery)"]

    try:
        data = json.loads(package_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"package.json invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return ["package.json must be a JSON object"]

    errors: list[str] = []
    keywords = data.get("keywords")
    if not isinstance(keywords, list) or "pi-package" not in keywords:
        errors.append("package.json keywords must include 'pi-package'")

    version = data.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append(f"package.json version {version!r} must be strict semver")

    pi = data.get("pi")
    if not isinstance(pi, dict):
        return errors + ["package.json missing 'pi' manifest object"]

    patterns = pi.get("skills")
    if not isinstance(patterns, list) or not patterns:
        return errors + ["package.json pi.skills must be a non-empty array"]

    matched: set[Path] = set()
    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern.startswith("./"):
            errors.append(
                f"package.json pi.skills entry must start with './': {pattern!r}"
            )
            continue
        matched.update(
            p for p in repo_root.glob(pattern.removeprefix("./")) if p.is_dir()
        )

    for root in skill_roots:
        if root not in matched:
            errors.append(
                f"package.json pi.skills does not cover {root.relative_to(repo_root)}"
            )

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


def validate_marketplace_plugin_names(
    repo_root: Path, plugin_dirs: list[Path]
) -> list[str]:
    """Each marketplace entry name must match its plugin manifest name.

    The marketplace entry is the install-time identifier for Claude Code; the
    manifest name is the package identity everywhere else. Keeping them equal
    prevents a split identity between the marketplace and the bundle.
    """
    errors: list[str] = []
    marketplace_file = repo_root / ".claude-plugin" / "marketplace.json"
    try:
        data = json.loads(marketplace_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []  # reported by validate_marketplace

    plugins = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(plugins, list):
        return []

    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        entry_name = plugin.get("name")
        source = plugin.get("source")
        if not isinstance(entry_name, str) or not isinstance(source, str):
            continue

        # Only relative sources map to a bundle directory in this repo.
        if not source.startswith("./"):
            continue
        plugin_dir = (repo_root / source.removeprefix("./")).resolve()
        if plugin_dir not in {p.resolve() for p in plugin_dirs}:
            continue

        manifest_name = None
        manifest_file = plugin_dir / ".claude-plugin" / "plugin.json"
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(manifest, dict):
            manifest_name = manifest.get("name")

        if manifest_name is not None and entry_name != manifest_name:
            errors.append(
                f"marketplace.json entry {entry_name!r} != manifest name "
                f"{manifest_name!r} for {source!r}"
            )

    return errors


def validate_release_versions_agree(repo_root: Path) -> list[str]:
    """The two release manifests must carry the same version."""
    marketplace_file = repo_root / ".claude-plugin" / "marketplace.json"
    package_file = repo_root / "package.json"
    if not marketplace_file.exists() or not package_file.exists():
        return []

    try:
        marketplace = json.loads(marketplace_file.read_text(encoding="utf-8"))
        package = json.loads(package_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []  # reported by the dedicated validators

    if not isinstance(marketplace, dict) or not isinstance(package, dict):
        return []

    left = marketplace.get("version")
    right = package.get("version")
    if left != right:
        return [
            f"release version mismatch: marketplace.json {left!r} "
            f"!= package.json {right!r}"
        ]
    return []


def main() -> int:
    if not PLUGINS_DIR.exists():
        print("plugins/ does not exist yet; nothing to validate")
        return 0

    errors: list[str] = []
    errors.extend(validate_marketplace(REPO_ROOT))

    plugin_dirs = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())
    errors.extend(validate_marketplace_plugin_names(REPO_ROOT, plugin_dirs))

    skill_roots: list[Path] = []
    for plugin_dir in plugin_dirs:
        errors.extend(validate_plugin_dir(plugin_dir))
        errors.extend(validate_agent_plugin_manifest(plugin_dir))
        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            skill_roots.append(skills_dir)
            for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                errors.extend(validate_skill(skill_dir))

    errors.extend(validate_pi_package(REPO_ROOT, skill_roots))
    errors.extend(validate_release_versions_agree(REPO_ROOT))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
