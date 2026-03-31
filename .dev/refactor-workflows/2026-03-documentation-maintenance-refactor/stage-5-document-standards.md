# Stage 5 Document Standards

## Placement Decision

Stage 5 runtime documentation lives under `.dev/operations/`.

Reason:

- it is project-specific truth
- it is not a business requirement document
- it is not a single-domain production spec
- it is cross-bounded-context runtime and maintenance knowledge

Current rule:

- do not create a top-level `.ops/` directory during this workflow

Migration to `.ops/` should be considered only when runtime operations knowledge becomes independently governed from the rest of `.dev/`.

## Standard Document Set

- `context-map.md`
- `event-catalog.md`
- `mq-topology.md`
- `runbooks/`

## Minimum Completion Rule

Stage 5 should not start by writing arbitrary narratives.

Each runtime document must:

- reference existing requirement/spec truth from Stage 4
- state ownership clearly
- document failure-sensitive behavior explicitly
- be usable by a maintainer during diagnosis or refactoring

## Scope Boundaries

- `context-map.md`
  - bounded context relationships and collaboration rules
- `event-catalog.md`
  - integration event ownership and delivery semantics
- `mq-topology.md`
  - broker/channel routing and retry/dead-letter behavior
- `runbooks/`
  - incident diagnosis and recovery procedures

## Non-Goals

- no environment-specific deployment manuals by default
- no duplication of full payload schemas already owned elsewhere
- no replacing domain specs with runtime summaries
