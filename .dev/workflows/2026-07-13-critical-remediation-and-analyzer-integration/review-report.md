# Repository Assessment And Remediation Review

## Template Metadata

- `template_id`: `dev-workflow/development-review-report`
- `template_version`: `1.0.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-07-10T18:25:11+08:00`

## Report Metadata

- `workflow_id`: `2026-07-13-critical-remediation-and-analyzer-integration`
- `report_id`: `development-review-2026-07-13-critical-remediation-and-analyzer-integration`
- `owner_skill`: `code-reviewer`
- `related_plan_id`: `development-plan-2026-07-13-critical-remediation-and-analyzer-integration`
- `status`: `final`
- `created_at`: `2026-07-13T22:37:26+08:00`
- `updated_at`: `2026-07-13T22:37:26+08:00`
- `template_source`: `.ai/assets/skills/dev-workflow/templates/development-review-report-template.md`
- `template_version`: `1.0.0`
- `workflow_locator`: `.dev/workflows/2026-07-13-critical-remediation-and-analyzer-integration/workflow.yaml`

## Scope

- Development stage: Pre-remediation repository assessment.
- Reviewed target: `src/`, `tests/`, messaging and runtime configuration, operations documentation, and analyzer/validation tooling.
- Review boundaries: DDD, Clean Architecture, CQRS, Event Sourcing, MQ durability, test quality, maintainability, operations, security and developer experience.
- Out of scope: No remediation was performed during the assessment; production behavior was not exercised against a running broker/database topology.

## Score

| Dimension | Weight | Score | Weighted Result |
| --- | ---: | ---: | ---: |
| Architecture, DDD, CQRS and Event Sourcing | 30% | 64 | 19.2 |
| MQ and distributed reliability | 20% | 46 | 9.2 |
| Test quality and coverage | 20% | 38 | 7.6 |
| Code quality and maintainability | 15% | 78 | 11.7 |
| Operations, observability and security | 10% | 55 | 5.5 |
| Documentation and developer experience | 5% | 86 | 4.3 |
| **Total** | **100%** | | **57.5 / 100** |

Interpretation: approximately 72/100 as an architecture lab and 43/100 for production readiness. The repository has a strong educational architecture skeleton but lacks sufficient Event Sourcing correctness, durable messaging evidence and test protection for production use.

## Findings

### ARC-001 — Event-Sourced Aggregate Persistence Lifecycle Is Incomplete

- Severity: `CRITICAL`
- Evidence: `src/Order/DomainCore/SaleOrders.Infrastructure/Applications/Repositories/OrderEventSourcingRepository.cs:113-176`; `src/BuildingBlocks/Lab.BuildingBlocks.Domains/AggregateRoot.cs:14`.
- Impact: After a successful append, the aggregate version is not advanced and pending domain events are not cleared. Re-saving the same instance can fail optimistic concurrency or replay the same pending events.
- Required action: Define and implement the post-commit aggregate lifecycle, including version advancement, pending-event cleanup and regression tests.

### ARC-002 — Order Event-Sourced State And Legal Transitions Are Not Fully Protected

- Severity: `CRITICAL`
- Evidence: `src/Order/DomainCore/SaleOrders.Domains/Order.cs:63-102`.
- Impact: `Status` is initialized outside `When`, and the aggregate permits illegal transitions such as shipping a cancelled order or delivering a placed order.
- Required action: Keep ES state mutation inside replay-safe transitions and enforce the legal state-transition matrix with GWT tests.

### MSG-001 — Durable Outbox Is Not Demonstrably Transactional

- Severity: `CRITICAL`
- Evidence: `src/Order/Presentation/SaleOrders.WebApi/Program.cs:30`; `src/Order/DomainCore/SaleOrders.Applications/Commands/PlaceOrderCommand.cs:90-115`; `src/Order/DomainCore/SaleOrders.Infrastructure/Applications/Repositories/OrderEventSourcingRepository.cs:167`.
- Impact: Durable outbox/inbox is declared without an observed Wolverine persistence provider or a transaction shared with Dapper/event-store commits. A process failure after commit and before publish can lose an integration event.
- Required action: Select and prove a durable message persistence/transaction boundary, then add failure-window integration tests.

### ARC-003 — Aggregate Repository And CQRS Boundaries Are Mixed

- Severity: `MUST FIX`
- Evidence: `src/BuildingBlocks/Lab.BuildingBlocks.Application/IDomainRepository.cs:11-49`; `src/Order/DomainCore/SaleOrders.Applications/Repositories/IOrderDomainRepository.cs:8-48`; `src/Order/DomainCore/SaleOrders.Infrastructure/Applications/Repositories/OrderEventSourcingRepository.cs:82`.
- Impact: Writable repositories expose batch and physical-delete operations, while the Order repository combines command and query operations. Query paths replay event streams and list queries can become N+1 event rehydration.
- Required action: Establish the portable aggregate write contract and a separate read-only query port/read model.

### MSG-002 — RabbitMQ Inventory Reservation Topology Is Incomplete

- Severity: `MUST FIX`
- Evidence: `src/Inventory/Presentation/InventoryControl.WebApi/Program.cs:30-60`; `src/Order/Presentation/SaleOrders.WebApi/Program.cs:66`.
- Impact: Kafka has the request/reply wiring, but the RabbitMQ branch does not listen to `inventory.requests`, so the Order flow can wait for a consumer that does not exist.
- Required action: Either implement and test broker parity or explicitly remove the unsupported claim/configuration.

### MSG-003 — Product Integration Publisher Is Not Connected To Product Behavior

- Severity: `MUST FIX`
- Evidence: `src/Product/DomainCore/SaleProducts.Infrastructure/BuildingBlocks/IntegrationEventPublisher.cs:7`; `src/Product/DomainCore/SaleProducts.Infrastructure/Repositories/ProductDomainRepository.cs:107`.
- Impact: Infrastructure and a route exist, but no Product use case publishes a Product integration contract and the domain dispatcher has no confirmed execution path.
- Required action: Define the Product integration-event ownership and connect a durable publisher path, or remove the inactive topology.

### MSG-004 — Reservation Idempotency And Failure Policy Are Missing

- Severity: `MUST FIX`
- Evidence: `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/Interactions/ReserveInventoryRequestContract.cs:9`; `src/Inventory/Presentation/InventoryControl.WebApi/RequestContractConsumers/ReserveInventoryRequestContractHandler.cs:18`.
- Impact: Reservation requests have no stable operation ID, while explicit retry/backoff, poison-message and dead-letter policy is absent. Retrying a timed-out logical operation can deduct inventory twice.
- Required action: Define idempotency identity, persistence and retry/dead-letter behavior with duplicate-delivery tests.

### MSG-005 — RabbitMQ Configuration Shape Is Inconsistent

- Severity: `MUST FIX`
- Evidence: `src/Inventory/Presentation/InventoryControl.WebApi/Program.cs:54`; `src/Inventory/Presentation/InventoryControl.WebApi/appsettings.json:2`.
- Impact: Code reads `GetConnectionString("MessageBroker")`, while appsettings uses `MessageBroker.ConnectionString`, which can pass null to URI creation outside Compose overrides.
- Required action: Use one configuration contract and validate it at startup and in configuration tests.

### TEST-001 — Critical Behavior Coverage And Test Conventions Are Insufficient

- Severity: `MUST FIX`
- Evidence: The code graph found approximately 15 Use Case classes but direct test evidence for only about four; no Inventory test project exists. `tests/SaleProducts.Domains.Tests/ProductTests.cs:8-61` and `tests/SaleOrders.Domains.Tests/OrderTests.cs:10-18` use traditional 3A/direct event-list assertions; Order application tests use Moq instead of the repository standard.
- Impact: Inventory, PlaceOrder, Ship, Deliver and multiple Product behaviors can regress without detection, while tests do not validate observable outbox/message outcomes.
- Required action: Add risk-ordered GWT coverage using the approved test doubles and observable boundaries.

### TEST-002 — Test Host Execution Is Not Deterministic

- Severity: `MUST FIX`
- Evidence: `tests/SaleOrders.Tests/GetOrderDetailsEndpointTests.cs:58-80` starts the full Wolverine/Kafka host; the two Domain test projects omit `Microsoft.NET.Test.Sdk`. During assessment, full solution tests aborted or hung despite no remaining test process or locked test DLL.
- Impact: Offline/local verification depends on broker availability or incomplete transitive testhost assets and can leave misleading results.
- Required action: Add explicit test SDK dependencies, isolate external broker startup from endpoint tests, and run sequential hang-dump-enabled validation.

## Strengths

- Product, Order and Inventory bounded contexts remain isolated through BC contracts and gateway ports.
- Most application operations expose explicit Use Case boundaries and cancellation tokens.
- Kafka topic separation and observability instrumentation are clear.
- The production solution builds successfully; code graph complexity across 197 production methods peaks at cyclomatic complexity 7.
- Analyzer self-tests pass 47/47 and runtime validation helper tests pass 2/2.
- The quick repository gate passes all six required checks.

## Test Process Diagnostic Addendum

- No `testhost`, `vstest.console` or `dotnet test` process remained after the assessment.
- The only observed `dotnet` processes belonged to Rider MSBuild, Roslyn and OpenTelemetry; none were terminated.
- All discovered test output DLLs could be opened with exclusive file sharing, so there was no lock evidence.
- The most likely endpoint-test blocker is full-host Kafka auto-provision/retry behavior; Windows Event Log access was a secondary logging failure.

## Analyzer Integration Assessment

- `DotnetBackendAnalyzers` is suitable for source-included build-time use through `OutputItemType="Analyzer"` and `ReferenceOutputAssembly="false"`.
- The integration must be scoped to `src/` so analyzer/tool projects do not self-reference.
- `DBA1001` must initially remain a warning linked to ARC-003 because the current repository contract intentionally fails that rule; it becomes an error only after remediation.
- `DotnetBackendValidation` is currently not applicable to product code because its EF projection-registration helper has no matching EF projection marker/model in this Dapper-based implementation. It remains a tested tool rather than a production runtime dependency.

## Validation

- Checks performed: codebase-memory graph review; targeted source/config review; `dotnet build MQArchLab.slnx --no-restore`; analyzer tests; runtime validation tests; `check-all.sh --quick`; process and file-lock inventory.
- Results: Build and tooling checks passed. Full product tests did not complete deterministically for the reasons recorded in TEST-002.
- Skipped checks and reasons: End-to-end broker/database execution was not attempted because the required topology was not established as part of the review.

## Decision

- Result: `changes-requested`
- Residual risks: Production message loss, duplicate inventory reservation, invalid order transitions, incomplete event lifecycle and insufficient automated protection.
- Recommended next development stage: Integrate analyzers as a bounded tooling slice, then record architecture decisions before critical product remediation.
