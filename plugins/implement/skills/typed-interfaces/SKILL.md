---
name: typed-interfaces
description: Use when creating or changing public interfaces, exported APIs, cross-language boundaries, schemas, stubs, or type contracts in Python, TypeScript, Rust, or Go.
---

# Typed Interfaces

## Overview

Public interfaces are contracts. Make type information explicit where callers,
tools, or language boundaries depend on it.

## Language Rules

Python:

- Add annotations for public functions, methods, and class attributes.
- Keep `.pyi`, `py.typed`, generated bindings, and runtime exports in sync when
  they exist.
- Use precise collection and optional types instead of `Any` unless the boundary
  is intentionally dynamic.

TypeScript:

- Type exported functions, props, events, and data models.
- Prefer named exported types for shared contracts.
- Avoid widening public return values through inference when callers depend on
  the shape.

Rust:

- Keep public signatures precise and avoid panics across FFI or external
  boundaries.
- Convert errors into the established public error type.
- Treat feature flags and trait bounds as part of the API.

Go:

- Define exported structs, interfaces, and function signatures deliberately.
- Document exported identifiers when required by local lint policy.
- Keep JSON tags, validation tags, and wire formats aligned with the contract.

## Cross-Language Boundaries

When data crosses languages or processes, define the shape once and verify every
binding or stub stays aligned with it. Tests should exercise the boundary, not
only the internal implementation.

## Common Mistakes

- Updating runtime exports but not stubs.
- Relying on inference for public contracts.
- Treating serialization tags as incidental implementation details.

