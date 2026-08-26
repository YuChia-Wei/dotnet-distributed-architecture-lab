# Specs Index

This index owns the file and directory catalog for `.dev/specs/`.

## Entry Files

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.dev/specs/`. |
| `INDEX.MD` | File and directory catalog for specs. |
| `SPEC-GUIDE.MD` | Spec authoring guide. |
| `SPEC-ORGANIZATION-GUIDE.MD` | Spec organization and target-repo placement guide. |

## Test Specs

| Path | Description |
| --- | --- |
| `tests/README.MD` | Test-spec area purpose and usage. |
| `tests/TEST-SPEC-GUIDE.MD` | Test-spec authoring guide. |
| `tests/GHERKIN-FEATURE-STORAGE-GUIDE.MD` | Gherkin feature storage guidance. |
| `tests/cross-domain/` | Cross-bounded-context test spec area. |
| `tests/e2e/` | End-to-end journey test spec area. |
| `tests/product/` | Product aggregate, use-case, and persistence test design; implementation coverage is partial. |
| `tests/order/` | Order aggregate, use-case, lifecycle, and messaging test design; most listed scenarios are planned. |
| `tests/inventory-item/` | Planned Inventory aggregate, use-case, persistence, and publication tests; no Inventory test project exists yet. |

## Target-Repo Production Specs

| Path | Description |
| --- | --- |
| `domains/product/` | Product aggregate, command/query use-case, and HTTP adapter specs. |
| `domains/order/` | Event-sourced Order aggregate, lifecycle/query use-case, and HTTP adapter specs. |
| `domains/inventory-item/` | InventoryItem aggregate, stock/query/reservation use-case, and HTTP adapter specs. |

## System Reconstruction Specs

| Path | Description |
| --- | --- |
| `reconstruction/README.MD` | Source-independent reconstruction entrypoint and authority order. |
| `reconstruction/system-blueprint.md` | DDD/Clean Architecture/Hexagonal/MQ-first implementation blueprint. |
| `reconstruction/project-manifest.json` | Machine-readable solution, project, dependency, SDK, and validation manifest. |
| `reconstruction/coverage-matrix.md` | Aggregate, use-case, adapter, persistence, messaging, test, and gap coverage ledger. |
| `reconstruction/reconstruction-procedure.md` | Ordered build and fresh-context acceptance procedure. |
| `reconstruction/http-api-contracts.json` | HTTP endpoint, DTO, status, and error mapping contract. |
| `reconstruction/message-contracts.json` | Published Language, channel, idempotency, and delivery contract. |
| `reconstruction/persistence-contracts.json` | Database schema, concurrency, transaction, event-store, and outbox contract. |
| `reconstruction/runtime-contracts.json` | Host, profile, topology, observability, and container contract. |

These target-repository specs were retained because matching aggregates and use cases exist under `src/`. Use `spec-compliance-validator` before treating them as a 100% compliance claim after product behavior changes.
