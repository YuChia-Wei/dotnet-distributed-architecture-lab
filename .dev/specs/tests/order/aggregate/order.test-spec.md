# Order Aggregate Test Spec

## Scope

Aggregate-focused verification for `Order` lifecycle transitions and domain events.

## Implementation Status

- Status: `implemented`
- Current aggregate tests cover reasoned transitions, same-state no-op, missing reasons, replay, and committed-event lifecycle.

## Related Production Spec

- `.dev/specs/domains/order/entity/order-spec.md`

## Scenario List

- Happy path: placed order starts in `Placed` status with `OrderPlacedDomainEvent`
- Happy path: each different target status records the supplied reason
- Validation: a missing reason leaves state and pending events unchanged
- Idempotency: a same-state transition is a no-op
- Replay: history alone restores state/version without pending events
- Commit lifecycle: a confirmed append advances version and clears pending events

## Given-When-Then

### Scenario 1: order starts in placed status

- Given:
  - valid product id, product name, quantity, order date, and total amount
- When:
  - an `Order` aggregate is created
- Then:
  - the initial status is `Placed`
  - an `OrderPlacedDomainEvent` is recorded

### Scenario 2: ship an existing order

- Given:
  - an existing order in any different state
  - a non-blank transition reason
- When:
  - `Order.Ship(reason)` is invoked
- Then:
  - status becomes `Shipped`
  - an `OrderShippedDomainEvent` is recorded
  - the event preserves the reason

### Scenario 3: deliver an existing order

- Given:
  - an existing order in any different state
  - a non-blank transition reason
- When:
  - `Order.Deliver(reason)` is invoked
- Then:
  - status becomes `Delivered`
  - an `OrderDeliveredDomainEvent` is recorded
  - the event preserves the reason

### Scenario 4: cancel an existing order

- Given:
  - an existing order in any different state
  - a non-blank transition reason
- When:
  - `Order.Cancel(reason)` is invoked
- Then:
  - status becomes `Cancelled`
  - an `OrderCancelledDomainEvent` is recorded
  - the event preserves the reason

### Scenario 5: reject a missing transition reason

- Given:
  - an existing order
  - a null, empty, or whitespace-only reason
- When:
  - any lifecycle transition is requested
- Then:
  - argument validation fails
  - status is unchanged
  - no domain event is added

### Scenario 6: repeat the current state

- Given:
  - an order already in the requested target status
  - a non-blank reason
- When:
  - the same transition is requested again
- Then:
  - the operation reports no change
  - no domain event is added

### Scenario 7: rehydrate event history

- Given:
  - placed and lifecycle transition events
- When:
  - an Order is rehydrated from the events
- Then:
  - identity, fields, and final status match the history
  - version equals the event count
  - pending domain events are empty

### Scenario 8: confirm a successful append

- Given:
  - an aggregate with pending events and the matching committed stream version
- When:
  - changes are marked committed
- Then:
  - aggregate version advances to the committed version
  - pending events are cleared exactly once

## Assertions

- status transitions
- event-sourced aggregate event recording
- aggregate field retention across lifecycle methods

## Test Level

- Primary: `unit`
- Secondary: `application`

## Notes / Deferred Cases

- Repository transaction failure and concurrency tests remain in the infrastructure test slice.
- A stricter commercial transition matrix is deferred until a requirement supersedes ADR-001.
