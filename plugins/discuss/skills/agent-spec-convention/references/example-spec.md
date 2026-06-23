---
name: example-spec
version: 1
last_updated: 2026-06-03
---

# Example Rule

## Rule

Public functions in `src/` must declare a return-type annotation. Internal
helpers (any function whose name starts with `_`) are exempt.

## Why

Public functions form the project's typed contract: callers, type checkers,
and IDE tooling all depend on the return-type information being explicit.
Inferring return types at every call site makes refactors that change the
inferred type silently break downstream callers.

## Where

- Applies to every `def ` in `src/` whose name does not start with `_`.
- Test fixtures under `tests/` are exempt.
- Generated code under `src/<pkg>/_generated/` is exempt.

## Examples

```python
# BAD: no return-type annotation on a public function
def compute_score(values):
    return sum(values) / len(values)

# GOOD: return-type annotation present
def compute_score(values: list[float]) -> float:
    return sum(values) / len(values)
```

## References

- The project's typing convention (PEP 484, `pyright`, or `mypy`
  configuration in `pyproject.toml`).
- Project lint policy enforcing public-function annotations
  (`ruff` rule `ANN201`).
