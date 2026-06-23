#!/usr/bin/env bash
# Warn about uncommitted tracked changes at session end. Never blocks — exits 0.
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
porcelain=$(git -C "$repo_root" status --porcelain 2>/dev/null) || exit 0

[[ -z "$porcelain" ]] && exit 0

# Ignore untracked files (??) — only care about tracked modifications/additions/deletions.
tracked=$(printf '%s\n' "$porcelain" | grep -v '^??' || true)

[[ -z "$tracked" ]] && exit 0

count=$(printf '%s\n' "$tracked" | wc -l | tr -d ' ')
printf 'Reminder: %s file(s) with uncommitted tracked changes — consider committing before you close.\n' "$count" >&2
printf '%s\n' "$tracked" | head -10 | sed 's/^/  /' >&2
[[ "$count" -gt 10 ]] && printf '  ... and %d more\n' "$((count - 10))" >&2

exit 0
