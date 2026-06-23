---
name: pydantic-config-tree
description: Use when a project has hyperparameters or behavioural settings scattered across modules, environment variables, or ad-hoc config classes, and a single typed root model with domain-grouped sub-models, env-var binding, and YAML round-trip is wanted.
---

# Pydantic Config Tree

## Overview

A typed, frozen root model with domain-grouped sub-models, env-var binding,
and YAML persistence is the recurring shape for medium-to-large Python
pipelines. This skill ships the template and the rules that keep the tree
maintainable: classmethod-based singleton hooks, `pydantic-settings` defaults,
flat-by-default with a hard nesting cap.

## When To Use

- A project has > ~30 settings and they live as scattered constants, env vars,
  or per-module config dataclasses.
- You're about to add another `MyComponentConfig` and the project has three of
  them already.
- Settings need YAML round-trip for human review or persistence.

Do not use for projects with < 10 settings — a single dataclass plus
`os.environ` is fine.

## Singleton Pattern

Singleton is **recommended, not required, and never module-level**. Module-level
`_instance = None` patterns hide the construction moment. Use classmethod hooks
on the root model:

```python
class AppConfig(BaseModel):
    @classmethod
    def bind(cls, cfg: "AppConfig") -> None:
        if cls._instance is not None:
            raise RuntimeError("AppConfig already bound; reset_for_tests first")
        cls._instance = cfg

    @classmethod
    def current(cls) -> "AppConfig":
        if cls._instance is None:
            raise RuntimeError("AppConfig not bound; call bind() at app entry")
        return cls._instance

    @classmethod
    def reset_for_tests(cls) -> None:
        cls._instance = None
```

Construction is grep-able: `AppConfig.bind(AppConfig.from_env())` at app entry
appears at one site.

## Env-Var Loading

`pydantic-settings` is the default. Use `BaseSettings` on the root or
sub-models with a project-wide `env_prefix`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_DB_", frozen=True)
    host: str = "localhost"
    port: int = 5432
```

Hand-written `from_env()` is the documented fallback for projects with sparse
env coverage (≤ 5 vars) or migrations off a legacy reader. See
[references/from-env-fallback.md](references/from-env-fallback.md).

## YAML Round-Trip

YAML is the default. **`yaml.safe_load` is mandatory**; `yaml.load` is a
remote-code-execution footgun.

```python
import yaml

def save(cfg: AppConfig, path: Path) -> None:
    path.write_text(yaml.safe_dump(cfg.model_dump(mode="json"), sort_keys=False))

def load(path: Path) -> AppConfig:
    return AppConfig.model_validate(yaml.safe_load(path.read_text()))
```

Adopters who must use JSON or TOML do a one-line `import` swap; no shipped
adapter.

## Nesting Discipline

- **Flat by default**: root → 5-ish sub-models. Add a sub-model only when it
  owns ≥ 3 fields.
- **Hard cap: three layers** (root → sub-model → sub-sub-model). Beyond three,
  env-var paths get unreadable; the signal is to split into multiple config
  trees, not deepen one.

See [references/root-template.md](references/root-template.md) for the worked
shape.

## Common Mistakes

- Defining `_instance = None` as a module-level variable instead of a
  classmethod-managed slot.
- Using `yaml.load` instead of `yaml.safe_load`.
- Adding a fourth nesting level "because the domain is hierarchical" — split
  the project into multiple trees instead.
- Letting two sub-models own < 3 fields each just to mirror the directory
  structure. Flatten.
- Calling `bind()` from inside a library import (binds at import time, hides
  the construction moment).

## Related Skills

- `centralized-path-config` — companion for path config; cross-link only.
- `loguru-first-logging` — config tree often binds the log level at app
  entry.
