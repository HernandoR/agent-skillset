"""Verify vendored upstream payloads against their pinned manifests.

Every ``plugins/*/skills/*/assets/MANIFEST.json`` must list a sha256 for each
file under the sibling ``upstream/`` tree, and every listed file must exist
with a matching hash. This keeps offline installers honest: what they copy is
byte-identical to the pinned upstream commit.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_MANIFEST_KEYS = {"upstream", "commit", "files"}


def validate_manifest(manifest_path: Path) -> list[str]:
    rel = manifest_path.relative_to(REPO_ROOT)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel} invalid JSON: {exc}"]

    errors: list[str] = []
    missing_keys = REQUIRED_MANIFEST_KEYS - set(manifest)
    if missing_keys:
        errors.append(f"{rel} missing keys: {', '.join(sorted(missing_keys))}")
        return errors

    upstream_dir = manifest_path.parent / "upstream"
    if not upstream_dir.is_dir():
        return errors + [f"{rel}: sibling upstream/ directory missing"]

    listed = manifest["files"]
    on_disk = {
        str(p.relative_to(upstream_dir)): p
        for p in sorted(upstream_dir.rglob("*"))
        if p.is_file()
    }

    for name in sorted(set(listed) - set(on_disk)):
        errors.append(f"{rel}: listed file missing on disk: {name}")
    for name in sorted(set(on_disk) - set(listed)):
        errors.append(f"{rel}: unlisted file in upstream/: {name}")
    for name in sorted(set(listed) & set(on_disk)):
        digest = hashlib.sha256(on_disk[name].read_bytes()).hexdigest()
        if digest != listed[name]:
            errors.append(f"{rel}: sha256 mismatch for {name}")

    return errors


def main() -> int:
    manifests = sorted(REPO_ROOT.glob("plugins/*/skills/*/assets/MANIFEST.json"))
    orphans = [
        d
        for d in REPO_ROOT.glob("plugins/*/skills/*/assets/upstream")
        if d.is_dir() and not (d.parent / "MANIFEST.json").exists()
    ]

    errors: list[str] = []
    for orphan in orphans:
        errors.append(f"{orphan.relative_to(REPO_ROOT)} has no MANIFEST.json")
    for manifest in manifests:
        errors.extend(validate_manifest(manifest))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Vendored payload validation passed ({len(manifests)} manifest(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
