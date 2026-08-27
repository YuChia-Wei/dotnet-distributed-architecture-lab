# Reserve Inventory Test Spec

## Inputs Used

- `INV-005`, `INV-006`, `INV-007`, and `INT-003` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/domains/inventory-item/usecase/reserve-inventory.json`
- `.dev/problem-frames/inventory/cbf/reserve-inventory/`
- `tests/InventoryControl.Tests/InventoryReservationIdempotencyTests.cs`
- `tests/InventoryControl.Tests/ReserveInventoryUseCaseTests.cs`
- `tests/InventoryControl.Tests/PostgresInventoryReservationRepositoryTests.cs`

## Implementation Status

- Status: `implemented-awaiting-external-execution`
- Inventory owns its test project and has executable validation, replay, conflict, terminal/transient/outbox-stage failure, stable relay identity, cancellation, failure-policy, JSON-contract, and PostgreSQL concurrency/atomicity scenarios.
- The PostgreSQL scenario is skipped by default and remains non-passing evidence until the explicit external profile runs successfully.

## Scenario Set

### Scenario 1: reserve once and stage an event

- Test level: `application`
- Given: a positive request references an item with sufficient stock.
- When: `IReserveInventoryUseCase.ExecuteAsync` runs.
- Then: stock decreases exactly once; a successful outcome and one `InventoryIntegrationOutbox` row commit together; the staged stock-decreased event uses `MessageId = operationId` and `PartitionKey = productId.ToString("N")`.

### Scenario 2: replay the same successful operation

- Test level: `integration`
- Given: an operation id has already completed successfully for the same product and quantity.
- When: the same request is replayed.
- Then: the stored outcome is returned with `WasAlreadyProcessed = true`; stock is not decremented again; no second outbox row is inserted and delivery identity remains stable.

### Scenario 3: reject operation identity conflict

- Test level: `integration`
- Given: an operation id is already bound to a product and quantity.
- When: the same id is reused with a different payload.
- Then: `OperationIdentityConflict` is terminal; stock is unchanged; no new success-event outbox row is staged.

### Scenario 4: preserve a terminal failure

- Test level: `integration`
- Given: an operation previously completed with item-not-found or insufficient-stock.
- When: stock later changes and the same request is replayed.
- Then: the original failure is returned with `WasAlreadyProcessed = true`; stock is not re-evaluated or decremented.

### Scenario 5: reject invalid input

- Test level: `application`
- Given: operation id or product id is empty, or quantity is not positive.
- When: the use case runs.
- Then: the matching failure reason is returned; no transaction is opened.

### Scenario 6: cancel without mutation

- Test level: `integration`
- Given: cancellation is requested before repository work begins.
- When: reservation is attempted.
- Then: `OperationCanceledException` propagates; stock and operation history remain unchanged.

### Scenario 7: serialize concurrent reservations

- Test level: `integration`
- Given: PostgreSQL contains stock that cannot satisfy two concurrent requests together.
- When: two distinct operation ids reserve concurrently.
- Then: row locking prevents negative stock; at most one succeeds; both durable outcomes match the final balance; exactly one source-outbox row exists for the successful operation.

### Scenario 8: roll back when event staging fails

- Test level: `application`
- Given: reservation calculation succeeds but staging the producer-created event fails before commit.
- When: the use case runs.
- Then: commit is not called; a real PostgreSQL failure-injection variant must prove stock, outcome, and outbox all roll back.

### Scenario 9: retry relay with stable identity

- Test level: `infrastructure`
- Given: one committed outbox row fails its first transport publish.
- When: the relay claims the same row again.
- Then: both attempts use the same MessageId, partition key, payload, and OccurredOn; success sets `PublishedAt`, while five failures park the row.

## Assertion Notes

- Assert each failure reason, stock value, durable operation row, outbox row count, commit call, message id, partition key, and retained event timestamp separately.
- Scenario 7 and the real rollback half of Scenario 8 require a PostgreSQL fixture; an in-memory double cannot establish locking or database rollback semantics. Use the opt-in contract in `tests/README.md`.

## Recommended Test Spec Path

`.dev/specs/tests/inventory-item/use-cases/reserve-inventory.test-spec.md`

## Implementation and Execution Handoff

The broker-free scenarios are implemented under `tests/InventoryControl.Tests/`. Real PostgreSQL execution remains a separate opt-in gate and skipped evidence is non-passing.
