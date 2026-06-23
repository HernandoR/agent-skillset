---
name: loguru-first-logging
description: Use when adding logging to a Python project, when business code uses `print()` or `import logging` directly, when third-party stdlib loggers (urllib3, requests, boto3, torch) bypass the file sink, or when log triage is hard because output is unstructured.
---

# Loguru-First Logging

## Overview

Standardise on `loguru.logger`, ban `print()` and `import logging` in business
code, intercept stdlib loggers from third-party packages, and give every
workflow app a per-workspace file sink with rotation and a start banner. The
skill ships the helper, the rule doc, and the detector.

## When To Use

- A new Python project that will produce diagnostic output beyond a few `print`s.
- An existing project where logs are split between `print()`, `logging.getLogger`,
  and `loguru.logger`.
- A project that wants per-run log files for post-hoc debugging.

## Rules

1. **`from loguru import logger` everywhere in business code.** No `print()`,
   no `import logging`, no `logging.getLogger`.
2. **`InterceptHandler` reroute is mandatory at app entry.** Third-party
   stdlib loggers (urllib3, requests, boto3, torch) silently bypass the file
   sink without it.
3. **File sinks are append + rotation by default.** `rotation="100 MB",
   retention="7 days"`. Truncate-on-start is opt-in for ephemeral CI runs.
4. **`enqueue=True` on the file sink by default** for thread- and
   process-safety. Pure single-threaded tools may opt out for the
   lowest-latency case. See the fork-after-enqueue note below.
5. **Use `logger.bind` / `logger.contextualize` for structured context.**
   Recommended, not required. Recommend `serialize=True` when downstream
   pipelines ingest the JSON.

## Helper Module

Drop [references/log_setup.py](references/log_setup.py) into the project as
`<pkg>/log_setup.py`. It exposes:

- `setup_file_logging(log_dir, *, rotation="100 MB", retention="7 days", enqueue=True)`
- `teardown_file_logging()`
- `log_start_banner(app_name: str, *, banner_context=None)`
- `intercept_stdlib_logging()` — installs `InterceptHandler` on the root
  stdlib logger.

The banner shape is fixed; the project supplies field content via a
`banner_context() -> dict[str, str]` callable.

```text
============================================================
 <app_name> starting at <timestamp>
 <key1>=<value1>  <key2>=<value2>  ...
============================================================
```

## App-Entry Wiring

```python
# src/<pkg>/__main__.py
from loguru import logger
from <pkg>.log_setup import (
    intercept_stdlib_logging, setup_file_logging, log_start_banner
)

def main() -> None:
    intercept_stdlib_logging()
    setup_file_logging(workspace_path)
    log_start_banner("myapp", banner_context=lambda: {"env": "prod", "rev": "a1b2"})
    run()
```

## Fork-After-`enqueue` Footnote

`enqueue=True` spawns a queue thread. Forking after that thread exists
deadlocks the child. Either call `setup_file_logging` **after** spawning
process pools, or set `multiprocessing.set_start_method("spawn")` at module
load.

## Detector Script

Copy [scripts/find_stdlib_logging.py](scripts/find_stdlib_logging.py) into the
target project's `scripts/`. It flags `import logging` and `logging.getLogger`
outside the allow-list (default: `<pkg>/log_setup.py`). Same in-skill +
copy-to-target pattern as `centralized-path-config`.

```bash
uv run python scripts/find_stdlib_logging.py src/
```

## Rule Doc Payload

Drop [references/agents-spec/no-print-no-stdlib-logging.md](references/agents-spec/no-print-no-stdlib-logging.md)
into the target project's `.agents/spec/`. It conforms to the schema enforced
by `agent-spec-convention`.

## Common Mistakes

- Forgetting `intercept_stdlib_logging()` at app entry — third-party logs
  silently bypass the file sink.
- `logger.add(sys.stdout, ...)` scattered through library code (loguru already
  has a default stdout sink; extra `add` calls double-print).
- Truncate-on-start in production — losing the previous run's tail every
  restart.
- Calling `setup_file_logging` before forking a process pool while
  `enqueue=True` (deadlock).

## Related Skills

- `pydantic-config-tree` — log level usually comes from
  `cfg.log.level` at app entry.
- `agent-spec-convention` — schema for the rule doc payload shipped here.
