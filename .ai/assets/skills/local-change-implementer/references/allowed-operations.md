# Allowed Operations

This skill is optimized for local technical changes.

## Preferred Operations

- extract method
- rename local symbol
- small code fix inside one class or object
- small SQL/ORM implementation adjustment
- move a small responsibility between directly related members
- simplify one local object interaction
- update direct call sites

## Requires Architect Or Slice Review First

These operations are out of scope and should first be reviewed by `ddd-ca-hex-architect` or planned as a `slice-implementer` task:

- extract class
- extract interface
- introduce a new abstraction boundary
- change dependency direction
- rename terms that affect ubiquitous language, DTOs, APIs, events, or boundary semantics
- cross-module behavior change

## Default Scope Limit

One primary target plus:

- direct dependencies;
- direct call sites;
- immediate tests when necessary.

## Disallowed Expansion

Do not expand into:

- multiple aggregates;
- multiple modules;
- broad namespace/package restructuring;
- architecture boundary changes;
- large cross-cutting rename campaigns;
- introducing new classes or interfaces without prior architecture review.
