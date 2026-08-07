---
name: install-codex-deepseek-subagent
description: Use when the user asks to install, update, or repair the DeepSeek V4 Flash custom subagent for Codex — the standalone agent TOML, the use-v4-flash-worker handoff skill, and the SubagentStart plaintext-handoff Hook. Fully offline; the payload is vendored in this skill and installed by a bundled script, no GitHub access needed. Installation only proceeds when DEEPSEEK_API_KEY is already set in the environment.
---

# Install Codex DeepSeek Subagent

## Overview

Installs the native DeepSeek V4 Flash custom subagent (from
Utopia-V/codex-deepseek-subagent) into the user's personal Codex configuration
without any network access. Everything needed is bundled:

- `assets/upstream/` — byte-exact vendored copy of the upstream payload
  (agent TOML for both platforms, the `use-v4-flash-worker` skill, hook
  scripts, hook example JSONs, `snippets/AGENTS.md`, protocol tests, the
  quick-smoke-test prompt, and the upstream MIT LICENSE).
- `assets/MANIFEST.json` — pinned upstream commit plus per-file sha256.
  Integrity is enforced by this repository's `just validate`, not at install
  time.
- `scripts/install.py` — the installer. Stdlib-only, Python 3.11+ (assume
  `uv`/`python` is available).
- `references/install-with-codex.md` — the verbatim upstream install prompt;
  authoritative wording for the invariants the script implements.

## How to Install

Precondition: `DEEPSEEK_API_KEY` must already be set in the environment the
installer runs in. The script checks presence only (never the value) and
refuses to write anything without it — an installed worker with no key would
be dead weight. If it is missing, tell the user to set it outside Codex (never
pasted into a prompt or a file) and stop; `--plan` still works for a preview.

Run the bundled installer instead of performing steps by hand:

```bash
python3 scripts/install.py --plan   # print the full plan, write nothing
python3 scripts/install.py --yes    # install, verify, report (non-interactive)
```

Without flags it prints the plan and asks for one clearance on a TTY. Show the
user the plan output before or alongside execution — the whole blast radius in
one screen, one clearance, no per-step prompting. `--codex-home PATH` overrides
`CODEX_HOME`/`~/.codex`; `--skip-tests` skips the local protocol test.

The script is idempotent: unchanged targets are reported as `unchanged`, a
re-run after success is a no-op, and the marked `AGENTS.md` block and hook
entry are replaced in place rather than duplicated.

## What the Script Enforces

The invariants come from the upstream install prompt (see `references/`):

- The main model, provider, login, and every unrelated Hook stay untouched;
  `config.toml` is asserted byte-identical before and after.
- Agent registration and `[model_providers.deepseek]` live only in the
  standalone `agents/v4-flash-worker.toml`, never in `config.toml`.
- No key handling: the only secret name is the `DEEPSEEK_API_KEY` environment
  variable. Its presence is a hard precondition for installing; the report
  states presence as a boolean, never a value.
- No paid provider call: verification is TOML/JSON assertions plus the vendored
  offline protocol test (collision rejection, exact-role delivery, marker
  preservation, one-shot consumption, replay rejection, expiry recovery).
- Hook trust stays with the user: the script never writes the `hooks.state`
  trust hash; the Hook is not runnable until reviewed via `/hooks`.

## When the Script Stops

The installer exits without writing anything when an existing artifact at an
intended identity serves a different purpose: a foreign agent in
`v4-flash-worker.toml`, a foreign skill at `skills/use-v4-flash-worker`,
invalid JSON in `hooks.json`, inline Hook configuration in `config.toml`
(TOML merging is out of scope — merge the vendored example entry manually),
or a start marker without an end marker in `AGENTS.md`. Report the conflict to
the user and let them decide; do not override.

## After Installing

1. The user must review and trust the Hook via `/hooks` in Codex.
2. A new Codex task must be started after trusting, so the Hook and agent
   configuration load together.
3. Run a paid smoke test only when the user asks, using the vendored
   `assets/upstream/prompts/quick-smoke-test.md`.

Windows note: the script selects the Windows agent TOML variant and the
PowerShell hook script, but this branch is untested here — verify with the
vendored `assets/upstream/tests/plaintext-handoff.windows.ps1`.

## Updating the Vendored Payload

Maintenance only (needs network, runs in this repository, never at install
time): re-fetch the upstream files at a new commit into `assets/upstream/`,
regenerate the hashes in `assets/MANIFEST.json`, run `just validate`, and bump
the bundle version.
