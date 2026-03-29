# AI Coding Guide for .NET CA + WolverineFx

> This guide is for AI assistants working on the .NET version of this codebase.

## Quick Start

### 1. Essential Reading Order
1. `coding-standards.md` - 編碼規範（優先閱讀）
2. This file - Overview and quick reference
3. `../guides/implementation-guides/TEMPLATE-USAGE-GUIDE.md` - 範本選擇與使用決策指南
4. `CLAUDE.md` - Project-specific rules and conventions
5. `project-structure.md` - .NET 專案結構
6. Relevant aggregate spec in `.dev/specs/[aggregate]/`

### 2. Project Overview
- **Purpose**: Todo List application with DDD architecture
- **Tech Stack**: .NET, ASP.NET Core, WolverineFx, EF Core, CQRS, Event Sourcing
- **Tests**: xUnit + BDDfy (Gherkin-style naming), NSubstitute (no BaseTestClass)

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

## Non-Negotiables

- DDD / CA / CQRS must be preserved.
- Event sourcing state changes must go through Apply/When.
- Repository limited to findById / save / delete.
- Use WolverineFx for CQRS/MQ/Event Sourcing.
- EF Core is the primary ORM.
- xUnit + BDDfy for BDD (Gherkin-style naming), NSubstitute for mocks.
- No BaseTestClass usage.

## Common Pitfalls

- Controller talking directly to Repository
- UseCase contains business logic
- Direct DateTime.UtcNow in Domain Events
- Querying Aggregate for read model (use Projection)
