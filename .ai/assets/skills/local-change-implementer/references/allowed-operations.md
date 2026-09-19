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

## Outside Local Scope

Use `../../../shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md` for selection.
The following operations cannot execute in the local skill. A settled, accepted
design can enter a bounded slice directly; architecture work is needed only
for an actual missing or changed decision:

- extract a public or responsibility-changing class
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
- introducing a public, responsibility-changing, dependency/lifetime/transaction-affecting
  class or an interface. A private implementation helper type may remain local
  only when it preserves the accepted target, radius, behavior, responsibility,
  dependency direction, lifetime, and transaction boundary.

The primary target, direct call sites and immediate tests may span several
files inside the allowed module/radius. That file count alone is not expansion.
