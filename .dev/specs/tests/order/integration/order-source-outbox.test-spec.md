# Order Source Outbox Test Spec

## Inputs Used

- `ORD-005`, `ORD-006`, `INT-004`, `INT-005`, and `INT-006` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/reconstruction/persistence-contracts.json`
- `.dev/specs/reconstruction/message-contracts.json`
- `tests/SaleOrders.Tests/OrderIntegrationOutboxRelayTests.cs`
- `tests/SaleOrders.Tests/OrderIntegrationEventSerializationTests.cs`

## Implementation Status

- Status: `implemented-partial`
- Relay retry identity, original occurrence time, payload preservation and successful-row deletion have unit-level test anchors. All four integration-event types have stored-JSON round-trip and existing producer-constructor tests. Real PostgreSQL atomicity and owner-token deletion checks remain integration-test gaps; a test double does not establish database rollback.

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

### Scenario 4: delete the claimed row only after success

- Test level: `integration`
- Given: an undelivered row is claimed with the relay's owner token.
- When: Wolverine accepts the message.
- Then: the relay deletes only the successfully published row whose id and owner token still match. Subsequent batches cannot claim the deleted row. A crash after publication but before deletion may redeliver with the same identity; at-least-once remains the contract.

## Assertion Notes

- Use explicit database transaction assertions for scenario 1 and 2.
- Never use sleeps to observe relay behavior; invoke a bounded relay batch and await the result.

## Recommended Test Spec Path

`.dev/specs/tests/order/integration/order-source-outbox.test-spec.md`

## Implementation and Execution Handoff

Only design and current evidence mapping are authorized.
