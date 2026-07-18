# Code Review Checklist Quick Index (.NET)

## 🚨 When You Receive a Code Review Request

**Format**: `code review [FileName]`

### ⚠️ Mandatory Steps (Do Not Skip)

1. **Read this file** - You are reading it now ✓
2. **Identify the file type** - Find the matching section in the table below.
3. **Read the matching section** - Read the full content in the .NET `.dev/standards/CODE-REVIEW-CHECKLIST.md`.
4. **Perform the review** - Check every item and create a results table.
5. **Assign issue severity** - CRITICAL / MUST FIX / SHOULD FIX.

### Rule Resolution Order

1. Apply type-first detection for Aggregate rules:
   - `EsAggregateRoot<TId>` uses ES rules (`AGGREGATE-ES-001`).
   - `IAggregateRoot<TId>` (normal, non-ES) does not use `Apply/When` rules.
2. Repository rules use `IAggregateRepository<TAggregate, TId>` as the write-side baseline; `IDomainRepository<TAggregate, TId>` is only a compatibility entry point that must inherit it.
3. Query capabilities belong in a read-only query port inheriting `IQueryRepository`. An additional QueryService is needed only for composition, policy, or calculation requirements.
4. `.dev/project-config.yaml` is only a supporting signal. When it conflicts with the type, use the type and mark the mismatch MUST FIX.

### 📋 File Type Quick Reference

| File Pattern | Checklist Location | Review Focus | Priority |
|---------|------------|---------|--------|
| `src/Domain/**/Aggregates/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Aggregate (type-first detection)** | 1. Detect `EsAggregateRoot<TId>` or `IAggregateRoot<TId>` first.<br>2. Check Apply/When only for ES.<br>3. Check invariants and state transitions for non-ES. | **CRITICAL** |
| `src/Application/**/UseCases/**/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Use Case / Handler** | 1. Explicit `I*UseCase` inbound port.<br>2. `ExecuteAsync` and transport-neutral contract.<br>3. Handler does not own orchestration. | HIGH |
| `src/**/Repositories/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Repository** | 1. Write side conforms to `IAggregateRepository<TAggregate, TId>`.<br>2. Generic type is an Aggregate Root.<br>3. Query and write capabilities are separated. | HIGH |
| `src/Api/Controllers/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Controller** | 1. Controller is sufficiently thin.<br>2. DTO is in a separate file.<br>3. HTTP status is correct. | MEDIUM |
| `src/Application/**/Ports/**/*Mapper.cs`<br>`src/Infrastructure/**/Mappers/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Mapper** | 1. Mapper is static/sealed.<br>2. One Mapper per DTO.<br>3. Outbox ToDomain handles both with-events and without-events cases. | **HIGH** |
| `src/Infrastructure/**/Outbox/*Data.cs` | [Repository Standards](../../../../../.dev/standards/coding-standards/repository-standards.md)<br>+ [Mapper Standards](../../../../../.dev/standards/coding-standards/mapper-standards.md) | 1. Preserve Aggregate + Outbox atomicity.<br>2. Keep serialized data separate from Domain types.<br>3. Apply target-selected EF/SQL mapping rules. | MEDIUM |
| `src/tests/**/*.cs` | [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **BDD Rules / UseCase Tests** | 1. xUnit GWT structure and naming (BDDfy is the default profile and may be explicitly disabled by the team).<br>2. Do not use 3A or BaseTestClass.<br>3. Use the target `testing.mocking` selection; default to NSubstitute. | HIGH |

---

### 🔴 Detailed Aggregate Review Steps (Example)

When receiving `code review Iteration.cs`:

#### Step 1: Read the Checklist
```
I need to code review Iteration.cs.
This is an Aggregate Root. According to DOTNET-CODE-REVIEW-INDEX.md,
I must first read the Aggregate Root review section in CODE-REVIEW-CHECKLIST.md.
```

#### Step 2: Perform CRITICAL Checks

| Check | Result | Location | Issue Description |
|---------|------|------|---------|
| Does the constructor set state fields directly? | ❌ FAIL | Lines 60-72 | Direct assignment: `this.id = sprintId` |
| Is When() triggered through Apply(event)? | ✅ PASS | Line 101 | Apply(event) is called. |
| Are state fields assigned only in When()? | ❌ FAIL | Lines 60-72 and When() | State is assigned twice. |

#### Step 3: Summarize and Score
**Critical issue count**: 2
**Score**: ⭐⭐ (2/5) - MUST FIX

---

### 🟡 Detailed Outbox Mapper Review Steps (Example)

Focus: `ToDomain()` must handle reconstruction both with and without events.

#### ✅ Correct ToDomain() Pattern
```csharp
public static Plan ToDomain(PlanData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = data.DomainEventDatas.Select(DomainEventMapper.ToDomain)
            .Cast<PlanEvents.IPlanEvent>()
            .ToList();
        var plan = new Plan(events) { Version = (int)data.Version };
        plan.ClearDomainEvents();
        return plan;
    }

    // Without events, reconstruct from stored state.
    var reconstructed = new Plan(PlanId.ValueOf(data.PlanId), data.Name, data.UserId)
    {
        Version = (int)data.Version
    };
    reconstructed.ClearDomainEvents();
    return reconstructed;
}
```

The review invariant is that every aggregate returned by `ToDomain()` has no pending domain events. A rehydration constructor SHOULD replay history through `When(...)` (or an equivalent state-transition path) without enqueueing new events. `ClearDomainEvents()` is required when reconstruction emits/enqueues events or when the constructor does not explicitly guarantee an empty pending-event collection; it is not an unconditional method-call requirement when that cleanliness guarantee is explicit.

#### ❌ Incorrect ToDomain() Pattern
```csharp
public static Plan ToDomain(PlanData data)
{
    var events = data.DomainEventDatas.Select(DomainEventMapper.ToDomain).ToList();
    return new Plan(events); // Without events, this creates an empty aggregate.
}
```

---

### 📚 Related Documents

- **Complete checklist**: [CODE-REVIEW-CHECKLIST.md](../../../../../.dev/standards/CODE-REVIEW-CHECKLIST.md)
- **Aggregate rules**: [aggregate-standards.md](../../../../../.dev/standards/coding-standards/aggregate-standards.md)
- **Mapper rules**: [mapper-standards.md](../../../../../.dev/standards/coding-standards/mapper-standards.md)
- **Outbox lifecycle**: [repository-standards.md](../../../../../.dev/standards/coding-standards/repository-standards.md)

---

### ⚠️ Consequences of Violating the Review Process

If you (the AI) perform a Code Review and:
- ❌ Do not read DOTNET-CODE-REVIEW-INDEX.md first.
- ❌ Do not read the matching CODE-REVIEW-CHECKLIST.md section.
- ❌ Do not create a checklist comparison table.
- ❌ Give evaluation and recommendations directly.

**Consequences**:
- The Code Review result is invalid and must be redone.
- Critical errors may be missed, such as Aggregate Event Sourcing violations.
- The review does not satisfy project rules.

---

## 💡 Reminder

Before every Code Review, repeat mentally:

> "I must first read DOTNET-CODE-REVIEW-INDEX.md, identify the file type, read the matching checklist section, and check every item. I must never skip this process."

## Aggregate Pattern Rules

For aggregate review, use this detection order before applying rules:

1. Type hierarchy in BuildingBlocks domain (primary):
   - `EsAggregateRoot<TId>` => apply Event Sourcing checks (`Apply/When`) as CRITICAL.
   - `IAggregateRoot<TId>` and not `EsAggregateRoot<TId>` => do NOT apply `Apply/When` checks.
2. `.dev/project-config.yaml` architecture pattern (secondary hint only).
3. If type and config disagree:
   - report `TYPE-CONFIG MISMATCH` as MUST FIX,
   - keep type hierarchy as final ruleset decision.

Report output must include:
- `Detected Aggregate Type`
- `Detected Pattern`
- `Ruleset Applied` (ES / non-ES)

## Repository Rules

Repository checks in review:

- Write side baseline: `IAggregateRepository<TAggregate, TId>` with only
  `FindByIdAsync` and `SaveAsync`.
- `IDomainRepository<TAggregate, TId>` is a compatibility interface and must inherit
  `IAggregateRepository<TAggregate, TId>`.
- Canonical, compatibility, and derived repository interfaces may target Aggregate
  Roots only.
- Query capabilities belong to a read-only port inheriting `IQueryRepository`; a
  QueryService is conditional, not mandatory.
- Public generic writable CRUD repositories and query methods on aggregate
  repositories are MUST FIX.
- Batch aggregate access is not part of the portable core. A target-specific batch
  port requires measured need and complete execution semantics; using one for a
  single ID is a review failure.
- Physical deletion must use a restricted purge capability. Soft deletion is
  aggregate behavior followed by `SaveAsync`.
- Explicit `IUnitOfWork` is allowed only for a use case that documents exceptional
  all-or-nothing consistency. It must not be introduced merely to reduce IO calls.
