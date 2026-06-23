# Dataclass Fallback

For projects that cannot take a pydantic v2 dependency, use a frozen
`@dataclass` with the same three-axis taxonomy.

```python
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PathConfig:
    mount_dir: Path = Path("/mnt/data")
    env: str = "local"
    archive_timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
    )

    @property
    def output_root(self) -> Path:
        return self.mount_dir / "outputs" / self.env

    @property
    def cache_root(self) -> Path:
        return self.output_root / "cache"

    def for_scope(self, scope_id: str) -> "ScopedPaths":
        # `replace` cannot widen the type, so build the subclass explicitly.
        return ScopedPaths(
            mount_dir=self.mount_dir,
            env=self.env,
            archive_timestamp=self.archive_timestamp,
            scope_id=scope_id,
        )


@dataclass(frozen=True, slots=True)
class ScopedPaths(PathConfig):
    scope_id: str = ""

    @property
    def workspace(self) -> Path:
        return self.output_root / self.scope_id

    def per_frame_json(self, frame_id: str) -> Path:
        return self.workspace / "frames" / f"{frame_id}.json"
```

## Trade-offs vs Pydantic

| Concern | Pydantic v2 | dataclass |
|---|---|---|
| Validation | Field validation, coercion, regex, ranges | None — only the type checker |
| Serialization | `model_dump()` / `model_dump_json()` built-in | `dataclasses.asdict()` works only for primitives |
| Frozen + hashable | `model_config = ConfigDict(frozen=True)` | `@dataclass(frozen=True)` |
| Subclass field defaults | Mandatory keyword args supported | Must give every field a default if any parent field has one |
| Dependency cost | Adds pydantic to the dependency tree | None |

The main awkwardness is that `dataclass` subclasses must give every new field
a default once a parent field has one (hence `scope_id: str = ""` above plus a
runtime check, or use `kw_only=True` on Python 3.10+:
`@dataclass(frozen=True, slots=True, kw_only=True)`).
