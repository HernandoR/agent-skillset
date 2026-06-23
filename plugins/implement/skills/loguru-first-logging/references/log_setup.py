"""Loguru-first logging helper.

Drop into a project as ``<pkg>/log_setup.py`` and call
``intercept_stdlib_logging`` and ``setup_file_logging`` from the app entry
point.

Public surface
--------------

- ``intercept_stdlib_logging()`` — reroute stdlib ``logging`` (and any
  third-party logger that uses it) to loguru.
- ``setup_file_logging(log_dir, ...)`` — add a per-app file sink with
  rotation. Returns the sink id so callers can compose teardown.
- ``teardown_file_logging()`` — remove the active file sink, if any.
- ``log_start_banner(app_name, banner_context=None)`` — emit a fixed-shape
  start banner. ``banner_context`` is an optional callable returning a
  ``dict[str, str]`` of fields the project wants surfaced.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from loguru import logger

_FILE_SINK_ID: int | None = None


class InterceptHandler(logging.Handler):
    """Reroute stdlib ``logging`` records to loguru.

    Adapted from the loguru documentation. Preserves the original log level,
    exception info, and walks back to the user frame so file/line attribution
    matches what loguru's own callers would see.
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin glue
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = sys._getframe(6)
        depth = 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def intercept_stdlib_logging(level: int = logging.NOTSET) -> None:
    """Install ``InterceptHandler`` on the root stdlib logger.

    After this call, any module that does ``logging.getLogger(...).info(...)``
    is captured by loguru. Set ``level`` to filter at the stdlib boundary
    (default: capture everything and let loguru filter).
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=level, force=True)


def setup_file_logging(
    log_dir: Path,
    *,
    rotation: str = "100 MB",
    retention: str = "7 days",
    enqueue: bool = True,
    level: str = "DEBUG",
    filename: str = "app.log",
    fmt: str = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    ),
) -> int:
    """Add a per-workspace file sink in append mode with rotation.

    Replaces any previous sink installed by this helper. Returns the loguru
    sink id so advanced callers can compose teardown.
    """
    global _FILE_SINK_ID

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    teardown_file_logging()

    _FILE_SINK_ID = logger.add(
        str(log_dir / filename),
        level=level,
        format=fmt,
        rotation=rotation,
        retention=retention,
        enqueue=enqueue,
        mode="a",
    )
    return _FILE_SINK_ID


def teardown_file_logging() -> None:
    """Remove the active file sink, if one was installed by this helper."""
    global _FILE_SINK_ID
    if _FILE_SINK_ID is not None:
        try:
            logger.remove(_FILE_SINK_ID)
        except ValueError:
            pass
        _FILE_SINK_ID = None


def log_start_banner(
    app_name: str,
    *,
    banner_context: Callable[[], dict[str, str]] | None = None,
    sep_width: int = 60,
) -> None:
    """Emit a fixed-shape start banner.

    The shape is::

        ============================================================
         <app_name> starting at <timestamp>
         <key1>=<value1>  <key2>=<value2>  ...
        ============================================================

    Field content comes from ``banner_context()``. If absent, the body line
    is omitted.
    """
    sep = "=" * sep_width
    timestamp = datetime.now().isoformat(timespec="seconds")
    fields = banner_context() if banner_context is not None else {}
    field_line = "  ".join(f"{k}={v}" for k, v in fields.items())

    if field_line:
        logger.info(
            "\n{sep}\n {app} starting at {ts}\n {fields}\n{sep}",
            sep=sep,
            app=app_name,
            ts=timestamp,
            fields=field_line,
        )
    else:
        logger.info(
            "\n{sep}\n {app} starting at {ts}\n{sep}",
            sep=sep,
            app=app_name,
            ts=timestamp,
        )
