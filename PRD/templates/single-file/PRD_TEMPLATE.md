# Product Requirements Document (PRD) Template

## 1. Project Overview
- Summary: one paragraph describing the problem, users, and expected outcome.
- Scope: what is included vs. excluded for this delivery.
- Stakeholders: product, engineering, QA, design, ops.

## 2. Goals and Objectives
- Business goals: measurable outcomes (e.g., +10% conversion).
- User goals: key jobs-to-be-done and success criteria.
- Metrics: KPIs and how they are measured.

## 3. Functional Requirements
- User stories / use cases with acceptance criteria.
- Screens/flows or API behaviors per use case.
- Data model notes (entities, key fields, relationships).

## 4. Non-functional Requirements
- Performance (e.g., P95 < 200ms, throughput).
- Reliability (timeouts, retries, idempotency, durability).
- Security/privacy (authN/Z, PII handling, OWASP).
- Scalability, observability, internationalization.

## 5. System Architecture
- Approach: reference patterns such as Domain-Driven Design (DDD), CQRS, and Clean Architecture.
- Bounded contexts and service boundaries.
- Key components and interactions (diagrams optional).
- Messaging/brokers (Kafka/RabbitMQ), storage (PostgreSQL), and deployment targets.

## 6. API Design (RESTful)
- Resource model and nouns (plural).
- Endpoints with methods, paths, and status codes.
  - Example: `POST /orders` → 201 with body `{ id }`
  - Example: `GET /products/{id}` → 200 with `ProductDto`
- Request/response schemas, validation, error contracts.

## 7. Constraints and Assumptions
- Technical constraints (SDKs, frameworks, versions).
- Operational constraints (environments, quotas, SLAs).
- Assumptions and known risks.

## 8. Milestones and Timeline (optional)
- Phases, target dates, and dependencies.

## 9. Appendix (optional)
- Glossary, links to tickets/designs, sample payloads, and diagrams.

