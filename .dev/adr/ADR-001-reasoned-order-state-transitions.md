# ADR-001: Reasoned Order State Transitions

## Status

Accepted

## Date

2026-07-13

## Context

The Orders bounded context is an architecture lab and must demonstrate an auditable lifecycle without inventing a commercial transition restriction that has not been approved. The current aggregate allows every transition to a different terminal/lifecycle status, but it neither records why the change occurred nor prevents application code from publishing a duplicate integration event when the aggregate performs a same-state no-op.

## Decision

- An Order may transition from any current status to a different `Cancelled`, `Shipped`, or `Delivered` status.
- Every transition request requires a non-blank reason. The API/application boundary and aggregate both enforce this rule.
- The reason is recorded in the matching domain event and propagated in the integration event.
- Repeating a transition to the current status is a no-op: no new domain event, persistence operation, or integration event is produced.
- Event-sourced state remains derived exclusively through `When`; replayed events do not become pending events.

## Consequences

### Positive

- Every actual lifecycle change has an audit reason.
- The lab can compare permissive workflow transitions without falsely encoding an unapproved commercial rule.
- Retries do not announce lifecycle changes that did not occur.

### Negative

- Existing callers must provide request bodies/reasons and integration contracts gain a field.
- Reasons can contain operator/customer text, so downstream logging must avoid treating the full event as safe diagnostic content.

### Follow-up

- Update Orders production and test specs.
- If a commercial transition matrix is approved later, supersede this ADR and add explicit rejected-transition scenarios.

## Notes

`PreviousStatus` is intentionally omitted until a consumer requirement needs it; event replay can derive it.
