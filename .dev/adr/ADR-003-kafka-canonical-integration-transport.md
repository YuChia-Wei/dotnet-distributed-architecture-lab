# ADR-003: Kafka As The Canonical Integration Transport

## Status

Accepted

## Date

2026-08-27

## Context

The lab needs one canonical broker path for event-driven verification. Ordering matters for changes concerning the same product or aggregate, while future independent subscribers may need broadcast-style delivery. Kafka and RabbitMQ can both carry the logical contracts, but their physical semantics are not interchangeable: Kafka orders records within a partition and fans a topic out through distinct consumer groups; RabbitMQ fans out through an exchange bound to separate queues, while multiple consumers on one queue compete for messages.

Treating both profiles as equally authoritative created ambiguity about partition keys, queue topology, required external gates, and which behavior a reconstruction must prove.

## Decision

- Kafka is the canonical runtime and external verification path.
- The producing bounded context owns integration-event meaning, schema, compatibility, and partition-key selection.
- Inventory reservation uses normalized `ProductId` as its Kafka partition key; ordering is promised only within that partition, never globally across partitions.
- Independent Kafka subscribers use distinct consumer groups.
- RabbitMQ remains a compatibility profile. Current shared queue names are competing-consumer topology and are not a broadcast contract. ADR-005 later selected Kafka + RabbitMQ dual broadcast as a target direction, with implementation gated on destination-aware outbox state and fanout routing.
- Migration to RabbitMQ, promotion to an equally required profile, or dual deployment requires a separate owner decision supported by topology and workload evidence.

## Consequences

### Positive

- Reconstruction and acceptance have one unambiguous broker path.
- Ordering scope and producer responsibility are explicit.
- A future broadcast requirement can compare concrete consumer-group and exchange/queue designs instead of selecting a broker by label.

### Negative

- RabbitMQ code can drift until a compatibility gate is deliberately run.
- Physical dead-letter and replay procedures remain broker-specific work.
- Dual-profile packages remain maintenance cost even though only Kafka is canonical.

### Follow-up

- Prove Kafka connectivity and keyed ordering in the clean-room acceptance run.
- Define consumer group identities when business handler ownership is decided.
- Before claiming RabbitMQ broadcast, define exchange type, routing keys, one queue per subscriber, retry/DLQ topology, and parity tests.

## Notes

This ADR does not remove RabbitMQ support and does not authorize dual deployment.
