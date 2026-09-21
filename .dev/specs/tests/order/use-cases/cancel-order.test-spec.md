# CancelOrder Test Spec

## Scope

Application and integration-aware verification for `CancelOrder`.

## Implementation Status

- Status: `partial`
- `tests/SaleOrders.Tests/CancelOrderTests.cs` covers successful state transition, `IOrderEventCommitter` staging of one `OrderCancelled` with its reason, and repeat-cancel no-op. Direct not-found assertions remain planned; a committer double is not broker-publication or PostgreSQL-atomicity proof.

## Related Production Spec

- `.dev/specs/domains/order/usecase/cancel-order.json`

## Scenario List

- Happy path: existing order is marked as cancelled
- Failure path: target order does not exist
- Integration path: successful cancellation stages `OrderCancelled` with state; the source-outbox relay publishes after commit

## Given-When-Then

### Scenario 1: cancel succeeds for an existing order

- Given:
  - an existing order is loaded by id
- When:
  - `ICancelOrderUseCase.ExecuteAsync` is invoked with `CancelOrderInput`
- Then:
  - the order status becomes `Cancelled`
  - `IOrderEventCommitter` receives the order and one `OrderCancelled` event with the cancellation reason for atomic persistence
  - the source-outbox relay owns subsequent publication

### Scenario 2: order does not exist

- Given:
  - no order exists for the requested id
- When:
  - `ICancelOrderUseCase.ExecuteAsync` is invoked with `CancelOrderInput`
- Then:
  - the operation fails with `KeyNotFoundException` or equivalent not-found semantics
  - no status change is persisted
  - no success-event commit or `OrderCancelled` outbox staging occurs

## Assertions

- repository load and event-committer invocation
- order status transition
- integration-event staging and reason, with relay publication verified separately
- not-found failure semantics

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Compensation behavior against downstream consumers should be expanded later in cross-domain runtime scenarios.
