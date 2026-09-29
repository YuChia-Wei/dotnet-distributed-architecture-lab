# Transactional Messaging Standards (.NET)

Rule ID: `MESSAGING-TX-001`

This profile-default standard applies when a message consumer must make local
business state, durable outgoing intent, and successful incoming-processing
completion atomic in one selected durable store. It does not make a broker,
ORM, inbox/outbox provider, or Wolverine mandatory. A target may choose another
design with explicit architecture evidence that states the resulting consistency,
failure, and validation guarantees.

## Transaction Contract

For a selected transactional message path:

1. The Application Use Case declares the required local consistency and
   orchestrates Aggregate behavior and outbound ports.
2. Exactly one selected component physically completes the local transaction:
   an explicit Unit of Work **or** a verified runtime transaction pipeline.
   Repositories, message adapters, and decorators participate; they do not add
   an independent commit path.
3. When the selected store and runtime contract support enrollment, commit
   Aggregate state, durable outgoing intent, and successful incoming-processing
   completion in that one local transaction.
4. Persisting an incoming envelope or claiming broker delivery is distinct from
   successful business processing. Initial durable receipt must not be reported
   as completed processing.

The contract is local. It does not make an external broker, HTTP API, file
system, or another database part of the transaction, and it does not provide
end-to-end exactly-once delivery. External effects are represented by durable
intent and remain retryable after the local commit.

Inbox and outbox records are technical persistence with operational semantics;
they are not Domain Aggregates merely to fit a Repository shape. A target may
use conditional updates, uniqueness constraints, claimed states, and
capability-specific adapters. It must define the relevant concurrency behavior.

## Native Runtime And Adapter Selection

Prefer configured native inbox/outbox, enrollment, dispatch, retry, and recovery
facilities when they satisfy this contract. Do not add a second relay, inbox
success marker, or Unit of Work commit around the same path. A portable
Application port may still hide a selected adapter; it must not manufacture a
parallel completion owner.

Wolverine is one conditional .NET adapter example, not a portable dependency.
The reference sample used Wolverine `6.36.0` with a durable endpoint and Eager
EF Core transaction middleware. A target that selects Wolverine must verify its
installed version, endpoint durability, DbContext enrollment, generated pipeline,
and failure behavior. It must not copy that sample version or mode as a universal
default.

## Idempotency, Concurrency, And Disposition

- Define the envelope deduplication key, its consumer/tenant scope, retention,
  cleanup, and replay behavior. A transport envelope ID is not a permanent
  business-operation idempotency guarantee.
- If distinct envelopes can request the same business operation, define a
  separate business `OperationId` or equivalent idempotency contract.
- Deduplication prevents repeated processing of one delivery identity; optimistic
  concurrency prevents lost updates between valid competing operations. Neither
  replaces the other.
- Classify business rejection, transient infrastructure failure, optimistic
  concurrency conflict, and poison-message disposition separately. A persistence
  failure must not be swallowed and marked as successful handling.
- A retry after a concurrency conflict uses a fresh processing attempt and
  reloads valid state. Retry, dead-letter, and manual intervention policy remain
  target-specific.

## EF Core Context Participation

For an EF Core path selected for this contract, use one DbContext instance for
the processing unit and share that instance with participating repositories.
Registration, instance identity, tracking, transaction enrollment, and disposal
are separate concerns. Equal DbContext type, Factory instance, or connection
string does not prove a shared instance or transaction.

`IDbContextFactory<TContext>` is allowed for independent units of work or when
an explicit outer owner creates, shares, and disposes the instance. Repository
methods must not independently create and dispose contexts that are expected to
participate in the same transaction. DbContext is not thread-safe: independent
parallel work uses separate contexts/scopes. Multiple contexts require explicit
connection/transaction enrollment and equivalent validation; they are not made
atomic by DI registration alone.

## Evidence

Validate the selected contract with observable behavior, not compilation,
mock-only tests, generated-pipeline inspection, middleware presence, or skipped
external tests alone. The relevant evidence demonstrates success, rollback after
a persistence failure, duplicate/replay behavior within the declared retention
window, and optimistic-concurrency handling. Add recovery, outage, Factory, or
multi-context evidence when the target claims those behaviors. A bounded test
observation must retain its subject, environment, instrumentation, and limits;
it is not evidence of unbounded non-delivery or exactly-once behavior.
