# Root Config Template

A worked template. Copy into `src/<project>/config/__init__.py`, rename, and
add domain sub-models.

```python
"""Root configuration for <project>."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── Sub-models ────────────────────────────────────────────────────────


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_DB_", frozen=True)
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"


class CacheConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_CACHE_", frozen=True)
    backend: str = "memory"
    ttl_seconds: int = 300


class LogConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_LOG_", frozen=True)
    level: str = "INFO"
    file: Path | None = None


# ── Root ──────────────────────────────────────────────────────────────


class AppConfig(BaseModel):
    """Singleton root. Bind exactly once at app entry."""

    model_config = ConfigDict(frozen=True)

    db: DBConfig = Field(default_factory=DBConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    log: LogConfig = Field(default_factory=LogConfig)

    _instance: ClassVar["AppConfig | None"] = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls()  # `BaseSettings` sub-models read env vars on construction

    @classmethod
    def bind(cls, cfg: "AppConfig") -> None:
        if cls._instance is not None:
            raise RuntimeError(
                "AppConfig already bound; call reset_for_tests() first"
            )
        cls._instance = cfg

    @classmethod
    def current(cls) -> "AppConfig":
        if cls._instance is None:
            raise RuntimeError("AppConfig not bound; call bind() at app entry")
        return cls._instance

    @classmethod
    def reset_for_tests(cls) -> None:
        cls._instance = None

    def save(self, path: Path) -> None:
        path.write_text(
            yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
```

## App-Entry Pattern

```python
# src/<project>/__main__.py
def main() -> None:
    AppConfig.bind(AppConfig.from_env())
    cfg = AppConfig.current()
    setup_logging(cfg.log)
    run(cfg)
```

## Test Pattern

```python
@pytest.fixture(autouse=True)
def _reset_config():
    yield
    AppConfig.reset_for_tests()


def test_thing():
    AppConfig.bind(AppConfig(db=DBConfig(host="testdb")))
    ...
```

## Anti-Patterns

```python
# BAD: module-level singleton
_instance: AppConfig | None = None

def get_config() -> AppConfig:
    global _instance
    if _instance is None:
        _instance = AppConfig()      # construction moment is hidden
    return _instance

# BAD: bind() at import time
AppConfig.bind(AppConfig.from_env())  # at module top level

# BAD: yaml.load
yaml.load(path.read_text())          # arbitrary code execution

# BAD: 4-level nesting
class AppConfig(BaseModel):
    services: ServicesConfig          # → DBServicesConfig → ICPDBServicesConfig
                                      #   (split into multiple trees instead)
```
