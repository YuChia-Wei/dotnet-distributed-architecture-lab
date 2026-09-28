# Distributed Commerce Bounded Context Overview

## Metadata
- Version: 0.3
- Date: 2026-09-28
- Owner: Architecture / Documentation Workflow
- Scope: Active `Products`, `Orders`, `Inventory`, and `Procurement` bounded-context baseline

## Context & Goals

This repository models a distributed commerce sample system using DDD, Clean Architecture, Hexagonal Architecture, CQRS, and explicit integration boundaries. Orders-to-Inventory reservation and Procurement-to-Inventory receipts use MQ; Procurement reaches the external supplier through configured HTTP profiles.

The current codebase centers on four business bounded contexts:

- `Products`
- `Orders`
- `Inventory`
- `Procurement`

`SupplierSandbox` and `SupplierMock` are external-system lab samples. The two Vue frontends and YARP are user-interface and routing adapters, not bounded contexts.

The goal of this document is to provide the minimum project-specific requirement truth needed before deeper spec completion and runtime operations documentation.

## Personas

- Product maintainer
  - manages sellable product information
- Order maintainer
  - handles order placement and lifecycle transitions
- Inventory maintainer
  - manages available stock and stock adjustments
- Procurement maintainer
  - manages supplier purchases, uncertain outcomes, and actual goods receipts
- AI / human maintainer
  - needs a clear bounded-context map and integration constraints before refactoring or extending the system

## Functional Requirements

### Products bounded context

- The system must allow creating a product with name, description, and price.
- The system must allow updating existing product information.
- The system must allow deleting a product.

### Orders bounded context

- The system must allow placing an order for a product.
- The order flow must include product identity, product name, quantity, order date, and total amount.
- The order lifecycle must support shipped, delivered, and cancelled transitions.

### Inventory bounded context

- The system must track stock per product.
- The system must support increasing stock, decreasing stock, and restocking.
- The inventory context must reject stock decreases when available stock is insufficient.

### Procurement bounded context

- The system must allow a supplier quote, single-product purchase creation and lookup, reconciliation of an uncertain supplier submission, and partial goods receipts.
- Procurement must reject over-receipt and conflicting reuse of a receipt identity.

### Cross-context collaboration

- Orders must not directly call another bounded context through web API.
- Order placement must collaborate with Inventory through MQ-first contracts and gateways.
- Inventory must publish integration events when stock changes materially affect other bounded contexts.
- Procurement must keep a stable client request identity when submitting or reconciling a supplier purchase through its selected fixed HTTP profile.
- A supplier acceptance must not increase stock. A first committed actual goods receipt must publish `GoodsReceived`; Inventory must apply it idempotently despite possible redelivery.

## Non-Functional Requirements

- The implemented Orders-to-Inventory and Procurement-to-Inventory collaborations use MQ contracts. Procurement's supplier connection uses configured HTTP profiles.
- The system must remain compatible with eventual consistency across bounded contexts.
- Products, Orders, and Procurement use Dapper + Npgsql. Inventory uses EF Core with the Npgsql provider.
- The documentation system must preserve enough truth for maintainers to map code changes back to bounded-context responsibilities.

## Constraints & Assumptions

- Target stack is .NET 10, WolverineFx, PostgreSQL 16, and canonical Kafka. RabbitMQ remains a compatibility profile; Kafka + RabbitMQ dual broadcast is the target direction but needs destination-aware outbox state and fanout topology before activation.
- Bounded contexts currently visible in `src/` are treated as the active project truth.
- This document does not yet define every use case in the system; it only establishes the current bounded-context baseline.

## Domain / Business Rules

- Product price cannot be negative.
- Inventory decreases must fail when stock is insufficient.
- Orders require successful inventory reservation before final order placement succeeds.
- Only actual goods receipt, not supplier acceptance, increases Inventory stock.
- Cross-context communication must use contracts and integration events, not direct internal model sharing.

## Acceptance Criteria

- A maintainer can identify the active bounded contexts from `.dev/requirement/` without relying on `src/` discovery alone.
- A maintainer can tell that Orders and Inventory collaborate through MQ-first integration.
- A maintainer can distinguish Procurement's supplier HTTP boundary from its Kafka receipt event to Inventory.
- Later specs can expand from this document without re-deciding the system’s top-level bounded-context split.

## References

- `.dev/ARCHITECTURE.md`
- `.dev/project-config.yaml`
- `src/Product/`
- `src/Order/`
- `src/Inventory/`
- `src/Procurement/`
- `src/BC-Contracts/`
- `.dev/operations/procurement-supplier-lab.md`
