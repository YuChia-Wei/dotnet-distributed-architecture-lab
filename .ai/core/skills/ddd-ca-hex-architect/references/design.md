# Design a bounded architecture

## Inputs and authority

Confirm business capability/module, requested new design or revision, source
requirements/AC IDs, known workload, quality constraints, adopted architecture,
existing decisions and compatibility obligations. Separate source facts,
observed behavior, assumptions and proposed decisions. Existing code does not
override an accepted requirement by existing.

Use explicit target sources for this scope; no directory or registry is
mandatory. Conflicting or missing authority stops the dependent decision:
present bounded options and identify the decision owner. Reuse accepted choices
rather than reopening them merely because a class is added.

Use DDD for language, responsibility and invariant ownership; Clean Architecture
for dependency direction; Hexagonal Architecture for ports and external
adapters. These lenses do not make every pattern mandatory. CQRS, event
sourcing, a broker, physical project splits, ORM and DI API need target
selection. This package has no technology supplement. Apply selected supplied
guidance only within scope; report missing specialist coverage and leave the
affected required acceptance unresolved.

## Design sequence

1. Describe capability, actors, trigger, result and measurable acceptance.
   Preserve business vocabulary and label unconfirmed terms. Name ownership of
   data and decisions rather than treating a folder as the boundary.
2. Identify invariants and constrained state. Propose aggregate/module
   boundaries where responsibility or consistency warrants them. Explain what
   must be atomic and which intermediate states are acceptable.
3. Place inbound application ports and outbound dependency ports. Keep business
   decisions independent of transport, persistence and vendor APIs. Give each
   abstraction a purpose such as a stable dependency boundary or controllable
   failure/time/data seam; avoid speculative interfaces.
4. Describe commands, queries or reactions only when needed by the chosen
   model. Specify input/output, errors, transitions, transaction owner, external
   effects and dependency lifetimes relevant to correctness.
5. Compare credible alternatives, including the simpler valid option. State
   benefits, costs, operational burden, rejected choices and the evidence or
   assumption driving the recommendation.
6. Walk relevant failure windows: commit versus publish, retry, duplicates,
   ordering, partial failure, cancellation, recovery and observability. Record
   actual guarantees; do not assume exactly-once delivery. Compare coordination
   or compensation against invariants for cross-owner effects.
7. For existing consumers, explain compatibility, versioning, rollout order,
   migration/recovery and rollback limits when relevant. A proposal authorizes
   none of these actions.
8. Define observable acceptance and evidence needs. Distinguish controlled
   tests from required real storage/messaging/integration evidence and record
   feasibility limits.

## Scale the deliverable

| Requested subject | Include when relevant |
| --- | --- |
| Bounded context/module | Purpose, owner, vocabulary, aggregates/invariants, ports, adapters, integrations and target-selected placement. |
| Aggregate or major refactor | Responsibility, entities/value objects, behavior/events, consistency, persistence decision and regression risks. |
| Command/query/reaction | Trigger/input, application responsibility, domain/projection logic, outbound effects, result/error and acceptance. |
| Messaging integration | Producer/consumer ownership, payload, guarantees, duplicate/order policy, transaction/publish boundary, retry and recovery. |

Return a coherent proposal with source bindings, alternatives, assumptions,
recommendation, unresolved owner decisions and validation needs. Label choices
proposed until accepted by the target owner. Use a diagram when it clarifies
dependencies or effects. Default to conversation; persist only at a selected
authorized destination with an available editor.

Use [review criteria](review.md) as an author self-check when useful and label
it self-check. It is not independent review, implementation or specification
compliance. Optional ADR/knowledge persistence is a separate selected handoff:
return decision context, options, consequences, status and sources when no
persistence capability is available. Accepted designs can pass to an
implementation owner with existing permission and open questions; proposals
never silently become accepted target truth.
