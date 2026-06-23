# Path Extension Decision Tree

Before adding a new path, walk this tree.

```text
Q1: Does the path contain a runtime variable that the caller already
    supplied at PathConfig construction time (mount root, env, scope id)?
    → YES: build the path from that field via `@property`. Skip to Q3.
    → NO:  go to Q2.

Q2: Does the path's final segment depend on a value the caller chooses
    PER CALL (frame id, group id, timestamp set inside this call)?
    → YES: expose as an instance method with that value as a parameter.
           Done.
    → NO:  the path needs a NEW runtime variable. Add a constructor field
           with the right default, then expose the path as `@property`.
           Skip to Q3.

Q3: Is there an existing parent property whose value this path extends?
    → YES: reuse it. `return self.<parent_property> / "<new-segment>"`.
           Done.
    → NO:  add the path at the highest reusable level. Done.
```

## Examples

| Path needed | Axis | Reason |
|---|---|---|
| `/mnt/data/outputs/local/scope-42/frames/0001.json` | method `per_frame_json(frame_id)` on `ScopedPaths` | Final segment changes per call. |
| `/mnt/data/outputs/local/scope-42/manifest.json` | `@property manifest_json` on `ScopedPaths` | Stable per-scope file. |
| `/mnt/data/outputs/local/cache` | `@property cache_root` on `PathConfig` | Stable global path. |
| `/mnt/data/outputs/local/archive/20260603_120000/...` | init field `archive_timestamp` + `@property archive_root` | Timestamp is fixed for the run; `default_factory` captures it once. |
| `/<custom-mount>/outputs/local/...` | init field `mount_dir` | Caller picks per process. |

## Anti-Examples

- "It's just one literal" → still belongs in the config module. The detector
  exists to catch the next nine.
- "I'll inline it now and refactor later" → the consolidation work that
  produced this skill came from exactly this rationalisation, multiplied by
  twenty.
- "It's a test, the rule doesn't apply" → tests breaking when the layout
  changes is precisely the cost the rule prevents. Tests must use the same
  config classes.

## Forbidden Shapes

- `@staticmethod` for path generation. Forces callers to instantiate the
  config class.
- Module-level `build_<scope>_paths(cfg, ...)` factories. Use a method on
  the base class instead.
- `datetime.now()` inside `@property`. Use a `default_factory` init field.
- `Path(some_path) / "literal"` in business code. The literal lives in the
  config module.
