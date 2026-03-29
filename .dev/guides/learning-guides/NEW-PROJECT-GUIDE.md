# AiScrum Project Structure and New Project Setup Guide (Dotnet)

This guide explains how to create a new dotnet project based on the AiScrum structure.

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

### Environment requirements
- .NET SDK (version defined in `.dev/project-config.yaml`)
- Git
- PostgreSQL (test port 5800, production port 5500)
- Your IDE (Rider, Visual Studio, VS Code)

### Knowledge prerequisites
- Domain-Driven Design (DDD)
- Clean Architecture (CA)
- CQRS fundamentals

## Step 1: Create the project skeleton

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
mkdir -p .dev/tasks/{feature,test,refactoring,frontend,main}
mkdir -p .dev/specs/{use-cases,aggregates,domain-events}
```

## Step 2: Set up AI project memory

- Keep `AGENTS.md` (or your chosen memory file) updated with project-specific context.
- Use `.dev/guides/LEARNING-PATH.md` as the onboarding reference for new agents.

## Step 3: Configure project metadata

Create `.dev/project-config.yaml` as the single source of truth:

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
1. Create use case spec in `.dev/specs/use-cases/...`
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
1. Read `.dev/guides/LEARNING-PATH.md`.
2. Use `.ai/CODE-TEMPLATES.md` for scaffolding.
3. Keep `.dev/adr/` updated with key decisions.



