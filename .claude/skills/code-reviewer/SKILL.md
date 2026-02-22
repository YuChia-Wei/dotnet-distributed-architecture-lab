---
name: dotnet/code-reviewer
description: |
  Review .NET code for DDD, Clean Architecture, CQRS, and Event Sourcing compliance.
  Use when: user asks to "code review", "review code", "check this file",
  mentions reviewing a specific C# file, or asks about code quality.
allowed-tools: Read, Glob, Grep, Bash
---

# Code Reviewer Skill (.NET)

## Overview
This skill performs systematic code reviews for .NET DDD + Clean Architecture + CQRS projects,
following the project's .NET checklist and review index.

## Trigger Conditions
Activate when user mentions:
- "code review" / "review code"
- "check this file" / "review [filename]"
- Specific file patterns like "review Sprint.cs"

## Mandatory Execution Flow
**Do not skip any step. Violations invalidate the review.**

### Step 1: Read Index (MANDATORY)
```
READ: .ai/CODE-REVIEW-INDEX.MD
```

### Step 2: Identify File Type
Match file patterns to checklist sections:

| File Pattern | Category | Checklist Section |
| --- | --- | --- |
| `src/Domain/**/Aggregates/*.cs` | Aggregate Root | Event Sourcing Compliance |
| `src/Domain/**/Events/*.cs` | Domain Event | Domain Event Design |
| `src/Domain/**/Entities/*.cs` | Entity | Entity Design |
| `src/Domain/**/ValueObjects/*.cs` | Value Object | Value Object Design |
| `src/Application/**/UseCases/Commands/*.cs` | Use Case (Command) | Use Case Handler |
| `src/Application/**/UseCases/Queries/*.cs` | Use Case (Query) | Query/Projection |
| `src/Api/Controllers/*.cs` | Controller | Adapter Layer |
| `src/Application/**/Ports/**/*Mapper.cs` | Mapper | Mapper Rules |
| `src/Infrastructure/**/Outbox/*Data.cs` | Outbox Data | Outbox Data Rules |
| `tests/**/*.cs` | Test | xUnit + BDDfy Rules |

### Step 3: Read Checklist (MANDATORY)
```
READ: .dev/standards/CODE-REVIEW-CHECKLIST.md
```

### Step 4: Read Target File
```
READ: [target file path]
```

### Step 5: Execute Tests (If Applicable)
```
dotnet test --filter FullyQualifiedName~[TestClassName]
```
If tests fail, the review **cannot proceed**.

### Step 6: Build Checklist Comparison Table
```markdown
| Check Item | Result | Location | Issue Description |
|------------|--------|----------|-------------------|
| State assigned only in When()? | FAIL | line 42-55 | Direct assignment in constructor |
```

### Step 7: Categorize Issues
- **CRITICAL**: Event Sourcing violations, missing Apply/When pattern, broken domain events
- **MUST FIX**: Wrong DI usage, missing pre/post conditions, broken mapping
- **SHOULD FIX**: Naming, minor organization, missing null guards

### Step 8: Generate Review Report
```markdown
## Code Review Report: [FileName]

### Test Status: [PASSING/FAILING]

### Compliance Check: [COMPLIANT/NON-COMPLIANT]

### Issues Found
#### CRITICAL Issues
1. ...

#### MUST FIX Issues
1. ...

#### SHOULD FIX Issues
1. ...

### Summary
- Critical Issues: X
- Must Fix Issues: Y
- Should Fix Issues: Z
```

---

## Aggregate Complete Review Mode
If the target is an Aggregate Root, also review related files in the same aggregate:

```
src/Domain/<Aggregate>/
├── Aggregates/<Aggregate>.cs
├── Events/<Aggregate>Events.cs
├── Entities/*.cs
└── ValueObjects/*.cs
```

**Priority**:
- Aggregate Root / Events → CRITICAL
- Entities → HIGH
- Value Objects → MEDIUM

---

## Key .NET Review Rules (Summary)

### Aggregate Root (CRITICAL)
- State **only** set in `When(...)`
- Constructor uses `Apply(event)` (no direct state assignment)
- Domain events are immutable and include metadata

### DI Rules
- No attribute-based component scanning
- Use `IServiceCollection` for registration
- Use case services are plain classes (POCO)

### Tests
- xUnit + BDDfy (Gherkin-style naming only)
- No BaseTestClass
- NSubstitute for mocks

### Repository Rules
- Write side must align with `IDomainRepository<TEntity, TId>`
- Domain-specific wrapper interface is optional, but must not add extra methods
- Queries must go through Query Service / Query Repository (not Domain Repository)

---

## Reference Files
- `.ai/CODE-REVIEW-INDEX.MD`
- `.dev/standards/CODE-REVIEW-CHECKLIST.md`
- `.dev/standards/project-structure.md`
- `CHECKLIST-REFERENCE.MD` (same directory - detailed checklist with C# examples)
