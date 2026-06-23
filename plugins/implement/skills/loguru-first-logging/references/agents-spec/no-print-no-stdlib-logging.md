<!-- Drop into target project as `.agents/spec/no-print-no-stdlib-logging.md`. -->

---
name: no-print-no-stdlib-logging
version: 1
last_updated: 2026-06-03
---

# No `print()`, No Stdlib `logging` In Business Code

## Rule

Business code must use `from loguru import logger` for diagnostic output. The
following are forbidden in any module outside the project's `log_setup.py`:

- `print(...)` for diagnostics, progress, or debugging output.
- `import logging`, `from logging import ...`, `logging.getLogger(...)`.
- `logger.add(sys.stdout, ...)` scattered through library code (loguru
  already has a default stdout sink).

The single allowed site for `import logging` is the project's `log_setup.py`,
where it appears solely to install the `InterceptHandler` that reroutes
stdlib loggers (urllib3, requests, boto3, torch, …) to loguru.

## Why

Mixed `print` / `logging` / `loguru` output makes log triage and post-hoc
debugging painful: each source has its own format, file location, and
buffering behaviour. Centralising on loguru gives a single sink, a single
format, deterministic flush behaviour, file rotation, and (with
`InterceptHandler`) coverage of third-party libraries that only know how to
talk to stdlib `logging`.

## Where

- One file per project — `<pkg>/log_setup.py` — owns sink construction,
  banner emission, and the stdlib intercept install.
- App entry calls `intercept_stdlib_logging()` and `setup_file_logging(...)`
  before any business logic runs.
- Test fixtures call `teardown_file_logging()` between tests if they swap
  workspaces.

## Examples

```python
# BAD: print() in business code
def process(item):
    print(f"Processing {item}")

# BAD: stdlib logging in business code
import logging
log = logging.getLogger(__name__)

def process(item):
    log.info("Processing %s", item)

# BAD: scattered file sink
from loguru import logger
logger.add(sys.stdout, level="INFO")    # double-prints, hides config drift

# GOOD: loguru everywhere in business code
from loguru import logger

def process(item):
    logger.info("Processing {}", item)

# GOOD: stdlib intercept (only in log_setup.py)
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger.opt(depth=6, exception=record.exc_info).log(
            record.levelname, record.getMessage()
        )

def intercept_stdlib_logging():
    logging.basicConfig(handlers=[InterceptHandler()], force=True)
```

## References

- The project's `<pkg>/log_setup.py` module — single source of truth
  for sink construction, banner emission, and stdlib intercept.
- The `loguru-first-logging` skill — template helper, banner contract,
  and `find_stdlib_logging.py` detector.
