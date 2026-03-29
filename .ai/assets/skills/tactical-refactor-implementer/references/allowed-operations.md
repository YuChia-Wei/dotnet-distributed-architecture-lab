# Allowed Operations

This skill is optimized for local structural refactoring operations.

## Preferred Operations

- extract method
- rename symbol
- move a small responsibility between directly related classes
- simplify one local object interaction

## Requires Architect Review First

These operations are out of scope for this skill and should first be reviewed by `ddd-ca-hex-architect`:

- extract class
- extract interface
- renames that affect ubiquitous language, DTOs, APIs, events, or boundary semantics

## Default Scope Limit

One primary target plus:

- direct dependencies
- direct call sites
- immediate tests when necessary

## Disallowed Expansion

Do not expand into:

- multiple aggregates
- multiple modules
- broad namespace/package restructuring
- architecture boundary changes
- large cross-cutting rename campaigns
- introducing new classes or interfaces without prior architect review
