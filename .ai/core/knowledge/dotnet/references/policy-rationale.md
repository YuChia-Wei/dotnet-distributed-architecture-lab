# Methodology sources and selected .NET policies

This is explanatory guidance for the retained .NET policies, not a new Rule ID,
Analyzer catalog or target adoption record. The linked owner documents retain
their contracts and existing registration status. Reading, installing or updating
this guidance does not override a target's accepted policy. An alternative may
fit a methodology while remaining outside this selected profile.

## Source register and permitted use

Record four different statements: what the source explicitly supports; the
Framework's interpretation; the selected or unresolved policy; and an observed
product predicate at a named version. Examples below are original illustrations,
not additional accepted business rules or reproduced source code.

Use authors, publishers, official organizations or verifiably authorized sources.
Unverified mirrors and unidentified author drafts are not normative evidence.
Preserve a caller's exact edition, chapter/page and reference context. Public
readability alone does not license redistribution. Source silence cannot prove
that every alternative is permitted or that a restriction is universal.

| ID | Author, work, version and location | Direct support and use / rights boundary |
|---|---|---|
| S1 | Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries*, 2015-03, printed pp.12,16–18; [official landing page](https://www.domainlanguage.com/ddd/reference/), [official PDF](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) | Value meaning without conceptual identity, Aggregate consistency, Repository access to roots and encapsulated complete creation. The Repository discussion includes criteria; it does not prescribe the two .NET methods selected here. Adapted conceptual summaries under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see attribution below. |
| S2 | Robert C. Martin, *The Clean Architecture*, 2012-08-13, “The Dependency Rule”, “Use Cases”, “Interface Adapters”, “Crossing boundaries”; [author article](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) | Inward source dependencies and separation of orchestration from external mechanisms. Original short summary and link only; no open reproduction license established. No image, full text, code or translated article included. |
| S3 | Alistair Cockburn, *Hexagonal Architecture*, HaT report 2005.02, displayed 2005-09-04 v0.9, “Intent”, “Motivation”, “Structure”; [author's original article](https://alistair.cockburn.us/hexagonal-architecture) | Application interaction through ports and technology-specific adapters, independently driven by different external actors. Original short summary and link only; no open reproduction license established. |
| S4 | Robert C. Martin, *Solid Relevance*, 2020-10-18, SRP/OCP/LSP/ISP/DIP sections; [author article](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html) | Separate reasons for change, preserve consumer contracts and depend on appropriate abstractions. Original short summary and link only; no open reproduction license established. |
| S5 | Martin Fowler, *Data Mapper*, 2003-03-05, catalog entry and *Patterns of Enterprise Application Architecture*, chapter 10; [author catalog](https://martinfowler.com/eaaCatalog/dataMapper.html) | Persistence mapping isolates object and database representations. Original short summary and link only; no book text, diagrams, code or translation included; no open reproduction license established. |

The S1 conceptual summaries here and in the common DDD topics are adaptations of
Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries*
(2015), Domain Language, under CC BY 4.0. Changes: selective paraphrase, comparison
with Framework policy and original examples. No endorsement by Eric Evans or
Domain Language is implied. The separate *Pattern Summaries* and the full 2004
book have distinct rights; this notice does not license those works. Check actual
license/attribution before reproducing any further material. Source qualification
does not replace package license/provenance review.

## Reconstruction and projection sources

The following sources were rechecked on 2026-10-31 for Framework #519. These
are original summaries and links, not reproduced articles, diagrams, code or
translations. For the Microsoft/Fowler articles no open redistribution license
is asserted; inspect the applicable license before reproducing material.

| Source / version and section | Explicit support | Framework interpretation / selected contract |
|---|---|---|
| Microsoft .NET, [Best practices for exceptions](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions), live documentation, “Use try/catch/finally blocks…” and “Restore state when methods don't complete…” | Recovery must be possible for a handled error; failed operations need defined state. | Required Aggregate reconstruction fails without exposing a usable partial object. Exception versus failed Result is target-selected; optional display degradation is not a mandate for all mappers to throw. |
| Eric Evans, *DDD Reference*, 2015-03, printed pp.16,18,22, [official PDF](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf), Aggregates / Factories / Assertions | Consistency boundaries, complete valid creation/reconstitution and explicit state assertions. | Identity alone does not establish complete business state. Creation and rehydration responsibilities differ; historical compatibility is explicit. These conceptual adaptations use S1's CC BY 4.0 attribution above. |
| Martin Fowler, [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html#ExternalUpdates), 2005-12-12 draft, External Updates / External Queries / Code Changes | Replaying history must distinguish external updates and time-dependent external input. | Replay restores facts without new publication or today's external decisions. No unique Gateway, queue topology or pending-event API is prescribed by this summary. |
| Microsoft Azure Architecture Center, [Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing), live documentation, Solution / Issues and considerations (versioning, ordering, idempotency) | Event handlers update materialized views; duplicate delivery and schema/order compatibility need handling. | Reader and projector capabilities differ. Owned read-row writes precede checkpoint/ack; selected deduplication and recovery handle replay. The article's example queue is not mandatory for every ES system; tolerant optional additive fields do not justify dropping required invariant state. |

The owner documents are [Mapper](../integration/persistence/mapper-standards.md),
[Aggregate](../architecture/ddd-cqrs/aggregate-standards.md),
[Repository](../integration/persistence/repository-standards.md) and
[query/projector](../integration/persistence/projection-standards.md). Their original cases
are Framework interpretations and selected examples, not claims that the cited
authors mandate each .NET method or transaction mechanism.

The [contract cases](../testing/reconstruction-and-projector-cases.md) summarize the optional ArchPrecept
`0.0.3-preview` behavior from the
[fixed CT-005 contract](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/docs/product/event-sourcing-contract.md).
Framework #179 owns actual external integration/version adoption. Package-free
and custom-contract implementations remain supported. No knowledge change adds
Analyzer exception analysis, arbitrary side-effect or interprocedural dataflow
coverage, an event store, a broker or a universal recovery runtime.

## Decision provenance and evidence limits

The earlier rationale assessment was recorded under [Framework #518](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/518).
The following fixed source records preserve earlier decisions. They are historical
evidence, not executable workflow instructions, required package resources or
proof of present-day target adoption. The explanations below distinguish recorded
decisions from the Framework's current rationale; missing original discussion
does not mean that no decision was ever made.

| Selected policy | Historical evidence at Framework `0ee07d83` | What the record establishes |
|---|---|---|
| Aggregate identity load/save | [Repository alignment D2](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/0ee07d8314c55a95c99428fa8d4fd12c4673c04c/.dev/workflows/2026-07-repository-pattern-standards-alignment/workflow-plan.md#L138-L151) | Recorded as resolved by the user: `FindByIdAsync` / `SaveAsync`, soft deletion through Aggregate behavior/save and separately restricted physical purge. This is the shared Aggregate contract, not a claim that every data-access role has two methods. |
| Consistency and explicit Unit of Work | [Repository alignment D6](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/0ee07d8314c55a95c99428fa8d4fd12c4673c04c/.dev/workflows/2026-07-repository-pattern-standards-alignment/workflow-plan.md#L309-L334) | Recorded user decision: eventual consistency by default; an explicit `IUnitOfWork` dependency identifies synchronous strong consistency. Aggregate/outbox persistence is atomic and pending events are acknowledged only after success. |
| Dedicated Input and real delivery Handler | [UseCase decision gate, 2026-07-07](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/0ee07d8314c55a95c99428fa8d4fd12c4673c04c/.dev/workflows/2026-07-usecase-command-handler-boundary/decision-difference-analysis.md#L122-L143) | Dedicated transport-neutral Input is the default, with a standard scalar exception. A Handler corresponds to an actual dispatch/message entry. Earlier mixed examples are not an additional exception. |
| Static-only pure Mapper | [Validator phase 3 decision](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/0ee07d8314c55a95c99428fa8d4fd12c4673c04c/.dev/workflows/2026-07-dotnet-validator-phase-3/workflow-plan.md#L58-L67) | Records static-only as resolved and assigns dependency/data-acquisition/orchestration work to other roles. It does not preserve the complete original discussion; the rationale below also uses the current #518 requirement. |
| MQ-only cross-BC interaction | [UseCase scope baseline](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/0ee07d8314c55a95c99428fa8d4fd12c4673c04c/.dev/workflows/2026-07-usecase-command-handler-boundary/workflow-plan.md#L57-L68) | Preserves the restriction without redesigning broker/transport behavior. It does not establish its original rationale or resolve the named-broker scope gap. |

The bounded historical search did not recover the original rationale for the
static Aggregate factory restriction. The current #518 requirement keeps both
that question and MQ-only applicability open. Neither search silence nor a
historical baseline statement grants a new policy decision.

## Repository: a narrow selected write port

Owner: [Repository standards](../integration/persistence/repository-standards.md), with
[query candidate flow](../integration/persistence/projection-standards.md).
S1 supports encapsulated root persistence; Framework selects the stricter
`FindByIdAsync` / `SaveAsync` surface to keep criteria, paging and DTO needs from
expanding the write port or exposing generic Entity CRUD around invariants.
`SaveAsync` remains neutral between insert/update/upsert/tracking/event append.

The cost is an additional query port and potentially another read. A query may
return candidate IDs, then the command reloads each root and revalidates current
eligibility before behavior/save. Candidate selection is not a lock or permission
to reuse stale state. A criteria finder returning roots is outside the selected
Aggregate port even though richer finders are not forbidden by DDD in general.
Target batch I/O and physical purge are separately specified capabilities;
neither becomes every Repository's obligation. Batching does not establish a
shared transaction or justify Unit of Work. An existing compatibility alias
preserves the original callers while keeping the same two operations. Keep
physical purge on a separate, restricted port so ordinary write consumers
cannot bypass retention and audit controls.

## Controller, UseCase, Handler and operation shape

Owners: [Controller](../application-types/web-api/controller-standards.md),
[UseCase](../architecture/ddd-cqrs/usecase-standards.md).
S2/S3 support separation of internal behavior and external delivery. Framework
selects ordinary HTTP Controller → UseCase port and a thin Handler only for an
actual dispatch/message/scheduled entry. UseCase owns orchestration; do not chain
UseCases or move business work into a Handler. This makes the same operation
usable through different entry points and keeps delivery retry/error behavior
outside it. The cost is explicit mapping and more types. An application-handler
or Mediator architecture requires its own evaluation; it is not automatically
accepted by this profile because CA/HexArch allow other arrangements.

The selected `ExecuteAsync`, dedicated `*Input` and required cancellation token
give callers a consistent operation contract. They are Framework form policies,
not methodology-mandated names or proof that Task is universally better than
ValueTask. Retain the no-input and single built-in/BCL scalar exceptions defined
by the owner; tuples, collections and custom command records do not acquire that
exception. A transport-neutral `AppCommand` is not inherently a transport type,
but passing it directly still violates the dedicated Input policy. An
Application-owned publisher port separates business intent from vendor bus and
delivery details; an interface name alone cannot hide mixed forbidden capabilities.

Only an explicitly selected pure-query endpoint may call a read-only query port
directly. It is not a write, query-handler-dispatch or general orchestration exception.

## Pure object Mapper versus work with dependencies

Owner: [Mapper standards](../integration/persistence/mapper-standards.md).
Framework selects static-only, dependency-free object conversion: no instance
state, DI, I/O or orchestration. The purpose is visible inputs and fewer hidden
dependencies; the cost is moving context acquisition to a separately named
Enricher, Assembler or Adapter. A routine needing clock/user/query access must
declare that responsibility and pass acquired values to a pure conversion.
S5's persistence Data Mapper is a different responsibility; it does not justify
allowing an instance pure-object Mapper under this policy.

Static syntax does not prove purity: a static method may read a clock, mutate
shared state or perform I/O. Nor does it prove determinism or a complete inverse.
A DTO projection may intentionally omit persistence state; a write-model round
trip must preserve its selected invariant/metadata/event contract. Reconstruction
and failure semantics have their own owner; a rename or static modifier cannot
repair event loss or incomplete state.

## Query reader and read-model projector

Owners: [Projection standards](../integration/persistence/projection-standards.md) and the
Repository role table. Immutable read results avoid exposing tracked state.
A pass-through query service with no composition, policy or calculation adds
an unnecessary boundary. A query reader does not write. A projector may update its
owned read store; its input, ordering, replay and failure contract must be specified.
That permission does not permit command-store mutations or arbitrary external
effects. “Projection” alone cannot determine the role. Existing read-only query
guidance remains correct. Detailed reconstruction behavior requires its separately
selected contract; this explanation does not supply it.

## Value Objects and bounded product checks

Owner: [Aggregate/VO standards](../architecture/ddd-cqrs/aggregate-standards.md).
S1 motivates value meaning and immutable treatment without conceptual identity.
Framework retains that invariant and warns about mutable referenced state.
ArchPrecept separately chooses stricter declared-state checks (DBA1018) and
Entity-reference-free state (DBA1019). Their policy reduces mutable aliases and
identity coupling, at the cost of explicit IDs/snapshots and additional modeling.
A snapshot name, record, readonly field or read-only collection interface does
not prove deep immutability. Do not use an unverified mirror to strengthen the
rule, or an abbreviated source's silence to permit all Entity references.

## Factory: retained policy and unresolved justification

Owner: [Aggregate construction](../architecture/ddd-cqrs/aggregate-standards.md).
S1 supports encapsulating creation and returning a complete invariant-valid object.
Creation and rehydration have different lifecycle responsibilities; neither may
bypass required state. The existing profile uses public constructors and rejects
static Aggregate factories. The evidence does not establish a general DDD ban
or a sufficient universal reason for that form restriction.

Bounded comparison, still unselected: a constructor gives a direct creation
surface; a named static factory may express alternative creation intent; a
separate factory can encapsulate complex assembly. Compare required state,
invariant completion, dependencies and rehydration/event behavior. These are
evaluation questions, not adopted alternatives or proof that every factory is
required/forbidden. Preserve a target's accepted policy until its owner reconciles
it. Do not create an Analyzer rule from this gap.

## Cross-BC interaction: retained restriction and scope gap

Owner: [retained cross-context restrictions](../architecture/ddd-cqrs/overview.md#retained-cross-context-restrictions).
Common DDD guidance distinguishes meaning/ownership from transport; a BC is not
a microservice. The .NET profile currently restricts cross-BC communication to
MQ, and its playbook further names RabbitMQ/Kafka. Public contracts, translation,
consistency requirements and failure responsibility remain required concerns.

Asynchronous messaging can reduce temporal coupling but introduces delayed
completion, ordering, duplicate/retry and operational costs. These are comparison
considerations, not recovered evidence that every interaction needs MQ or either
broker. The difference between MQ-only and named-broker-only scope is unresolved.
Compare HTTP/RPC or an in-process port against latency, availability, ownership
and failure requirements as unselected alternatives. This revision does not
adopt them, remove an accepted restriction, or call them universally non-DDD.

## SOLID reasoning and representative cases

S4 is a reasoning aid: investigate independent reasons for change, safe extension,
substitutability including failure behavior, consumer-specific contracts and
dependency direction. Count of classes, interfaces, methods or constructor
parameters does not prove these properties. Static code and zero Diagnostics
are likewise insufficient. Narrow ports can cost additional mapping/registration;
introduce them for an actual consumer responsibility, not a numerical target.

| Original case | Expected judgment under the selected policy |
|---|---|
| `FindIdsByStatusAsync` → reload root by ID → revalidate → domain behavior → save | Accepted division; a stale candidate may be refused after reload. No concurrency/transaction guarantee follows from the diagram. |
| Add `FindActiveProducts(criteria)` to the Aggregate write port | Reject under this profile; do not claim all DDD repositories forbid criteria. |
| One SQL adapter implements separate Aggregate and query interfaces; each consumer injects only its narrow port | Multiple implemented interfaces alone do not violate ISP. Inspect each contract and behavior. |
| Consumer injects a single interface exposing save, search, publish and transport acknowledgement | A wide mixed dependency obscures responsibility; nominal port naming does not resolve it. |
| Static Mapper converts supplied values; Enricher separately reads clock/user/query | Appropriate separation when the Mapper has no hidden state or I/O. Static alone is insufficient evidence. |
| `ExecuteAsync(CreateOrderInput, CancellationToken)` versus a plain Application `CreateOrderCommand` input | First follows canonical shape. Second may be transport-neutral and still fail the selected dedicated Input contract. |
| HTTP → UseCase; message → thin Handler → UseCase | Accepted entry reuse. UseCase → UseCase and business orchestration in Handler remain prohibited. |
| Explicit pure-query endpoint → read-only query port | Conditional exception only; designation and no writes must be established. |
| Named static Aggregate factory; HTTP between BCs | Bounded unresolved comparisons above; not newly accepted policy and not automatic methodology violations. |

## Versioned ArchPrecept comparison, not a second rule catalog

The observed reference is ArchPrecept source
[`60330242f7f690a01cfa2332b578aac35584f067`](https://github.com/YuChia-Wei/ArchPrecept/tree/60330242f7f690a01cfa2332b578aac35584f067),
whose build version says `0.0.3-preview` but whose Git identity is eight commits
after tag `v0.0.3-preview`. Do not label these source observations as that published
package's behavior. Actual package/feed/source adoption and consumer tests remain
an explicit integration operation, including package-free/custom-contract paths.

| Concept / Framework policy | Product reference at that source | What remains unproved |
|---|---|---|
| Optional ES Aggregate; state follows selected event transitions | [DBA1009](https://github.com/YuChia-Wei/ArchPrecept/blob/60330242f7f690a01cfa2332b578aac35584f067/docs/diagnostics/DBA1009.md), doc 0.5: recognized ES roles and canonical `void When(TEvent)` virtual/abstract contract/true override identity, not any same-name method | Replay correctness, constructor/initializer effects, arbitrary indirect mutation and successful storage transaction. |
| VO value semantics / immutable intent | [DBA1018](https://github.com/YuChia-Wei/ArchPrecept/blob/60330242f7f690a01cfa2332b578aac35584f067/docs/diagnostics/DBA1018.md), doc 0.4: bounded instance-state policy | Full runtime/deep immutability; preserve unknown/not-evaluated. |
| Conservative VO Entity-reference-free product policy | [DBA1019](https://github.com/YuChia-Wei/ArchPrecept/blob/60330242f7f690a01cfa2332b578aac35584f067/docs/diagnostics/DBA1019.md), doc 0.4: recognized declared state and supported containers | Arbitrary runtime object graphs, unknown wrappers; no universal DDD prohibition inferred. |
| Port/adapter, Input and Mapper policies | Consult the selected product's [single catalog](https://github.com/YuChia-Wei/ArchPrecept/blob/60330242f7f690a01cfa2332b578aac35584f067/rules/catalog.xml), actual profile/configuration and Diagnostic evidence | No claim that Framework file patterns are running analyzers, or that no Diagnostic proves complete SOLID/DDD/CA/HexArch. |

These links are product-owner documentation observations, not fresh Analyzer
execution. Rule applicability, compilation/configuration failure, generated or
disabled coverage and not-evaluated results must remain distinguishable.
ArchPrecept owns its predicate, Rule/Diagnostic/API documentation and preview
compatibility policy. That lifecycle cannot renumber Framework's released Rule IDs
or supersede target decisions. This guidance allocates no new normative identity.
