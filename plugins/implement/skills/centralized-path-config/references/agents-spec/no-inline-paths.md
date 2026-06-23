<!-- Drop into target project as `.agents/spec/no-inline-paths.md`. Edit the
two placeholder class/module references before committing. -->

---
name: no-inline-paths
version: 1
last_updated: 2026-06-03
---

# No Inline Path Concatenation

## Rule

Business logic must not introduce inline path concatenation with path-segment
literals, including the `Path(...) / "literal" / "literal"` form. Path
generation belongs in the project's path-config module
(`src/<project>/configs/path_config.py` by default).

## Why

When directory names live as string literals across many modules, renaming
or moving a directory turns into a hunt across the codebase, with the
constant risk of missing one site or introducing a subtle off-by-one in
the path tree. Centralising path agreements lets the storage layout
refactor in one place, makes IDE "Go to definition" resolve to the
canonical spec, and lets a single-line lint rule prevent regressions.

## Where

- `src/<project>/configs/path_config.py` is the only module allowed to
  contain path-segment string literals used to assemble paths.
- New child paths should reuse the nearest existing parent `@property`
  rather than rebuild segments from the root.
- Path generation must not be implemented as `@staticmethod`. Derived
  paths must be built from instance attributes so callers use a
  configuration instance.
- Three axes for path entries:
  - **Constructor / model fields** — runtime variables (mount roots,
    environment IDs, scope IDs).
  - **`@property` (no parameters)** — fixed directory and file names
    chosen by the implementation.
  - **Instance method (parameterised)** — final segment depends on a
    per-call value.

## Examples

```python
# BAD: inline concatenation in business code
def export_manifest(scope_id: str, mount: Path) -> None:
    out = mount / "outputs" / "local" / scope_id / "manifest.json"
    out.write_text("{}")

# BAD: rebuilding segments instead of reusing a parent property
class ScopedPaths(PathConfig):
    @property
    def per_scope_cache(self) -> Path:
        return self.mount_dir / "outputs" / self.env / "cache" / self.scope_id

# BAD: @staticmethod for path generation
class PathConfig(BaseModel):
    @staticmethod
    def per_frame(scope_id: str, frame_id: str) -> Path:
        return Path("/mnt/data") / scope_id / f"{frame_id}.json"

# GOOD: business code uses the config tree
def export_manifest(paths: ScopedPaths) -> None:
    paths.manifest_json.write_text("{}")

# GOOD: child path reuses the parent property
class ScopedPaths(PathConfig):
    @property
    def per_scope_cache(self) -> Path:
        return self.cache_root / self.scope_id
```

## References

- The project's `<pkg>/configs/path_config.py` module — single source of
  truth for path agreements.
- The `centralized-path-config` skill — template, decision tree, and
  `find_inline_paths.py` detector.
