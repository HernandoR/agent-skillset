# Hand-Written `from_env()` Fallback

Use this when:

- The project has ≤ 5 environment variables — `pydantic-settings` is more
  ceremony than the win is worth.
- A legacy env-reader (e.g. an internal `prod_get_env_value` wrapper, a
  feature-flag service) must be invoked instead of bare `os.environ.get`.
- You're mid-migration off such a reader and want one place to flip the
  source.

## Shape

```python
import os
from pydantic import BaseModel, ConfigDict, Field

class DBConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    host: str = "localhost"
    port: int = 5432

    @classmethod
    def from_env(cls) -> "DBConfig":
        return cls(
            host=os.environ.get("MYAPP_DB_HOST", "localhost"),
            port=int(os.environ.get("MYAPP_DB_PORT", "5432")),
        )
```

## Wrapping a Legacy Reader

```python
from myapp._legacy import prod_get_env_value


def _env(key: str, default: str) -> str:
    # Legacy reader during transition; swap to os.environ after migration.
    return prod_get_env_value(key, default)


class DBConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    host: str = "localhost"

    @classmethod
    def from_env(cls) -> "DBConfig":
        return cls(host=_env("MYAPP_DB_HOST", "localhost"))
```

## Migration Path To `pydantic-settings`

1. Add `pydantic-settings` to dependencies.
2. Convert one sub-model at a time: replace its `BaseModel` with `BaseSettings`
   and add a `model_config = SettingsConfigDict(env_prefix=...)`.
3. Delete the corresponding `from_env()` classmethod.
4. The root `AppConfig.from_env()` shrinks one defaulted call at a time:
   `cls(db=DBConfig.from_env())` → `cls(db=DBConfig())` → `cls()`.

Keep both shapes in the project only as long as the migration is in flight.
The endpoint is one shape per project.
