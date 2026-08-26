# Order Source Outbox Test Spec

## Inputs Used

- `ORD-007`, `INT-004`, and `INT-005` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/reconstruction/persistence-contracts.json`
- `.dev/specs/reconstruction/message-contracts.json`
- `tests/SaleOrders.Tests/OrderIntegrationOutboxRelayTests.cs`

## Implementation Status

- Status: `implemented-partial`
- Relay retry and delivered-row behavior have executable unit-level evidence; a real PostgreSQL atomicity fixture remains planned.

## Scenario Set

### Scenario 1: commit event stream and outbox atomically

- Test level: `integration`
- Given: reservation succeeded and the expected stream version is current.
- When: the order committer saves pending domain events and the mapped integration event.
- Then: both records commit in one local transaction with a stable message id; neither is visible after transaction failure.

### Scenario 2: reject optimistic concurrency conflict

- Test level: `integration`
- Given: another writer advanced the stream version.
- When: commit is attempted with the stale expected version.
- Then: the commit fails; pending changes remain diagnosable; no outbox row is added.

### Scenario 3: retry relay without changing identity

- Test level: `integration`
- Given: an undelivered outbox row exists and the first publish attempt fails transiently.
- When: the relay retries.
- Then: payload, message id, partition key, and occurrence time are unchanged; attempt metadata advances.

### Scenario 4: mark delivered only after success

- Test level: `integration`
- Given: an undelivered row is publishable.
- When: Wolverine accepts the message.
- Then: `DeliveredAt` is set once; subsequent batches do not republish that row.

## Assertion Notes

- Use explicit database transaction assertions for scenario 1 and 2.
- Never use sleeps to observe relay behavior; invoke a bounded relay batch and await the result.

## Recommended Test Spec Path

`.dev/specs/tests/order/integration/order-source-outbox.test-spec.md`

## Implementation and Execution Handoff

Only design and current evidence mapping are authorized.
