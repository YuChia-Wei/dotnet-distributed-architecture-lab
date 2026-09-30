# .NET backend architecture overview

This optional profile describes DDD, Clean Architecture, CQRS and ports/adapters.
Read the target's adopted decisions before applying it. Supported technologies and
versions are described by the [technology profile](../requirements/TECH-STACK-REQUIREMENTS.MD);
[project structure](../standards/project-structure.md) is a conditional layout.
Installation does not adopt either document or describe the target's actual system.

## Responsibilities

- Domain: aggregates, entities, value objects and domain invariants.
- Application: command/query/reactor behavior and application-facing ports.
- Infrastructure: selected persistence, messaging and integration adapters.
- Inbound adapters: API/message delivery, mapping and invocation of a use case.

The [use-case/handler relationship](../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD)
keeps a dispatch adapter separate from the behavior it invokes. Naming and physical
layout remain subject to accepted target boundaries; do not create a handler for a
use case that has no dispatch entry.

## Persistence and integration

An aggregate persistence port owns aggregate-root storage; child entities do not
acquire independent application-injected repositories. Read-model ports stay
read-only. Purge, outbox, projection and import writers have explicit capabilities.
Confirm transaction, concurrency and delivery semantics for each bounded context.

EF Core, Dapper/direct SQL, event stores and in-memory adapters are alternatives
selected per domain. Event Sourcing, outbox and batch persistence apply only where
the target accepts their contracts. Preserve existing mixed persistence choices.
An application use case depends on project-owned outbound ports; broker-specific
handlers and registration stay at the actual adapter/composition boundary.

## Evidence before configuration

Read target project files, dependencies, deployment configuration and accepted
architecture decisions. Summaries may refer to that evidence but cannot override
it or fill unknown technology choices with defaults. This package does not invoke
an initialization skill, generate project-config, or require a fixed `.dev` path.
