---
name: centralized-path-config
description: Use when adding or refactoring filesystem paths in a project that assembles paths from runtime variables and directory-name literals (pipelines, ETL, ML training, build output trees), or when reviewing code that imports `pathlib.Path` together with string segments.
---

# Centralized Path Config

## Overview

Inline path concatenation (`Path(...) / "literal" / "literal"`) scattered across
business logic turns the storage layout into a refactor minefield. This skill
ships a **typed, frozen, tree-shaped path-config module** as the single source
of truth, plus the rule doc and detector script to keep it that way.

## When To Use

- Adding any new derived path that contains a directory name or filename literal.
- Onboarding a project where path literals already appear in `>1` business module.
- Reviewing changes that import `pathlib.Path` together with string literals.

Do not use for projects with a single path (`./output`); the overhead is not
worth it.

## Three-Axis Taxonomy

Every path entry must live on one of three axes. The decision rule is:

| Layer | What lives here | Decision rule |
|---|---|---|
| Constructor / model fields | Mount roots, environment IDs, scope IDs (POI, clip), sensor aliases | Changes per process invocation |
| `@property` (no parameters) | Fixed directory and file names chosen by the implementation | Stable for a given set of init attributes |
| Instance method (parameterised) | Final segment depends on a per-call value (frame id, group id, timestamp) | Varies per call |

`@staticmethod` for path generation is forbidden — callers must use a config
instance, not class-level helpers.

A new `@property` MUST reuse the nearest existing parent property rather than
rebuild segments from the root.

## Recommended Shape

Pydantic v2 frozen models are the primary template. See
[references/pydantic-template.md](references/pydantic-template.md) for the full
worked example. The shape:

```python
from pydantic import BaseModel, ConfigDict, Field

class PathConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    mount_dir: Path = Field(default=Path("/mnt/data"))
    env: str = Field(default="local")

    @property
    def output_root(self) -> Path:
        return self.mount_dir / "outputs" / self.env

    def for_scope(self, scope_id: str) -> "ScopedPaths":
        return ScopedPaths(scope_id=scope_id, **self.model_dump())


class ScopedPaths(PathConfig):
    scope_id: str

    @property
    def workspace(self) -> Path:
        return self.output_root / self.scope_id

    def per_frame_json(self, frame_id: str) -> Path:
        return self.workspace / f"{frame_id}.json"
```

Factory methods live on the base class (`for_scope`, `for_clip`, `for_poi`),
not as module-level free functions. Module-level singletons are rejected
because they hide the construction moment.

For projects that cannot take the pydantic dependency, see
[references/dataclass-fallback.md](references/dataclass-fallback.md).

## Time-Derived Paths

Never call `datetime.now()` inside a `@property` — it makes the value flicker
across calls. Use an optional init-attribute with a `default_factory`:

```python
archive_timestamp: str = Field(
    default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
)

@property
def archive_path(self) -> Path:
    return self.output_root / "archive" / self.archive_timestamp
```

## Rule Doc Payload

Drop [references/agents-spec/no-inline-paths.md](references/agents-spec/no-inline-paths.md)
into the target project's `.agents/spec/no-inline-paths.md`. The payload
conforms to the schema enforced by `agent-spec-convention`. Edit the placeholder
class names and module path before committing.

## Detector Script

Copy [scripts/find_inline_paths.py](scripts/find_inline_paths.py) into the
target project's `scripts/`. It is stdlib-only and accepts `--allow` to extend
the default allow-list (the path-config module itself).

```bash
uv run python scripts/find_inline_paths.py src/
uv run python scripts/find_inline_paths.py --allow src/myproj/configs/path_config.py src/
```

Updates flow skill → re-copy. Wire it into `just lint` or pre-commit.

## Workflow

1. Read [references/extension-decision-tree.md](references/extension-decision-tree.md)
   before adding any new path.
2. Pick the axis (init / `@property` / method) using the three-axis rule.
3. Reuse the nearest existing parent property — do not rebuild from the root.
4. Run the detector before committing.

## Common Mistakes

- Adding a `@property` that rebuilds segments instead of reusing a parent
  property.
- Using `@staticmethod` for path generation.
- Calling `datetime.now()` inside a `@property`.
- Re-deriving the layout in tests by string-concatenation.
- Defining module-level free functions like `build_clip_paths(cfg, ...)`
  instead of a factory method on the base class.

## Related Skills

- `pydantic-config-tree` — companion for hyperparameter / behavioural config.
  Cross-link only; no shared layout doc.
- `agent-spec-convention` — schema for the rule doc payload shipped here.
