# Legacy AI Coding Guide for .NET CA + WolverineFx

> **Status: legacy profile example — not active repository or target-project truth.**
>
> This document preserves an earlier Todo/.NET backend profile for historical
> reference. Do not infer that a target repository uses WolverineFx, EF Core,
> Event Sourcing, PostgreSQL, BDDfy, or the topology below. Establish target
> facts with `repo-structure-sync`, then follow the generated repository context
> and the applicable `.ai/assets/tech-stacks/dotnet-backend/` references.
> Architecture and package choices require target-repository evidence or an
> explicit decision.

## Quick Start

### 1. Essential Reading Order
1. `coding-standards.md` - Coding standards (read first)
2. This file - Overview and quick reference
3. `../guides/implementation-guides/TEMPLATE-USAGE-GUIDE.md` - Template selection and usage decision guide
4. Root `AGENTS.md` and `README.md` - repository rules and identity
5. `project-structure.md` - conditional .NET backend target structure profile; physical names and paths require target adoption
6. Relevant aggregate spec in `.dev/specs/[aggregate]/`

### 2. Preserved Example Profile
- **Purpose**: Historical Todo List example; not this repository's product identity
- **Tech Stack**: .NET, ASP.NET Core, WolverineFx, EF Core, CQRS, Event Sourcing
- **Tests**: xUnit + BDDfy (Gherkin-style naming), NSubstitute default (no BaseTestClass)

### 3. Key Principles
- ✅ DO: Follow existing patterns, use explicit loading, write tests first
- ❌ DON'T: Generate ezDDD/ezSpec classes, skip validation, bypass UseCase layers

## Architecture Layers (Clean Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (ASP.NET Core)             │
├─────────────────────────────────────────────────────────┤
│                  Adapter Layer (In/Out)                 │
├─────────────────────────────────────────────────────────┤
│                 Use Case Layer (Handlers)               │
├─────────────────────────────────────────────────────────┤
│                Entity Layer (Domain Model)              │
└─────────────────────────────────────────────────────────┘
```

## Preserved Profile Constraints (Conditional)

The following constraints apply only when the target repository has explicitly
adopted this legacy profile. They are not universal framework requirements.

- DDD / CA / CQRS must be preserved.
- Event sourcing state changes must go through Apply/When.
- Repository limited to findById / save / delete.
- Use WolverineFx for CQRS/MQ/Event Sourcing.
- EF Core is the primary ORM.
- xUnit + BDDfy for BDD (Gherkin-style naming), with NSubstitute as the default mocking selection.
- No BaseTestClass usage.

## Common Pitfalls

- Controller talking directly to Repository
- UseCase contains business logic
- Direct DateTime.UtcNow in Domain Events
- Querying Aggregate for read model (use Projection)
