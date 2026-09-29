# Effective target engineering rules

This is the current target-owned semantic authority for the fourteen rules selected by this repository. It preserves the complete normative statements and the target applicability recorded before RC2 replacement. Legacy v0.18 catalog identities are historical provenance, not the RC2 installation or a validation receipt. Apply each rule only when its condition holds; a loaded rule is not automatically applicable to every work item.

The owner approved destructive RC2 adoption with these semantics retained. The fixed candidate, knowledge projection and selected checks must be recorded separately. S6, runtime, upgrade/recovery and independent admission are deferred for this adoption; no result below claims those checks passed.

## Target rule index

| Rule | Strength | Target applicability |
| --- | --- | --- |
| `AGGREGATE-ES-001` | conditional | Orders adopts event sourcing and reconstructs Order by replaying persisted domain events through EsAggregateRoot behavior. |
| `AICTX-EVIDENCE-001` | invariant | AI-context initialization, upgrade, audit, and development must rely on repository-backed evidence and disclose optional external discovery. |
| `ARCH-UOW-001` | profile-default | Command use cases persist aggregates, use explicit local transactions for aggregate/outbox consistency, and message across bounded contexts. |
| `ASSESSMENT-ARTIFACT-001` | invariant | AI-context audits, code reviews, and architecture assessments are persisted as governed assessment artifacts. |
| `CONTRACT-SEMANTICS-001` | invariant | Domain behavior declares and enforces preconditions and invariants for products, orders, and inventory. |
| `DELETE-PURGE-001` | conditional | Inventory persistence contains an executable physical-delete implementation, so purge/archive governance cannot be globally excluded. |
| `DELETE-SOFT-001` | profile-default | Products persists an isdeleted marker and filters deleted records from aggregate and query repositories. |
| `MAP-EVENTS-001` | invariant | Order reconstruction replays persisted events without creating pending events, and tests verify clean rehydration behavior. |
| `MESSAGING-TX-001` | profile-default | a message consumer requires atomic local business state, durable outgoing intent, and successful incoming-processing completion |
| `PROJECT-GRAMMAR-001` | profile-default | The target adopts the conditional slnx navigation profile with bounded context DomainCore and Presentation solution folders. |
| `TECH-SELECT-001` | invariant | Testing, persistence, messaging, and observability choices are explicit, evidence-backed, and recorded in target configuration. |
| `TEST-BDDFY-001` | profile-default | The dotnet-backend profile applies and the target explicitly selects the baseline-permitted plain-xUnit branch with mandatory GWT semantics. |
| `TEST-GWT-001` | invariant | New and modified tests use recognizable Given-When-Then semantics regardless of the selected runner. |
| `TEST-MOCK-001` | profile-default | Test projects use the explicitly recorded per-project Moq and NSubstitute selection. |

## Complete normative statements

### AGGREGATE-ES-001

Strength: `conditional`. Target applicability: Orders adopts event sourcing and reconstructs Order by replaying persisted domain events through EsAggregateRoot behavior.

## Optional `EsAggregateRoot<TId>` Behavior Contract

Rule ID: `AGGREGATE-ES-001` (`conditional` when Event Sourcing is selected).

`EsAggregateRoot<TId>` is the only supplied optional base class. A target may
copy the source include, reimplement this contract, or use another implementation
that preserves the behavior.

### Required behavior

1. `Replay(history)` dispatches committed events to `When` in order.
2. Replay increments the committed `Version` once per event.
3. Replay never adds events to the pending-event collection.
4. `Apply(event)` dispatches the event to `When` before recording it as pending.
5. If `When` rejects an event, that event is not recorded as pending.
6. `Apply` does not advance the committed `Version`.
7. `MarkChangesAsCommitted(committedVersion)` accepts only
   `Version + pending-count`.
8. A successful commit advances `Version` and clears pending events exactly
   once.
9. A rejected commit confirmation preserves the committed version and pending
   events for retry or diagnosis.
10. Product state changes occur only in `When`; `When` is deterministic and
    performs no external I/O.

### Construction rule

Do not invoke virtual `When` from the base constructor. In C#, a derived type's
field initializers have not completed while its base constructor executes.
The derived reconstruction constructor calls `Replay(history)` from its own
constructor body:

```csharp
public sealed class Order : EsAggregateRoot<OrderId>
{
    private readonly List<OrderLine> _lines = [];

    public Order(IEnumerable<IDomainEvent> history)
    {
        Replay(history);
    }

    protected override void When(IDomainEvent @event)
    {
        // deterministic type dispatch
    }
}
```

The repository-owned source include is under
[`source-includes/domain/`](../source-includes/domain/). It is reference-only
framework material, not a published package or complete reference product. An
adopting target owns SDK compatibility, compilation, behavior tests, invocation
evidence, and upgrade reconciliation before claiming executable validation.

### AICTX-EVIDENCE-001

Strength: `invariant`. Target applicability: AI-context initialization, upgrade, audit, and development must rely on repository-backed evidence and disclose optional external discovery.

## Tool-Neutral Evidence Boundary

Rule ID: `AICTX-EVIDENCE-001`

Optional repository indexes, code graphs, IDE indexes, MCP servers, semantic
search, and similar tools are discovery accelerators. They may identify candidate
files, sections, or relationships, but their output is not authoritative project
truth and must not be the sole evidence for an AI-context finding, absence claim,
inventory, or relationship conclusion.

- Keep AI-context skills usable when no optional discovery tool is installed.
- Do not require one vendor, graph schema, hook, cache, or persisted index.
- Verify material findings against direct repository files, Git-tracked paths,
  structured manifests, or repository-owned deterministic validators.
- Treat an empty search result as unknown until the declared scope is checked by
  a tool-independent fallback.
- Record tool name, index freshness, scope, exclusions, and skipped checks when
  tool output materially accelerated an assessment.
- Prefer the narrowest direct verification needed for a candidate finding; an
  accelerator may choose where to look, but it may not decide what is true.

### Quick Fallback Verification

Use these repository-native checks before accepting a discovery-tool conclusion:

| Risk | Fast verification |
| --- | --- |
| Hidden or skipped AI-context roots | Run `git ls-files -- .ai .dev .agents .claude .codex .github AGENTS.md CLAUDE.md AGENTS.zh-TW.md README.md README.en.md`, then inspect `git status --short --untracked-files=all` for untracked context. |
| Incomplete Markdown inventory | Run `git ls-files -- '*.md'` and compare the relevant paths with the tool result. |
| Missing Markdown relationship | Search the literal target or link text with `git grep -n -F -- '<target-or-link-text>' -- '*.md'`, open the source file, and resolve the target relative to that file. |
| Stale index or snapshot | Compare the tool's recorded revision, when available, with `git rev-parse HEAD`; directly reopen every file used by a material finding. |
| Tool-specific omissions | Run `python .ai/scripts/validate-ai-context.py` for registered context contracts and record any relationship class the validator does not cover. |

The 2026-07-13 Codebase Memory MCP probe is an example, not a permanent
product contract: its full index omitted `.claude/` and exposed Markdown files
and headings without Markdown link edges. Re-test current tool behavior when it
matters, and use the fallback checks above regardless of tool brand.

### Generated Inventory Contract

A generated inventory, index, graph export, or snapshot that is retained as a
repository artifact must identify its generator, generation time, source Git
revision or input digest, scope, and exclusions. It must also state how a user
can reproduce or validate it. If those fields are absent or its source revision
differs from the subject revision, treat it as a discovery hint rather than
primary evidence.

- Do not overwrite human-owned or file-backed truth with a generated view.
- Do not infer completeness from a generated artifact merely because it is committed.
- Prefer a repository-owned deterministic regeneration or parity check when the generated artifact is an active catalog.
- When no active generated inventory exists, record the check as not applicable instead of creating one solely for convenience.

### ARCH-UOW-001

Strength: `profile-default`. Target applicability: Command use cases persist aggregates, use explicit local transactions for aggregate/outbox consistency, and message across bounded contexts.

### 7. Strong Consistency MUST Be Explicit

One command changes one Aggregate by default. Events and eventual consistency are
the default for coordination between Aggregates. A Use Case may inject
`IUnitOfWork` for multiple Aggregates only as an exceptional same-bounded-context
decision when all of these conditions hold:

1. The business names an all-or-nothing invariant involving the Aggregates.
2. Any eventually consistent intermediate state would be unacceptable and cannot
   be safely compensated.
3. The design rechecks that the Aggregate boundaries are correct instead of using
   a transaction to hide a misplaced invariant.
4. The decision documents the invariant, the involved Aggregates, and why eventual
   consistency or compensation is insufficient.

The following Reservation + Capacity example represents such an exceptional
business rule; it is not a general Use Case template:

```csharp
public sealed class CompleteReservationUseCase
{
    private readonly IUnitOfWork unitOfWork;

    public async Task ExecuteAsync(CancellationToken cancellationToken)
    {
        // Exceptional case: Reservation and Capacity are in the same bounded
        // context and the named invariant requires both changes to succeed or
        // neither to succeed. An intermediate overbooked state is unacceptable
        // and cannot be safely compensated. Do not copy this as a general template.
        // Load Reservation and Capacity, invoke Domain behavior, and save through ports.
        await this.unitOfWork.CommitAsync(cancellationToken);
    }
}
```

- MUST NOT select a multi-Aggregate transaction because of shared storage, ORM or
  framework capabilities, fewer I/O round trips, implementation convenience, or a
  general future need.
- MUST NOT make `IUnitOfWork` a default Use Case dependency.
- MUST NOT span bounded contexts with one transaction; cross-bounded-context
  coordination uses integration events and eventual consistency.
- A Repository participating in a Unit of Work MUST NOT commit independently.
- A Handler MUST NOT introduce a transaction or commit after the Use Case. A
  selected runtime pipeline or middleware may enroll and complete the processing
  transaction outside the Handler; it does not make the Handler a transaction owner.
- Pending Domain Events may be acknowledged or cleared only after a successful commit.

For a selected transactional message path, the Use Case declares and
orchestrates the required local consistency; the selected Unit of Work or
verified runtime pipeline physically completes it. This does not make
`IUnitOfWork` a default Use Case dependency and does not weaken the
multi-Aggregate, same-bounded-context exception above. See
[Transactional Messaging Standards](transactional-messaging-standards.md) for
the single completion-owner, inbox/outbox, and adapter contract.

### ASSESSMENT-ARTIFACT-001

Strength: `invariant`. Target applicability: AI-context audits, code reviews, and architecture assessments are persisted as governed assessment artifacts.

## Assessment Versus Workflow

| Mode | Use | Durable artifact |
| --- | --- | --- |
| Transient analysis | Read-only analysis that remains in the conversation. | none |
| Standalone assessment | A persisted audit, large code review, architecture assessment, or technical-debt inventory without authorized remediation. | `.dev/assessments/<assessment-id>/` |
| Workflow execution | Authorized multi-stage work, remediation, or source-of-truth change. | `.dev/workflows/<workflow-id>/` |

Persistence alone does not turn an observation into a workflow. If the user asks
to assess and remediate in one request, store the assessment under
`.dev/assessments/` and store execution state under the owning workflow. The
workflow references the assessment; it does not copy the report.

### CONTRACT-SEMANTICS-001

Strength: `invariant`. Target applicability: Domain behavior declares and enforces preconditions and invariants for products, orders, and inventory.

## Contract Categories

- A precondition rejects invalid input or an invalid state before behavior runs.
- A postcondition verifies the observable state/result promised by a successful
  operation.
- An invariant must hold for every externally observable valid Aggregate or
  Entity state.

### DELETE-PURGE-001

Strength: `conditional`. Target applicability: Inventory persistence contains an executable physical-delete implementation, so purge/archive governance cannot be globally excluded.

## 📌 Core Concept

An **Archive** is a database write pattern dedicated to Query Models in a CQRS architecture:

- Its interface resembles a Write Model Repository, but an Archive handles database write requirements for a Query Model.
- A Repository is limited to writing a single Aggregate in the Command Model.
- It may write to one table or across multiple tables.
- A Reactor in the Handler layer invokes the Archive after receiving a Domain Event and writes the data to the database.

---

### DELETE-SOFT-001

Strength: `profile-default`. Target applicability: Products persists an isdeleted marker and filters deleted records from aggregate and query repositories.

### 0. Soft-Delete Default Profile

Rule ID: `DELETE-SOFT-001` (`profile-default`).

The dotnet-backend Aggregate Repository profile defaults to soft deletion.
Affected Aggregates support the following field and event-application behavior,
and deletion is persisted through `SaveAsync`.

A target may explicitly opt out for an Aggregate or repository profile when its
requirements or architecture decision select another lifecycle. The opt-out
must be recorded in target evidence such as `.dev/project-config.yaml`
architecture capability selections, requirements, or an ADR. An opted-out
Aggregate is not required to add `IsDeleted`.

#### Adopted Aggregate Root Must Have an `IsDeleted` Field and Handling Logic

```csharp
// ✅ Correct when soft deletion is adopted
public class WorkItem : EsAggregateRoot<WorkItemId>
{
    public bool IsDeleted { get; private set; }  // Required soft-delete marker

    // Set IsDeleted = true when handling the deletion event
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case WorkItemDeleted e:
                IsDeleted = true;  // Mark as deleted
                break;
            // Other event handling...
        }
    }
}
```

---

### MAP-EVENTS-001

Strength: `invariant`. Target applicability: Order reconstruction replays persisted events without creating pending events, and tests verify clean rehydration behavior.

### Pending Domain Events After Reconstruction

An aggregate returned by `ToDomain()` MUST have no pending `DomainEvents`. Rehydration restores historical or persisted state; it does not represent a new business decision and MUST NOT cause those events to be published or persisted again.

- A rehydration constructor SHOULD replay historical events through `When(...)` or an equivalent state-transition path that does not enqueue them as new events.
- `ClearDomainEvents()` is not unconditionally required when the aggregate API explicitly guarantees that reconstruction leaves the pending-event collection empty.
- If the selected constructor or replay path emits or enqueues events, or its cleanliness contract is not explicit, the mapper MUST call `ClearDomainEvents()` before returning the aggregate.
- State-based fallback reconstruction follows the same rule; constructor side effects must not escape as pending events.

---

### MESSAGING-TX-001

Strength: `profile-default`. Target applicability: a message consumer requires atomic local business state, durable outgoing intent, and successful incoming-processing completion

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

### PROJECT-GRAMMAR-001

Strength: `profile-default`. Target applicability: The target adopts the conditional slnx navigation profile with bounded context DomainCore and Presentation solution folders.

### Workload Mapping

Rule ID: `PROJECT-GRAMMAR-001` (`profile-default`).

`workload` is a logical solution-navigation boundary, not a universal physical
directory name:

| Repository profile | `workload` means | Typical count | Example logical folders |
| --- | --- | --- | --- |
| micro-system / mini-system mono repo | one Bounded Context | one or more | `/Orders/DomainCore/`, `/Orders/Presentation/` |
| mono-system repository | the system represented by the repository | normally one | `/Commerce/DomainCore/`, `/Commerce/Presentation/` |

This mapping gives both profiles the same development navigation:

- `DomainCore` groups Domain, Application, and Infrastructure projects that
  realize the workload's business capability;
- `Presentation` groups runtime inbound adapters such as Web API, gRPC, worker,
  and MQ Consumer projects;
- tests, analyzers/tooling, BuildingBlocks, Shared Kernel, Published Language,
  and CrossCutting projects may remain explicit top-level capability groups;
- a target may retain a flat physical `src/` layout while using the logical
  `.slnx` grammar.

Do not create artificial Bounded Context folders in a mono-system repository
only to imitate a micro-system repo. Conversely, do not collapse real Bounded
Contexts in a micro-system mono repo into one layer-first solution view.

### TECH-SELECT-001

Strength: `invariant`. Target applicability: Testing, persistence, messaging, and observability choices are explicit, evidence-backed, and recorded in target configuration.

## Selection Record

Target selections belong in generated `.dev/project-config.yaml` under
`technologySelections`. Every record uses the schema in
`.ai/assets/skills/ai-context-init/templates/technology-selection.schema.yaml`.

```yaml
technologySelections:
  - slot: testing.mocking
    value: Moq
    status: selected
    source: explicit-target-decision
    evidence:
      - .dev/requirement/TECH-STACK-REQUIREMENTS.MD
    reason: Existing product test stack
```

Required semantics:

- `slot` is a stable dotted capability name, not a package-specific field;
- `value` is the target selection;
- `status` is `selected`, `not-applicable`, or `unresolved`;
- `source` is `repository-evidence` or `explicit-target-decision`;
- `evidence` contains repository-relative paths supporting the selection;
- `reason` explains an explicit override or unresolved decision.

An absent slot does not invent target truth. If the framework registers a
profile default for that slot, the default applies until target evidence records
another selection. A target override changes the selected technology, not the
architecture invariants surrounding it.

Recommended stable slots include:

- `testing.mocking`
- `testing.bdd-runner`
- `persistence.orm`
- `persistence.database`
- `messaging.broker`
- `messaging.framework`
- `observability.runtime`

New slots must reuse this record shape.

### TEST-BDDFY-001

Strength: `profile-default`. Target applicability: The dotnet-backend profile applies and the target explicitly selects the baseline-permitted plain-xUnit branch with mandatory GWT semantics.

### 3. Use GWT; Default to BDDfy

**Mandatory**: All tests must use Given-When-Then semantics and recognizable step names. Arrange-Act-Assert (3A) must not replace GWT. Use Case and integration tests default to BDDfy; plain xUnit may implement the same GWT structure only when the target team explicitly opts out of that package.

`.feature` files and runners are not minimum dependencies. When requirements directly provide a `.feature` file, its design or production is explicitly requested, or the target profile has adopted a runner, create or maintain it according to the [Gherkin Feature Storage Guide](../../../../../../.dev/specs/tests/GHERKIN-FEATURE-STORAGE-GUIDE.MD). Otherwise, express the scenario directly as a GWT-style C# test.

#### Step Methods And Scenario Readability

For scenario-style unit, Use Case and integration tests, the test method must
read as Given/When/Then step calls, directly or through the selected fluent
runner. Give methods behavior-specific names such as `GivenMonthlyBudget`,
`WhenQueryingBudget` and `ThenAmountShouldBe`; comments or generic `Setup`,
`Execute` and `Check` methods alone do not satisfy this form. Preserve the
compact exception-contract form explicitly permitted in section 5; it still
needs an observable exception assertion and source traceability.

| Step | Responsibility | Must not substitute for |
| --- | --- | --- |
| Given | Establish the scenario's data/state and controlled dependency responses. Put reusable construction mechanics in helpers. | The primary action or the scenario's outcome assertions. Fixture guards may fail fast but are not Then coverage. |
| When | Execute the real subject's primary behavior once per scenario/data row and capture its result, state or exception. An intentional multi-operation behavior must be explicit in the design. | A mock of the subject, a fabricated result, or a hidden repeat of the action during verification. |
| Then / And | Assert each specified observable value, relation, state, event or exception against the result of that When. | Re-executing the subject, calculating the expected answer using its algorithm, or merely checking that no exception occurred when a value is specified. |

Keep material inputs and expected values visible in the scenario method or its
explicitly bound theory row. A business-named builder may encapsulate irrelevant
defaults; it must not hide the values that distinguish scenarios. Use fresh
per-test state, instance fixtures with isolated scenario state, or explicit
arguments/results. Avoid static mutable scenario fields and test-order coupling.
A result field must distinguish "not executed" from a legitimate default result
(for example, nullable captured data with a Then assertion that it is present).

For asynchronous behavior, await the step to completion using the selected
runner's supported Task API. Do not use `async void`, fire-and-forget actions,
`.Wait()` or `.Result`. Capture expected exceptions during When (for example
with xUnit `Record.ExceptionAsync`) and assert the required type and relevant
details during Then; do not swallow exceptions to make the test green. A bounded
eventual assertion may wait for an observable asynchronous outcome, but must not
repeat the command/query that caused it.

Use the [GWT handoff contract](../../../../shared/GWT-TEST-HANDOFF-CONTRACT.md)
to preserve scenario/data-row IDs, source/AC bindings and every Then-to-assertion
mapping. Parameterized cases are valid when each row remains identifiable and
uses the same behavior and assertion responsibilities. A generated report,
method-name match, successful build or passing run alone cannot prove that the
scenario was implemented faithfully.

#### Default BDDfy Form

This excerpt's fixture and step implementations are in the
[runnable step-method example](../../examples/bdd-step-methods/README.md).
It exposes the behavior-bearing data while keeping mechanics inside steps.

```csharp
[Fact]
public void Should_return_zero_when_query_month_has_no_budget()
{
    this.Given(x => x.GivenMonthlyBudget("202102", 28m))
        .When(x => x.WhenQueryingBudget(
            new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2)))
        .Then(x => x.ThenAmountShouldBe(0m))
        .BDDfy();
}
```

#### Explicit Plain-xUnit Opt-Out Form

The same example includes a separately selected BDDfy opt-out. Opting out of
the package preserves method responsibilities and GWT semantics.

```csharp
[Fact]
public async Task Should_return_zero_when_query_month_has_no_budget()
{
    GivenMonthlyBudget("202102", 28m);
    var actual = await WhenQueryingBudget(
        new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2));
    ThenAmountShouldBe(actual, 0m);
}
```

Test the concrete Use Case directly for business-flow behavior and mock its
outbound ports. Handler adapter tests remain separate and narrow: verify only
Command-to-Input mapping, exactly one Use Case invocation, and delivery-specific
failure mapping. A Handler test that mocks a Repository must not duplicate
responsibility for business-flow testing.

---

### TEST-GWT-001

Strength: `invariant`. Target applicability: New and modified tests use recognizable Given-When-Then semantics regardless of the selected runner.

### 3. Use GWT; Default to BDDfy

**Mandatory**: All tests must use Given-When-Then semantics and recognizable step names. Arrange-Act-Assert (3A) must not replace GWT. Use Case and integration tests default to BDDfy; plain xUnit may implement the same GWT structure only when the target team explicitly opts out of that package.

`.feature` files and runners are not minimum dependencies. When requirements directly provide a `.feature` file, its design or production is explicitly requested, or the target profile has adopted a runner, create or maintain it according to the [Gherkin Feature Storage Guide](../../../../../../.dev/specs/tests/GHERKIN-FEATURE-STORAGE-GUIDE.MD). Otherwise, express the scenario directly as a GWT-style C# test.

#### Step Methods And Scenario Readability

For scenario-style unit, Use Case and integration tests, the test method must
read as Given/When/Then step calls, directly or through the selected fluent
runner. Give methods behavior-specific names such as `GivenMonthlyBudget`,
`WhenQueryingBudget` and `ThenAmountShouldBe`; comments or generic `Setup`,
`Execute` and `Check` methods alone do not satisfy this form. Preserve the
compact exception-contract form explicitly permitted in section 5; it still
needs an observable exception assertion and source traceability.

| Step | Responsibility | Must not substitute for |
| --- | --- | --- |
| Given | Establish the scenario's data/state and controlled dependency responses. Put reusable construction mechanics in helpers. | The primary action or the scenario's outcome assertions. Fixture guards may fail fast but are not Then coverage. |
| When | Execute the real subject's primary behavior once per scenario/data row and capture its result, state or exception. An intentional multi-operation behavior must be explicit in the design. | A mock of the subject, a fabricated result, or a hidden repeat of the action during verification. |
| Then / And | Assert each specified observable value, relation, state, event or exception against the result of that When. | Re-executing the subject, calculating the expected answer using its algorithm, or merely checking that no exception occurred when a value is specified. |

Keep material inputs and expected values visible in the scenario method or its
explicitly bound theory row. A business-named builder may encapsulate irrelevant
defaults; it must not hide the values that distinguish scenarios. Use fresh
per-test state, instance fixtures with isolated scenario state, or explicit
arguments/results. Avoid static mutable scenario fields and test-order coupling.
A result field must distinguish "not executed" from a legitimate default result
(for example, nullable captured data with a Then assertion that it is present).

For asynchronous behavior, await the step to completion using the selected
runner's supported Task API. Do not use `async void`, fire-and-forget actions,
`.Wait()` or `.Result`. Capture expected exceptions during When (for example
with xUnit `Record.ExceptionAsync`) and assert the required type and relevant
details during Then; do not swallow exceptions to make the test green. A bounded
eventual assertion may wait for an observable asynchronous outcome, but must not
repeat the command/query that caused it.

Use the [GWT handoff contract](../../../../shared/GWT-TEST-HANDOFF-CONTRACT.md)
to preserve scenario/data-row IDs, source/AC bindings and every Then-to-assertion
mapping. Parameterized cases are valid when each row remains identifiable and
uses the same behavior and assertion responsibilities. A generated report,
method-name match, successful build or passing run alone cannot prove that the
scenario was implemented faithfully.

#### Default BDDfy Form

This excerpt's fixture and step implementations are in the
[runnable step-method example](../../examples/bdd-step-methods/README.md).
It exposes the behavior-bearing data while keeping mechanics inside steps.

```csharp
[Fact]
public void Should_return_zero_when_query_month_has_no_budget()
{
    this.Given(x => x.GivenMonthlyBudget("202102", 28m))
        .When(x => x.WhenQueryingBudget(
            new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2)))
        .Then(x => x.ThenAmountShouldBe(0m))
        .BDDfy();
}
```

#### Explicit Plain-xUnit Opt-Out Form

The same example includes a separately selected BDDfy opt-out. Opting out of
the package preserves method responsibilities and GWT semantics.

```csharp
[Fact]
public async Task Should_return_zero_when_query_month_has_no_budget()
{
    GivenMonthlyBudget("202102", 28m);
    var actual = await WhenQueryingBudget(
        new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2));
    ThenAmountShouldBe(actual, 0m);
}
```

Test the concrete Use Case directly for business-flow behavior and mock its
outbound ports. Handler adapter tests remain separate and narrow: verify only
Command-to-Input mapping, exactly one Use Case invocation, and delivery-specific
failure mapping. A Handler test that mocks a Repository must not duplicate
responsibility for business-flow testing.

---

### TEST-MOCK-001

Strength: `profile-default`. Target applicability: Test projects use the explicitly recorded per-project Moq and NSubstitute selection.

### 6. Mocking Library Selection

NSubstitute is the `TEST-MOCK-001` profile default. Before generating or
reviewing mocks, resolve `testing.mocking` through
`.dev/project-config.yaml#technologySelections` and
[Target Technology Selection Policy](../../../../../../.dev/standards/TECHNOLOGY-SELECTION-POLICY.md).

- When no target selection exists, use NSubstitute.
- When an evidenced target selection exists, use that library consistently.
- Do not mix mocking libraries without an explicit migration decision.
- Changing the library does not change GWT, test independence, or boundary
  interaction rules.

```csharp
// ✅ Correct: NSubstitute
var repository = Substitute.For<IAggregateRepository<Product, ProductId>>();
repository.FindByIdAsync(Arg.Any<ProductId>(), Arg.Any<CancellationToken>())
    .Returns(Task.FromResult<Product?>(existingProduct));

// Verify the call
await repository.Received(1).SaveAsync(Arg.Any<Product>(), Arg.Any<CancellationToken>());

// Valid only when the target explicitly selects Moq
var repository = new Mock<IAggregateRepository<Product, ProductId>>();
repository.Setup(x => x.FindByIdAsync(...)).ReturnsAsync(existingProduct);
repository.Verify(x => x.SaveAsync(...), Times.Once);
```

---

## Target knowledge request routes

The target selects these twenty exact capability, operation and file-type request shapes for .NET work. The source example was checked against the previous target route inventory; this table records target intent without carrying old packet hashes or an execution receipt. Each selected normative knowledge resource still needs an explicit selection binding to this authority and an exact raw SHA-256. Apply individual rules only where their target predicate above holds.

| Route | Capability | Mode | Operations | File type |
| --- | --- | --- | --- | --- |
| `mq-route-01` | `implementation` | `command` | `implement` | `csharp-production` |
| `mq-route-02` | `specification` | `direct` | `draft`, `normalize` | `specification-markdown` |
| `mq-route-03` | `local-change` | `direct` | `implement` | `csharp-production` |
| `mq-route-04` | `implementation` | `generic` | `implement` | `csharp-production` |
| `mq-route-05` | `review` | `direct` | `review` | `dotnet-mixed-review` |
| `mq-route-06` | `local-change` | `direct` | `implement` | `csharp-test` |
| `mq-route-07` | `problem-framing` | `direct` | `draft`, `review-draft` | `problem-frame-yaml` |
| `mq-route-08` | `test-design` | `direct` | `design`, `review` | `gherkin-feature` |
| `mq-route-09` | `review` | `direct` | `review` | `csharp-review` |
| `mq-route-10` | `architecture` | `direct` | `design`, `review` | `architecture-decision` |
| `mq-route-11` | `local-change` | `direct` | `implement` | `project-file` |
| `mq-route-12` | `requirements` | `direct` | `draft`, `normalize` | `requirement-markdown` |
| `mq-route-13` | `test-design` | `direct` | `design`, `review` | `csharp-test` |
| `mq-route-14` | `compliance-validation` | `direct` | `assess-runtime`, `plan-validation`, `review-semantics` | `problem-frame-and-dotnet` |
| `mq-route-15` | `local-change` | `direct` | `implement` | `sql` |
| `mq-route-16` | `local-change` | `direct` | `implement` | `yaml-config` |
| `mq-route-17` | `implementation` | `generic` | `implement` | `csharp-test` |
| `mq-route-18` | `implementation` | `reactor` | `implement` | `csharp-production` |
| `mq-route-19` | `implementation` | `query` | `implement` | `csharp-production` |
| `mq-route-20` | `specification` | `direct` | `draft`, `normalize` | `specification-json` |

For these routes, `engineering-common` contributes `AICTX-EVIDENCE-001`, `ASSESSMENT-ARTIFACT-001`, and `TECH-SELECT-001`; `dotnet-backend` contributes the other eleven rule IDs. A package selection alone does not adopt any rule. Target configuration and the actual affected file determine applicability.

## Target customizations

These four target decisions remain effective. Historical base-framework, path and audit references in the old ledger are evidence only; this section states their active target meaning independently of the old schema.

### CUST-DOTNET-MQ-GOVERNANCE

Subject: `rule:downstream-ai-context-governance-projection`. Relationship: `extends`. Retained disposition: `merge`.

Merge the byte-exact v0.13 framework evolution while retaining target Issue-first authorization, repository governance and skill routing, directory-scoped .codex/agents tracking, the repository LF policy, and inactive profile/reuse/recipe boundaries. Adopt compact code-review routing without allowing package examples to replace target truth.

### CUST-DOTNET-MQ-VALIDATION

Subject: `contract:downstream-validation-runtime`. Relationship: `deviates`. Retained disposition: `merge`.

AICU-V010-PROJECTION-001, AICU-V011-SELECTION-001, AICU-V012-PROFILE-REGISTRY-PROJECTION-001, AICU-V012-COMMIT-CUTOVER-001, AICU-V012-COMMIT-DOC-001, AICU-V013-ROUTING-PROJECTION-001, AICU-V013-COMPONENT-OWNERSHIP-001, and AICU-V013-PREACTION-PACKET-BOOTSTRAP-001 require the SHA-pinned downstream-applicable target gate and prospective target policy. Do not claim stock profiles, changed-path execution, reuse, or source-only tests passed.

### CUST-DOTNET-MQ-REPO-TRUTH

Subject: `contract:target-repository-truth-boundary`. Relationship: `target-only`. Retained disposition: `retain`.

Preserve repository identity, .NET SDK and product truth, target catalogs and workflow authorities, complete analyzer/tools retirement, and inactive recipe boundaries while adopting v0.13 exact framework paths and removal of the bundled provider payload.

### CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION

Subject: `rule:target-execution-provenance-adoption-boundary`. Relationship: `deviates`. Retained disposition: `merge`.

Adopt AI execution provenance prospectively from 2026-08-12T22:08:09+08:00 and commit-subject grammar from 2026-08-13T11:05:12+08:00 without history rewrite. Preserve only the exact ad194beb3fb61a18b6870093b704264746c1516b / ASM-20260812-002 / missing-matching-trailer waiver in the target-owned fail-closed overlay while canonical v0.13 framework bytes remain exact.

## Repository-specific applications

- Inventory uses EF Core; Products and Orders use Dapper. Do not generalize a persistence choice across bounded contexts. Procurement is now a fourth business context; the Frontend and supplier lab are current project facts.
- Plain xUnit v3 with Given-When-Then semantics is the target testing choice. The baseline-permitted BDDfy opt-out remains effective. Each test project chooses Moq or NSubstitute from its actual configuration.
- Preserve Issue-first authorization, target-owned Git attribution and subject grammar, directory-scoped runtime metadata tracking, LF policy and explicit routes. Historical workflow evidence is not a current RC2 check.
- AI attribution applies prospectively from `2026-08-12T22:08:09+08:00`; commit-subject grammar applies prospectively from `2026-08-13T11:05:12+08:00`. The sole historical missing-matching-trailer exception is commit `ad194beb3fb61a18b6870093b704264746c1516b` for `ASM-20260812-002`; it grants no general waiver.
- Any applicable review or validation reports its actual result. Deferred, blocked and not-applicable are not passed. The RC2 adoption exception skips S6, runtime and upgrade/recovery experiments this time and does not activate CI.
## Target Git message and attribution contract

The current target policy remains [GIT-COMMIT-POLICY.yaml](../standards/GIT-COMMIT-POLICY.yaml) with its [human guide](../standards/GIT-COMMIT-POLICY.md). Its SHA-256 at this adoption base is `a933d39f4f2f082c1bffc43bb8ec8f8b6d7686ef9bd9597f7c90937d8f1c60ea`. The active subject grammar is `<type>(#<issue-number>[,#<issue-number>...]): <summary>` when an issue exists, or `<type>(<lowercase-boundary-scope>): <summary>` otherwise. The allowed types are `docs`, `workflow`, `feat`, `fix`, `refactor`, `test`, `chore`, and `merge`; a literal pipe is not part of the current grammar. Workflow commits include `Why`, `What`, `Validation`, and `Workflow` body sections with the actual workflow identity.

Agent-assisted commits end with a matching `Co-Authored-By: <runtime> (<model>, <reasoning_effort>) <noreply@provider>` trailer. The trailer must describe actual execution, and every present AI trailer must match the policy. Assessment commits use the applicable `Assessment-Id` trailer. The target cutover times and sole historical exception are recorded above; they do not authorize any new waiver or history rewrite.

The obsolete RC1 pinned target validator was removed. A replacement target-local automated validator is not configured by this adoption. For this workflow's planned commit only, the coordinator selected the matching source repository validator against an exact message file, with the source checkout as the execution directory. That check validates this message alone; it is not a target-history or RC2 gate pass.
