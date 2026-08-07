set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    just --list

validate:
    uv run python scripts/validate_skills.py
    uv run python scripts/validate_agent_specs.py --check-mirror
    uv run python scripts/validate_vendored.py

fmt:
    uv run ruff format scripts

lint:
    uv run ruff check scripts

ci: fmt lint validate

