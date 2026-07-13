# Common Pitfalls and Solutions (.NET)

This document records common errors and solutions when implementing with the Sub-agent Workflow for .NET.

## 🔴 DI / Configuration Issues (Frequent)

### 1. Duplicate EF Core Registration
**Error**: `InvalidOperationException: The service collection already contains ... DbContext`

**Cause**: `AddDbContext` is called in multiple places, or profiles are not isolated.

**Solution**:
1. Register it once in profile-specific configuration.
2. Use `ASPNETCORE_ENVIRONMENT` to select InMemory or Outbox.
3. Follow the target repository's actual profile configuration; generated `.dev/project-config.yaml` is only a supporting summary.

**Prevention**:
```bash
rg -n "AddDbContext" src
```

### 2. Inconsistent Use Case Input Field Names
**Error**: Controller and Handler read different field names, producing null values.

**Solution**: Map fields explicitly when converting DTO → Input.
```csharp
// Wrong
input.ProductId = request.Id;

// Correct
input.Id = request.ProductId;
```

## 🔴 Outbox / Event Sourcing Issues

### 3. Wolverine Outbox Is Not Enabled
**Error**: Events are not persisted or do not appear in the message store.

**Solution**:
```csharp
services.AddWolverine(opts =>
{
    opts.PersistMessagesWithPostgresql(conn);
    opts.UseDurableOutbox();
});
```

### 4. OutboxMapper Does Not Reconstruct Without Events
**Error**: The Aggregate has no state when loaded from the database.

**Solution**:
- With events → reconstruct from events.
- Without events → reconstruct from stored state and restore events.

### 5. Mixed InMemory / Outbox Registration
**Error**: The same profile registers both InMemory and Outbox repositories.

**Solution**: Keep profiles isolated (InMemory / Outbox) and register only the matching implementation.

## 🔴 Domain Model / Mapping Issues

### 6. Value Object Lacks a ValueOf/From Method
**Error**: Mapper or UseCase cannot create the VO consistently.

**Solution**: Provide an explicit factory such as `ValueOf(string)` or `From(string)` and retain validation.

### 7. Projection Returns an EF Entity Directly
**Error**: Projection returns an EF Core entity instead of a DTO.

**Solution**: Project through a Mapper into a DTO to avoid exposing the data layer.

### 8. Projection Mixes in DbContext Logic
**Error**: Projection directly inherits DbContext or uses a Repository interface to override the EF Core API.

**Solution**: Encapsulate query logic in an Adapter / Service; Projection exposes query methods only.

## 🔴 Controller Issues

### 9. Missing Null Guard
**Error**: The Controller/Handler constructor does not check for null.

**Solution**:
```csharp
public CreateProductController(ICreateProductUseCase useCase)
{
    ArgumentNullException.ThrowIfNull(useCase);
    _useCase = useCase;
}
```

### 10. Checking ExitCode for an Asynchronous Command
**Error**: ExitCode is checked even though the Command has already been scheduled.

**Solution**: Return `202 Accepted` or a result object directly without waiting synchronously.

## 🔴 Testing Issues

### 11. Default BDDfy Profile Does Not Call BDDfy()
**Error**: In a project using BDDfy, test execution does not trigger Given/When/Then. If the team explicitly disables BDDfy, plain xUnit must still retain clear GWT structure and naming; 3A must not be used instead.

**Solution**:
```csharp
[Fact]
public void Rule_Success_case()
{
    this.BDDfy();
}
```

### 12. Using BaseTestClass
**Error**: The test inherits BaseTestClass/BaseUseCaseTest.

**Solution**: Use an xUnit fixture plus DI composition.

### 13. Profile Is Hard-Coded in Tests
**Error**: `ASPNETCORE_ENVIRONMENT` is set in test code.

**Solution**: Let the test runner / fixture control the environment.

## Prevention

1. Use the Sub-agent Workflow.
2. Refer to `.dev/standards/examples/`.
3. Run `.ai/scripts/check-all.sh` as the transitional local orchestrator.
4. Read `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD`.

Last updated: 2026-02-01
