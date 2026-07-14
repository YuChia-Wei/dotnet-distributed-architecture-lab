# Legacy ExampleApp Project Setup Guide (Dotnet)

> **Status: retired onboarding example — do not execute as the current setup path.**
>
> The commands and topology below preserve an earlier ExampleApp profile. For a
> real target repository, copy the framework context and run `repo-structure-sync`
> first. That skill inventories file-backed facts and refreshes the target-specific
> `AGENTS.md`, `.dev/`, and necessary `.ai/` entries. Do not create the legacy
> directory tree or install the listed packages unless the target repository has
> explicitly selected this profile.

This guide documents the retired ExampleApp setup for historical comparison.

## Table of Contents
1. Prerequisites
2. Step 1: Create the project skeleton
3. Step 2: Set up AI project memory
4. Step 3: Configure project metadata
5. Step 4: Initialize the .NET solution
6. Step 5: Create the first feature
7. Step 6: Work with AI workflows
8. FAQ

## Prerequisites

All database, framework, test-library, and package requirements in this document
are conditional on adopting the preserved ExampleApp profile; they are not
defaults for a new target repository.

### Environment requirements
- .NET SDK (version confirmed from `global.json`, project files, or generated `.dev/project-config.yaml`)
- Git
- PostgreSQL (test port 5800, production port 5500)
- Your IDE (Rider, Visual Studio, VS Code)

### Knowledge prerequisites
- Domain-Driven Design (DDD)
- Clean Architecture (CA)
- CQRS fundamentals

## Step 1: Create the project skeleton

> Legacy example only. Current onboarding must use `repo-structure-sync` to
> discover and adapt the target repository instead of recreating this topology.

```bash
# 1) Create project root
mkdir my-scrum-project
cd my-scrum-project

# 2) Initialize git
git init

# 3) Create solution structure
mkdir -p src/Api src/Application src/Domain src/Infrastructure src/tests

# 4) Create .ai and .dev folders
mkdir -p .ai/{config,guides,prompts,scripts,tech-stacks,workflows}
mkdir -p .dev/{adr,specs,tasks}
mkdir -p .dev/tasks/{feature,test,refactoring,main}
mkdir -p .dev/specs/{use-cases,aggregates,domain-events}
```

## Step 2: Set up AI project memory

- Keep `AGENTS.md` (or your chosen memory file) updated with project-specific context.
- Use `.dev/guides/learning-guides/LEARNING-PATH.md` as the onboarding reference for new agents.

## Step 3: Configure project metadata

Run `repo-structure-sync` to generate `.dev/project-config.yaml` from repository evidence:

The YAML below is illustrative. Package versions and feature flags must come
from target-repository evidence or explicit maintainer decisions.

```yaml
projectName: MyScrum
rootNamespace: MyScrum
version: 0.1.0
dotnetSdkVersion: 8.0.x
dependencies:
  wolverineVersion: <set>
  efCoreVersion: <set>
  npgsqlVersion: <set>
  xunitVersion: <set>
  nsubstituteVersion: <set>
  bddfyVersion: <set>
  bddStyle: Gherkin-style-naming
database:
  production: PostgreSQL
  test: PostgreSQL
features:
  eventSourcing: true
  cqrs: true
  restApi: true
```

## Step 4: Initialize the .NET solution

### 4.1 Create solution and projects
```bash
dotnet new sln -n MyScrum

dotnet new webapi -n Api -o src/Api

dotnet new classlib -n Application -o src/Application

dotnet new classlib -n Domain -o src/Domain

dotnet new classlib -n Infrastructure -o src/Infrastructure

dotnet new xunit -n Tests -o src/tests

# Add projects to solution
dotnet sln add src/Api/Api.csproj
dotnet sln add src/Application/Application.csproj
dotnet sln add src/Domain/Domain.csproj
dotnet sln add src/Infrastructure/Infrastructure.csproj
dotnet sln add src/tests/Tests.csproj
```

### 4.2 Add required packages

These packages are required only for the preserved WolverineFx/EF Core/
PostgreSQL/xUnit/BDDfy example profile. They are not framework-wide defaults.

In `src/Api` and `src/Infrastructure`:
```bash
dotnet add src/Api package WolverineFx
dotnet add src/Api package WolverineFx.Http
dotnet add src/Infrastructure package Microsoft.EntityFrameworkCore
dotnet add src/Infrastructure package Npgsql.EntityFrameworkCore.PostgreSQL
```

In `src/tests`:
```bash
dotnet add src/tests package xunit
dotnet add src/tests package xunit.runner.visualstudio
dotnet add src/tests package NSubstitute
dotnet add src/tests package TestStack.BDDfy
 # TODO: add optional BDDfy reporter/integration packages if needed
```

### 4.3 Wire project references
```bash
dotnet add src/Application/Application.csproj reference src/Domain/Domain.csproj
dotnet add src/Infrastructure/Infrastructure.csproj reference src/Domain/Domain.csproj
dotnet add src/Api/Api.csproj reference src/Application/Application.csproj
dotnet add src/Api/Api.csproj reference src/Infrastructure/Infrastructure.csproj
dotnet add src/tests/Tests.csproj reference src/Application/Application.csproj
dotnet add src/tests/Tests.csproj reference src/Infrastructure/Infrastructure.csproj
```

### 4.4 Verify build
```bash
dotnet build
dotnet test
```

## Step 5: Create the first feature

### Option 1: Use spec documents (recommended)
1. Create a use case spec in the target repository spec area defined by repo-structure-sync
2. Implement with TDD using canonical sub-agent assets:
   - `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
   - `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
   - `.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/sub-agent.yaml`

### Option 2: Describe requirements directly
Provide the operation, inputs, outputs, business rules, and required events.

## Step 6: Work with AI workflows

Common workflows:
- command-sub-agent
- query-sub-agent
- reactor-sub-agent
- aggregate-sub-agent
- controller-sub-agent
- outbox-sub-agent
- mutation-testing-sub-agent

Canonical delegated sub-agent definitions are under `.ai/assets/sub-agent-role-prompts/`.
Shared explanatory materials, examples, and reusable rule fragments are under `.ai/assets/shared/`.

## FAQ

### Q1: Missing ezDDD/ezSpec packages in .NET
There are no direct .NET packages yet. Preserve the concepts and use TODOs where tooling is not available.

### Q2: How to register domain events
Use Wolverine message registration and ensure events are serializable. TODO: define a shared event registration pattern.

### Q3: Tests failing because of profile mismatch
Ensure `ASPNETCORE_ENVIRONMENT` matches `test-inmemory` or `test-outbox` and that the matching appsettings file is present.

## Next Steps
1. Read `.dev/guides/learning-guides/LEARNING-PATH.md`.
2. Use `.ai/assets/tech-stacks/dotnet-backend/references/CODE-TEMPLATES.MD` for scaffolding.
3. Keep `.dev/standards/`, `.dev/guides/`, and `.dev/ARCHITECTURE.md` updated as the primary rule set.
