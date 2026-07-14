# ADR Index

This directory contains ADR governance and active target-repository decisions.

## Current Contents

| File | Role |
| --- | --- |
| `README.md` | ADR governance guidance |
| `ADR-TEMPLATE.md` | Template for a new ADR |
| `WHEN-TO-CREATE-ADR.MD` | Criteria for creating an ADR |

## Active Decisions

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-001](ADR-001-reasoned-order-state-transitions.md) | Accepted | Require a recorded reason for every actual Order state change while keeping same-state requests as no-ops. |
| [ADR-002](ADR-002-pluggable-durable-messaging.md) | Accepted | Keep durable messaging behind project-owned ports with Wolverine PostgreSQL as the first adapter and broker-free default tests. |

## Status Rule

- Add `ADR-###-<topic>.md` for a new significant structural decision.
- When a decision is fully incorporated into `.dev/standards/`, `.dev/guides/`, or `.ai/`, this index may mark it as retired/landed.
- When there is no active decision record to retain, `INDEX.md` may remain a catalog of governance documents only.

## Naming Rule

- Filename format: `ADR-###-<topic>.md`
- Use a three-digit sequence number for `###`.
- Use English kebab-case for `<topic>`.
