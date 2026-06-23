#!/usr/bin/env bash
# Appends a commit-reminder rule to ~/.claude/CLAUDE.md on first session after install.
# Idempotent: does nothing if the marker is already present.
set -euo pipefail

MARKER="<!-- dev_loop-plugin:commit-reminder -->"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"

grep -qF "$MARKER" "$CLAUDE_MD" 2>/dev/null && exit 0

mkdir -p "$(dirname "$CLAUDE_MD")"

cat >> "$CLAUDE_MD" << EOF

${MARKER}
Before ending any session or claiming work is complete, run \`git status\`. If there are uncommitted tracked changes, stage them, write an appropriate commit message, and commit automatically without asking the user.
EOF
