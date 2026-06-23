# Pydantic v2 Path-Config Template

A worked template for a tree-shaped path config. Copy into
`src/<project>/configs/path_config.py` and rename classes for the project.

```python
"""Unified path protocol for the <project> pipeline.

This module is the single place where path agreements are encoded. Treat these
classes as a tree:

- Constructor fields hold runtime variables (mount roots, environment IDs,
  scope IDs).
- ``@property`` values encode fixed directory and file names.
- Instance methods derive paths whose final segment depends on a per-call
  value.

When adding a new path, reuse the nearest existing parent property instead of
rebuilding segments from the root.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class PathConfig(BaseModel):
    """Runtime roots and shared derived paths.

    Fields describe runtime context. Properties describe stable path
    agreements. Do not add ``@staticmethod`` builders.
    """

    model_config = ConfigDict(frozen=True)

    mount_dir: Path = Field(default=Path("/mnt/data"))
    env: str = Field(default="local")
    archive_timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
    )

    @property
    def output_root(self) -> Path:
        return self.mount_dir / "outputs" / self.env

    @property
    def cache_root(self) -> Path:
        return self.output_root / "cache"

    @property
    def archive_root(self) -> Path:
        return self.output_root / "archive" / self.archive_timestamp

    def for_scope(self, scope_id: str) -> "ScopedPaths":
        return ScopedPaths(scope_id=scope_id, **self.model_dump())


class ScopedPaths(PathConfig):
    """Per-scope branch of the path tree.

    ``scope_id`` is the runtime variable for this branch. New scope-local
    paths should derive from ``workspace`` or ``scope_cache``.
    """

    scope_id: str

    @property
    def workspace(self) -> Path:
        return self.output_root / self.scope_id

    @property
    def scope_cache(self) -> Path:
        return self.cache_root / self.scope_id

    @property
    def manifest_json(self) -> Path:
        return self.workspace / "manifest.json"

    def per_frame_json(self, frame_id: str) -> Path:
        return self.workspace / "frames" / f"{frame_id}.json"

    def per_group_dir(self, group_id: str) -> Path:
        return self.workspace / "groups" / group_id
```

## Notes

- `model_config = ConfigDict(frozen=True)` makes the config hashable and lets
  `@lru_cache` cache factory results when needed.
- `for_scope` is a factory method on the base class. Module-level free
  functions like `build_scope_paths(cfg, ...)` are deprecated.
- Use `Path` types in fields, not `str`. Pydantic coerces.
- For `@lru_cache` on factories: cache the call site (e.g. wrap
  `for_scope` with `@lru_cache(maxsize=128)` via a thin module-level helper)
  only when profiling shows it matters.

## What Not To Do

```python
# BAD: @staticmethod for path generation
class PathConfig(BaseModel):
    @staticmethod
    def per_frame(scope_id: str, frame_id: str) -> Path:
        return Path("/mnt/data") / scope_id / f"{frame_id}.json"

# BAD: datetime.now() inside @property
class PathConfig(BaseModel):
    @property
    def archive_root(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")  # flickers per call
        return self.output_root / "archive" / ts

# BAD: rebuilding segments instead of reusing parent property
class ScopedPaths(PathConfig):
    @property
    def per_scope_cache(self) -> Path:
        # Should reuse self.cache_root / self.scope_id
        return self.mount_dir / "outputs" / self.env / "cache" / self.scope_id
```
