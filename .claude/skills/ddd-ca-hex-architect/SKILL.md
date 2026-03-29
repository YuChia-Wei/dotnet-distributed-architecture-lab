---
name: ddd-ca-hex-architect
description: Design and refactor architecture in this repository using DDD, Clean Architecture, CQRS, MQ-first integration, and a Hexagonal Architecture view of ports and adapters. Use when Codex needs to shape bounded contexts, aggregates, commands, queries, reactors, contracts, project structure, ADR-aligned refactors, or reusable AI prompts/workflows for this repo's .NET stack.
---

# DDD CA HEX Architect

## Overview

Use this skill to turn the repository's canonical AI assets, `.dev` standards, and ADR rules into one architecture workflow.
Treat `HEX` as the Hexagonal Architecture view inside the repo's existing DDD + Clean Architecture setup: define inbound/outbound ports clearly, keep domain and application pure, and isolate adapters in infrastructure or presentation.

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read [references/source-map.md](references/source-map.md) to choose the relevant prompt family and design slice.
3. Read [references/architecture-playbook.md](references/architecture-playbook.md) for repo-level constraints before proposing a design.
4. Read [references/design-deliverables.md](references/design-deliverables.md) when the user wants a concrete artifact such as an architecture outline, implementation plan, prompt rewrite, or refactor blueprint.
5. Read [references/prompt-templates.md](references/prompt-templates.md) when the user needs examples of how to invoke this skill from a prompt.
6. If the task touches a specific implementation area, load only the matching source prompt or ADR rather than bulk-reading the entire `.ai` tree.

## Workflow

### 1. Frame the design problem
Classify the task first:
- Bounded context or module boundary
- Aggregate and domain behavior
- Command/query/reactor/reconciler flow
- Integration contract or MQ choreography
- Infrastructure profile, outbox, or persistence mode
- Prompt/skill/workflow redesign for future AI agents

### 2. Choose the architecture lens
Apply all three lenses together:
- `DDD`: bounded context, ubiquitous language, aggregate boundary, invariants, domain events
- `CA`: dependency direction, layer responsibilities, DTO/application/domain separation
- `HEX`: inbound port, outbound port, adapter placement, broker/database/API boundaries

### 3. Bind the design to repo rules
Always align with these repository constraints:
- Cross-bounded-context communication must use MQ only; web API between BCs is forbidden.
- Write side uses Dapper + Npgsql; read/projection side uses EF Core or Dapper.
- DI uses `IServiceCollection`; no attribute scanning.
- Repository rule stays generic; do not invent custom repository interfaces for domain behavior.
- Commands mutate state, queries never mutate, reactors react to event data rather than domain entities.
- Testing uses xUnit + NSubstitute; no `BaseTestClass`.

### 4. Select the minimal prompt/reference set
Do not dump every prompt into context.
Load only the prompt family that matches the current design decision:
- aggregate
- command/query
- reactor
- controller
- review/validation
- profile/outbox
- frontend integration if the boundary includes UI contracts

### 5. Produce an architect-grade output
Default output structure:
1. Context and goal
2. Proposed architecture decisions
3. Layer and adapter placement
4. Message, DTO, and persistence impact
5. Files/prompts/ADRs to update
6. Risks, tradeoffs, and open questions

Prefer decisions and rationale over raw code unless the user explicitly asks for implementation.

## Design Rules

### Bounded Context Design
- Keep language and ownership explicit for each BC.
- Put cross-BC contracts in `src/BC-Contracts`.
- Keep `src/BuildingBlocks` framework-like and business-agnostic.
- Keep `src/Shared` for true shared kernel concepts only; do not leak BC-specific behavior into it.

### Aggregate Design
- Model one aggregate root per consistency boundary.
- Put invariants and state transitions inside the aggregate, not controllers or mappers.
- If event sourcing applies, state changes must happen through event application only.
- Emit domain events with metadata for audit and traceability.

### Use Case and Port Design
- Model commands as inbound application ports that change state.
- Model queries as inbound application ports that return DTO/projection data only.
- Model outbound ports around persistence, message publishing, clock, identity, or external services.
- Keep adapters thin and technology-facing.

### MQ and Integration Design
- Prefer integration events for BC collaboration.
- Design reactors for eventual consistency, not synchronous domain orchestration across BCs.
- Keep event payloads stable, explicit, and serialization-friendly.
- When outbox is required, design persistence, mapping, and publishing as one unit.

### Prompt Refactoring Rules
- Convert task-specific prompt fragments into reusable decision-oriented references.
- Keep `SKILL.md` procedural and short; move detailed maps and examples into `references/`.
- Preserve file-path level traceability back to `.ai/assets` and `.dev` documents so future edits know the source of truth.

## Output Expectations

When producing an architecture artifact, include:
- Target bounded context or module
- Aggregate or use case ownership
- Inbound ports, outbound ports, and adapters
- Command/query/reactor boundaries
- Persistence mode and messaging impact
- Required updates to prompts, docs, ADRs, or project structure

If information is missing, make the smallest safe assumption and label it clearly.
If the task conflicts with an ADR or mandatory repo rule, call out the conflict before proposing implementation steps.

## References

- [references/source-map.md](references/source-map.md)
- [references/architecture-playbook.md](references/architecture-playbook.md)
- [references/design-deliverables.md](references/design-deliverables.md)
- [references/prompt-templates.md](references/prompt-templates.md)
