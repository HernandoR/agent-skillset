#!/usr/bin/env python3
"""Offline installer for the DeepSeek V4 Flash Codex subagent.

Installs the vendored payload from ``assets/upstream/`` (pinned copy of
https://github.com/Utopia-V/codex-deepseek-subagent) into a personal Codex
home. No network access is needed or attempted.

Flow: print the full plan, take one clearance, install idempotently, verify
offline, and print a redacted report. Stdlib only; requires Python 3.11+
(tomllib). Installation is gated on the DEEPSEEK_API_KEY environment variable
being present (presence only — the value is never read, printed, or stored);
--plan works without it.

Usage:
  install.py            # plan, ask once on a TTY, then install + verify
  install.py --plan     # print the plan and exit without writing
  install.py --yes      # skip the interactive clearance (for agents/CI)
  install.py --codex-home PATH   # override CODEX_HOME/~/.codex
  install.py --skip-tests        # skip the local hook protocol test
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:  # Python < 3.11; reported in main()
        tomllib = None

UPSTREAM = Path(__file__).resolve().parents[1] / "assets" / "upstream"
MARKER_START = "<!-- codex-deepseek-subagent:start -->"
MARKER_END = "<!-- codex-deepseek-subagent:end -->"
HOOK_DIR_NAME = "codex-deepseek-subagent"
RECOMMENDED_CODEX = (0, 145, 0)

IS_WINDOWS = os.name == "nt"
AGENT_SRC = (
    "agents/windows-live-env/v4-flash-worker.toml"
    if IS_WINDOWS
    else "agents/v4-flash-worker.toml"
)
HOOK_SCRIPT_SRC = (
    "hooks/plaintext-handoff.ps1" if IS_WINDOWS else "hooks/plaintext_handoff.py"
)
HOOK_EXAMPLE_SRC = (
    "hooks/hooks.windows.example.json"
    if IS_WINDOWS
    else "hooks/hooks.posix.example.json"
)
SKILL_FILES = (
    "skills/use-v4-flash-worker/SKILL.md",
    "skills/use-v4-flash-worker/agents/openai.yaml",
)


class InstallConflict(Exception):
    """An existing artifact at an intended identity serves a different purpose."""


@dataclass
class Action:
    label: str
    dst: Path
    kind: str  # "create" | "update" | "unchanged"
    diff: str = ""
    apply: Callable[[], None] | None = None  # set by the planner

    def describe(self) -> str:
        return f"[{self.kind:>9}] {self.label}: {self.dst}"


@dataclass
class Report:
    actions: list[Action] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def codex_home(override: str | None) -> Path:
    if override:
        return Path(override).expanduser()
    env = os.environ.get("CODEX_HOME")
    return Path(env).expanduser() if env else Path.home() / ".codex"


def codex_version_note() -> str:
    exe = shutil.which("codex")
    if not exe:
        return "codex CLI not found; proceeding (files are version-independent)."
    try:
        out = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=10, check=False
        ).stdout.strip()
    except OSError as exc:
        return f"could not run codex --version ({exc}); proceeding."
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
    if match and tuple(int(g) for g in match.groups()) < RECOMMENDED_CODEX:
        return (
            f"codex version {match.group(0)} is older than the recommended "
            f"{'.'.join(map(str, RECOMMENDED_CODEX))}; standalone agent files may "
            "not be discovered. Not upgrading anything; verify after install."
        )
    return f"codex --version: {out or 'unknown'}"


def unified_diff(old: str, new: str, path: Path) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"{path} (current)",
            tofile=f"{path} (new)",
        )
    )


def plan_copy(label: str, src: Path, dst: Path) -> Action:
    new = src.read_bytes()
    if dst.exists():
        current = dst.read_bytes()
        if current == new:
            return Action(label, dst, "unchanged")
        try:
            diff = unified_diff(current.decode(), new.decode(), dst)
        except UnicodeDecodeError:
            diff = "(binary change)"
        action = Action(label, dst, "update", diff)
    else:
        action = Action(label, dst, "create")

    def apply(src=src, dst=dst) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    action.apply = apply
    return action


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    _, block, _ = text.split("---", 2)
    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if line[:1] not in ("", " ", "\t") and ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()
    return fields


def check_agent_identity(dst: Path) -> None:
    """Stop if an existing agent file at the target serves a different purpose."""
    if not dst.exists():
        return
    try:
        data = tomllib.loads(dst.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise InstallConflict(f"{dst} exists but is not valid TOML: {exc}") from exc
    if data.get("name") not in (None, "v4_flash_worker"):
        raise InstallConflict(
            f"{dst} defines agent {data.get('name')!r}, not v4_flash_worker; "
            "refusing to overwrite a different agent."
        )


def check_skill_identity(dst_dir: Path) -> None:
    skill_md = dst_dir / "SKILL.md"
    if not skill_md.exists():
        return
    try:
        name = parse_frontmatter(skill_md.read_text(encoding="utf-8")).get("name")
    except ValueError:
        raise InstallConflict(
            f"{skill_md} exists without parseable frontmatter."
        ) from None
    if name != "use-v4-flash-worker":
        raise InstallConflict(
            f"{skill_md} belongs to skill {name!r}; refusing to overwrite."
        )


def hook_command(script_path: Path) -> str:
    if IS_WINDOWS:
        return (
            "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass "
            f'-File "{script_path}" -Mode hook'
        )
    return f'python3 "{script_path}" --mode hook'


def build_hook_entry(script_path: Path) -> dict:
    """The structural source is the vendored platform example json."""
    example = json.loads((UPSTREAM / HOOK_EXAMPLE_SRC).read_text(encoding="utf-8"))
    entry = example["hooks"]["SubagentStart"][0]
    entry["hooks"][0]["command"] = hook_command(script_path)
    return entry


def plan_hook_merge(home: Path, script_path: Path) -> Action:
    config_toml = home / "config.toml"
    if config_toml.exists():
        try:
            config = tomllib.loads(config_toml.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError):
            config = {}
        if "hooks" in config:
            raise InstallConflict(
                f"{config_toml} carries inline Hook configuration; merging TOML "
                "in place is not supported by this installer. Merge the entry from "
                f"{UPSTREAM / HOOK_EXAMPLE_SRC} there manually, then re-run with "
                "the hooks.json step already satisfied."
            )

    hooks_file = home / "hooks.json"
    entry = build_hook_entry(script_path)
    if hooks_file.exists():
        try:
            data = json.loads(hooks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InstallConflict(f"{hooks_file} is not valid JSON: {exc}") from exc
        old_text = json.dumps(data, indent=2)
    else:
        data = {"hooks": {}}
        old_text = ""

    subagent = data.setdefault("hooks", {}).setdefault("SubagentStart", [])
    replaced = False
    for i, existing in enumerate(subagent):
        if existing.get("matcher") == entry["matcher"]:
            if existing == entry:
                return Action("SubagentStart hook entry", hooks_file, "unchanged")
            subagent[i] = entry
            replaced = True
            break
    if not replaced:
        subagent.append(entry)

    new_text = json.dumps(data, indent=2) + "\n"
    kind = "update" if hooks_file.exists() else "create"
    action = Action(
        "SubagentStart hook entry",
        hooks_file,
        kind,
        unified_diff(old_text, new_text, hooks_file),
    )

    def apply(hooks_file=hooks_file, new_text=new_text) -> None:
        hooks_file.parent.mkdir(parents=True, exist_ok=True)
        hooks_file.write_text(new_text, encoding="utf-8")

    action.apply = apply
    return action


def plan_agents_md(home: Path) -> Action:
    snippet = (UPSTREAM / "snippets" / "AGENTS.md").read_text(encoding="utf-8").strip()
    target = home / "AGENTS.md"
    current = target.read_text(encoding="utf-8") if target.exists() else ""

    if MARKER_START in current:
        if MARKER_END not in current:
            raise InstallConflict(
                f"{target} has the start marker but no end marker; fix it manually."
            )
        pre, rest = current.split(MARKER_START, 1)
        _, post = rest.split(MARKER_END, 1)
        new = pre + snippet + post
    else:
        lead = "\n" if current and not current.endswith("\n") else ""
        block = lead + snippet + "\n"
        new = current + ("\n" if current else "") + block

    if new == current:
        return Action("AGENTS.md routing block", target, "unchanged")
    kind = "update" if target.exists() else "create"
    action = Action(
        "AGENTS.md routing block", target, kind, unified_diff(current, new, target)
    )

    def apply(target=target, new=new) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new, encoding="utf-8")

    action.apply = apply
    return action


def build_plan(home: Path) -> tuple[list[Action], Path]:
    agent_dst = home / "agents" / "v4-flash-worker.toml"
    check_agent_identity(agent_dst)
    check_skill_identity(home / "skills" / "use-v4-flash-worker")

    script_dst = home / "hooks" / HOOK_DIR_NAME / Path(HOOK_SCRIPT_SRC).name
    actions = [
        plan_copy("agent file", UPSTREAM / AGENT_SRC, agent_dst),
        *(
            plan_copy(
                f"skill file {Path(rel).name}",
                UPSTREAM / rel,
                home / rel,
            )
            for rel in SKILL_FILES
        ),
        plan_copy("hook script", UPSTREAM / HOOK_SCRIPT_SRC, script_dst),
        plan_hook_merge(home, script_dst),
        plan_agents_md(home),
    ]
    return actions, script_dst


def scan_for_credentials(text: str, path: Path, report: Report) -> None:
    if re.search(r"sk-[A-Za-z0-9]{16,}", text):
        fail(f"{path} appears to contain a plaintext credential; aborting.")
    report.checks.append(f"{path.name}: no plaintext credential")


def verify(home: Path, script_dst: Path, report: Report, skip_tests: bool) -> None:
    agent_path = home / "agents" / "v4-flash-worker.toml"
    text = agent_path.read_text(encoding="utf-8")
    agent = tomllib.loads(text)
    provider = agent.get("model_providers", {}).get("deepseek", {})
    expectations = {
        "name is v4_flash_worker": agent.get("name") == "v4_flash_worker",
        "model_provider is deepseek": agent.get("model_provider") == "deepseek",
        "model is deepseek-v4-flash": agent.get("model") == "deepseek-v4-flash",
        "wire_api is responses": provider.get("wire_api") == "responses",
        "context window is 1000000": agent.get("model_context_window") == 1000000,
        "defaults to read-only": agent.get("sandbox_mode") == "read-only",
        "no model_reasoning_effort": "model_reasoning_effort" not in agent,
        "own [model_providers.deepseek]": provider.get("env_key") == "DEEPSEEK_API_KEY",
    }
    for label, ok in expectations.items():
        if not ok:
            fail(f"installed agent file failed check: {label}")
    report.checks.append(f"{agent_path}: all 8 agent-file assertions hold")
    scan_for_credentials(text, agent_path, report)

    config_toml = home / "config.toml"
    if config_toml.exists():
        config = tomllib.loads(config_toml.read_text(encoding="utf-8"))
        if "v4_flash_worker" in config.get("agents", {}) or "deepseek" in config.get(
            "model_providers", {}
        ):
            fail(f"{config_toml} carries agent/provider entries; must stay standalone.")
        report.checks.append(f"{config_toml}: no agent or DeepSeek provider entries")
    else:
        report.checks.append("config.toml: absent, nothing to check")

    skill_md = home / "skills" / "use-v4-flash-worker" / "SKILL.md"
    front = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if front.get("name") != "use-v4-flash-worker" or not front.get("description"):
        fail(f"{skill_md} frontmatter is invalid.")
    if "TODO" in skill_md.read_text(encoding="utf-8"):
        fail(f"{skill_md} still contains a TODO placeholder.")
    openai_yaml = home / "skills" / "use-v4-flash-worker" / "agents" / "openai.yaml"
    if "$use-v4-flash-worker" not in openai_yaml.read_text(encoding="utf-8"):
        fail(f"{openai_yaml} default prompt does not name $use-v4-flash-worker.")
    report.checks.append(f"{skill_md.parent}: frontmatter, prompt, TODO checks pass")

    hooks_file = home / "hooks.json"
    data = json.loads(hooks_file.read_text(encoding="utf-8"))
    entries = [
        e
        for e in data.get("hooks", {}).get("SubagentStart", [])
        if e.get("matcher") == "^v4_flash_worker$"
    ]
    if len(entries) != 1:
        fail(f"{hooks_file} must contain exactly one ^v4_flash_worker$ entry.")
    hook = entries[0]["hooks"][0]
    if (
        hook.get("timeout") != 10
        or hook.get("additionalContextLimit") != 0
        or str(script_dst) not in hook.get("command", "")
    ):
        fail(f"{hooks_file} entry does not match the required matcher/command/limits.")
    report.checks.append(f"{hooks_file}: matcher, command, timeout, context limit OK")

    if skip_tests:
        report.notes.append("Hook protocol test skipped (--skip-tests).")
    elif IS_WINDOWS:
        report.notes.append(
            "Windows: run assets/upstream/tests/plaintext-handoff.windows.ps1 to "
            "prove the hook protocol; the Python test targets POSIX."
        )
    else:
        result = subprocess.run(
            [sys.executable, str(UPSTREAM / "tests" / "test_plaintext_handoff.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"hook protocol test failed:\n{result.stdout}\n{result.stderr}")
        report.checks.append(
            "protocol test: collision, role, marker, one-shot, replay, expiry all pass"
        )

    report.notes.append(f"DEEPSEEK_API_KEY present: {deepseek_key_present()}")


def deepseek_key_present() -> bool:
    """Presence only; the value is never read further, printed, or stored."""
    return bool(os.environ.get("DEEPSEEK_API_KEY"))


def print_plan(home: Path, actions: list[Action]) -> None:
    print(f"Codex home: {home}")
    print(f"Vendored source: {UPSTREAM} (see ../MANIFEST.json for the pinned commit)")
    print(codex_version_note())
    print(f"DEEPSEEK_API_KEY present: {deepseek_key_present()} (required to install)")
    print("\nPlan:")
    for action in actions:
        print(f"  {action.describe()}")
    print("\nUntouched: main model, provider config, login, every unrelated Hook.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="print the plan and exit")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation")
    parser.add_argument("--codex-home", help="override CODEX_HOME/~/.codex")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    if tomllib is None:
        fail("Python 3.11+ is required (tomllib). Run via uv if needed.")

    home = codex_home(args.codex_home)
    try:
        actions, script_dst = build_plan(home)
    except InstallConflict as exc:
        fail(f"conflict — stopping without changes: {exc}")

    print_plan(home, actions)
    if args.plan:
        return 0

    if not deepseek_key_present():
        fail(
            "DEEPSEEK_API_KEY is not set; installation is gated on it so the "
            "worker is never installed unusable. Set it outside Codex (never "
            "paste it into a prompt), then re-run. --plan previews without it."
        )

    pending = [a for a in actions if a.kind != "unchanged"]
    if pending and not args.yes:
        if not sys.stdin.isatty():
            fail("no TTY for the clearance prompt; re-run with --yes.")
        if input("\nProceed with the plan above? [y/N] ").strip().lower() != "y":
            print("Aborted; nothing written.")
            return 1

    config_toml = home / "config.toml"
    config_before = config_toml.read_bytes() if config_toml.exists() else None

    report = Report(actions=actions)
    for action in pending:
        assert action.apply is not None
        action.apply()

    if (config_toml.read_bytes() if config_toml.exists() else None) != config_before:
        fail("config.toml changed during installation; this must never happen.")

    verify(home, script_dst, report, args.skip_tests)

    print("\nInstalled and verified.")
    for action in actions:
        print(f"  {action.describe()}")
        if action.diff and action.kind == "update":
            print("    " + "\n    ".join(action.diff.splitlines()[:40]))
    print("\nChecks:")
    for check in report.checks:
        print(f"  - {check}")
    for note in report.notes:
        print(f"  - {note}")
    print(
        "\nNext steps:\n"
        "  1. The Hook is NOT runnable until you review and trust its exact\n"
        "     definition via /hooks in Codex. This installer never writes the\n"
        "     hooks.state trust hash.\n"
        "  2. After trusting, start a NEW Codex task so the Hook and agent load\n"
        "     together; a running root task does not prove the Hook reloaded.\n"
        "  3. No paid call was made. When you want a paid smoke test, use\n"
        f"     {UPSTREAM / 'prompts' / 'quick-smoke-test.md'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
