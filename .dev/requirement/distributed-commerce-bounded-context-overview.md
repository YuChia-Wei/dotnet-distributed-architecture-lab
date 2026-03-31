# Distributed Commerce Bounded Context Overview

## Metadata
- Version: 0.1
- Date: 2026-03-31
- Owner: Architecture / Documentation Workflow
- Scope: In

## Context & Goals

This repository models a distributed commerce sample system using DDD, Clean Architecture, Hexagonal Architecture, CQRS, and MQ-first bounded-context integration.

The current codebase centers on three bounded contexts:

- `Products`
- `Orders`
- `Inventory`

The goal of this document is to provide the minimum project-specific requirement truth needed before deeper spec completion and runtime operations documentation.

## Personas

- Product maintainer
  - manages sellable product information
- Order maintainer
  - handles order placement and lifecycle transitions
- Inventory maintainer
  - manages available stock and stock adjustments
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

### Cross-context collaboration

- Orders must not directly call another bounded context through web API.
- Order placement must collaborate with Inventory through MQ-first contracts and gateways.
- Inventory must publish integration events when stock changes materially affect other bounded contexts.

## Non-Functional Requirements

- Cross-bounded-context integration must be MQ-only.
- The system must remain compatible with eventual consistency across bounded contexts.
- Write-side persistence must remain Dapper + Npgsql oriented.
- Query/read-side persistence may use EF Core or Dapper.
- The documentation system must preserve enough truth for maintainers to map code changes back to bounded-context responsibilities.

## Constraints & Assumptions

- Target stack is .NET 10, WolverineFx, PostgreSQL 16, RabbitMQ, and Kafka.
- Bounded contexts currently visible in `src/` are treated as the active project truth.
- This document does not yet define every use case in the system; it only establishes the current bounded-context baseline.

## Domain / Business Rules

- Product price cannot be negative.
- Inventory decreases must fail when stock is insufficient.
- Orders require successful inventory reservation before final order placement succeeds.
- Cross-context communication must use contracts and integration events, not direct internal model sharing.

## Acceptance Criteria

- A maintainer can identify the active bounded contexts from `.dev/requirement/` without relying on `src/` discovery alone.
- A maintainer can tell that Orders and Inventory collaborate through MQ-first integration.
- Later specs can expand from this document without re-deciding the system’s top-level bounded-context split.

## References

- `.dev/ARCHITECTURE.MD`
- `.dev/project-config.yaml`
- `src/Product/`
- `src/Order/`
- `src/Inventory/`
- `src/BC-Contracts/`
