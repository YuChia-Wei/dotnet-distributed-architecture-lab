# Repository Structure Inventory

## Metadata

- workflow_id: `2026-07-13-repo-structure-sync`
- owner_skill: `repo-structure-sync`
- created_at: `2026-07-13T20:56:07+08:00`
- updated_at: `2026-07-13T20:56:07+08:00`
- template_source: `.ai/assets/skills/repo-structure-sync/references/output-contract.md`
- template_version: `1.0`

## 1. Evidence Used

- `git diff 780dcac e8e3f85` and commit `e8e3f85` history
- `global.json`, `MQArchLab.slnx`, all `src/`, `tests/`, and `tools/` project files
- codebase-memory graph index and searches for bounded-context use cases, aggregates, contracts, controllers, repositories, and integration events
- `docker-compose/docker-compose.yml`, host Dockerfiles, and runtime configuration
- pre-refresh target documents from commit `780dcac`, treated only as secondary evidence

## 2. Target Repository Mode

Existing product repository with a copied/refreshed AI context framework that replaced or removed some target-repository truth.

## 3. Confirmed Repo Facts

- .NET SDK 10.0.0; product projects target `net10.0`.
- Active bounded contexts are Products, Orders, and Inventory.
- Each context has Domain, Application, Infrastructure, Web API, and Consumer projects.
- Product solution has 22 source projects and four Products/Orders test projects.
- Kafka is active in Compose; RabbitMQ packages and conditional configuration remain supported but its Compose service is disabled.
- Product persistence uses Dapper/Npgsql/PostgreSQL; EF Core is not referenced by product source projects.
- Orders-to-Inventory reservation uses Wolverine request/reply contracts.
- Roslyn analyzers and runtime validators exist under `tools/` outside the main solution.

## 4. Project Config Decision

Regenerate `.dev/project-config.yaml` from the canonical template shape. Do not restore the historical config because it contained unrelated frontend claims, credentials, connection strings, ports, and source-repository database facts.

## 5. Copied or Stale Template Facts

- Root `AGENTS.md`, `agents.zh-tw.md`, `.dev/ARCHITECTURE.md`, and tech-stack requirements described the repository as only a reusable framework.
- Source-repository backlog items referenced workflows that were not copied and caused workflow validation to fail.
- The root README retained stale versions, only two bounded contexts, and directories no longer present.
- The refresh deleted valid Products/Orders/Inventory requirements, specs, test specs, MQ operations docs, and the Orders place-order frame.
- A deleted Payments frame had no current source/solution evidence and must remain removed.

## 6. P0 Hits

- Current entry docs materially conflicted with solution/project/runtime evidence.
- Architecture-facing documents required a fresh target-repository narrative rather than direct substitution.

## 7. P1 Hits

- Multiple host types exist: three Web APIs and three Consumers.
- The copied context contained many source-repository records and stale facts that do not map to the target repo.

## 8. Complexity Verdict

Escalated/high-synthesis sync. The main agent owns integration and final judgment; after explicit user authorization, bounded read-only sub-agents review entry facts, restored artifacts, and validation evidence without editing shared files.

## 9. Safe Direct Updates

- Root README identity, versions, structure, and run guidance
- project config and architecture/tech-stack entry documents
- AGENTS repository identity and navigation sections while preserving collaboration rules
- `.dev` indexes and operations/spec discovery statements
- removal of source-repository backlog items

## 10. Escalation Targets

- Full spec compliance remains a later `spec-compliance-validator` concern after behavior changes.
- Architecture redesign is out of scope; use `ddd-ca-hex-architect` if current implementation boundaries are to change.

## 11. Source Packet

- Three bounded contexts: Products, Orders, Inventory
- Six runtime hosts: one Web API and one Consumer per context
- Persistence: PostgreSQL 16, Dapper 2.1.72, Npgsql 10.0.2
- Messaging: WolverineFx 5.32.1, Kafka active, RabbitMQ optional/disabled in Compose
- Restorable target truth: current-context requirements/specs/tests/operations and Orders place-order frame
- Excluded copied truth: upstream backlog/workflows, Payments frame, old credential-bearing project config
