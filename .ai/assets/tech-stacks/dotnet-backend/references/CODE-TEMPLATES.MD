# Code Templates (.NET)

This document contains C# templates and patterns commonly used in the .NET stack.

## Command Use Case Template

```csharp
public sealed record CreateTaskInput(string PlanId, string ProjectName, string TaskName);

public interface ICreateTaskUseCase
{
    Task<CreateTaskOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken);
}

public sealed record CreateTaskOutput(string PlanId);

public sealed class CreateTaskUseCase : ICreateTaskUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _repository;

    public CreateTaskUseCase(IAggregateRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull(nameof(repository), repository);
        _repository = repository;
    }

    public async Task<CreateTaskOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken)
    {
        Contract.RequireNotNull(nameof(input), input);
        Contract.RequireNotNull(nameof(input.PlanId), input.PlanId);

        var plan = await _repository.FindByIdAsync(
            PlanId.ValueOf(input.PlanId),
            cancellationToken);
        if (plan == null)
        {
            throw new UseCaseFailureException("Plan not found");
        }

        plan.CreateTask(
            ProjectName.ValueOf(input.ProjectName),
            TaskName.ValueOf(input.TaskName));

        await _repository.SaveAsync(plan, cancellationToken);
        return new CreateTaskOutput(plan.Id.Value);
    }
}
```

## Query Use Case Template (Projection)

```csharp
public sealed record GetRecordInput(string RecordId);
public sealed record GetRecordOutput(RecordDto Record, ExitCode ExitCode, string? Message);

public interface IGetRecordUseCase
{
    Task<GetRecordOutput> ExecuteAsync(
        GetRecordInput input,
        CancellationToken cancellationToken);
}

public sealed class GetRecordUseCase : IGetRecordUseCase
{
    private readonly IRecordProjection _projection;

    public GetRecordUseCase(IRecordProjection projection)
    {
        Contract.RequireNotNull(nameof(projection), projection);
        _projection = projection;
    }

    public async Task<GetRecordOutput> ExecuteAsync(
        GetRecordInput input,
        CancellationToken cancellationToken)
    {
        Contract.RequireNotNull(nameof(input), input);

        var dto = await _projection.FindByIdAsync(
            input.RecordId,
            cancellationToken);
        if (dto == null)
        {
            return new GetRecordOutput(default!, ExitCode.FAILURE, "Record not found");
        }

        return new GetRecordOutput(dto, ExitCode.SUCCESS, null);
    }
}
```

## Optional Dispatch Handler Template

Create this adapter only when an actual Wolverine/message dispatch entry exists:

```csharp
public sealed record CreateTaskCommand(
    string PlanId,
    string ProjectName,
    string TaskName);

public sealed class CreateTaskCommandHandler
{
    public static Task<CreateTaskOutput> HandleAsync(
        CreateTaskCommand command,
        ICreateTaskUseCase useCase,
        CancellationToken cancellationToken)
    {
        var input = new CreateTaskInput(
            command.PlanId,
            command.ProjectName,
            command.TaskName);

        return useCase.ExecuteAsync(input, cancellationToken);
    }
}
```

## Validation Pattern

### Aggregate Root Validation
```csharp
Contract.RequireNotNull(nameof(recordId), recordId);
Contract.Require(name.Length <= 100, "name exceeds maximum length");
```

### Entity & Value Object Validation
```csharp
Objects.RequireNotNull(pbiId, "pbiId cannot be null");
Objects.RequireNotNull(name, "name cannot be null");
```

### Constructor Validation
```csharp
public CreateRecordUseCase(IAggregateRepository<Record, RecordId> repository)
{
    Contract.RequireNotNull(nameof(repository), repository);
    _repository = repository;
}
```

## Aggregate Constructor Template

```csharp
public sealed class Record : AggregateRoot<RecordId>
{
    public Record(RecordId recordId, RecordName name)
    {
        Contract.RequireNotNull(nameof(recordId), recordId);
        Contract.RequireNotNull(nameof(name), name);
        Apply(new RecordCreated(recordId, name, metadata: new Dictionary<string, string>(), DateProvider.Now()));
    }
}

// ❌ WRONG: Static factory hides event sourcing rules
// public static Record Create(...) { ... }
```

## Domain Event Template

```csharp
public sealed record RecordCreated(
    RecordId RecordId,
    RecordName Name,
    IReadOnlyDictionary<string, string> Metadata,
    Guid Id,
    DateTimeOffset OccurredOn
)
{
    public RecordCreated
    {
        Contract.RequireNotNull(nameof(RecordId), RecordId);
        Contract.RequireNotNull(nameof(Name), Name);
        Contract.RequireNotNull(nameof(Metadata), Metadata); // Required
        Contract.RequireNotNull(nameof(Id), Id);
        Contract.RequireNotNull(nameof(OccurredOn), OccurredOn);
    }
}
```

## Use Case Interface Pattern (Required)

```csharp
public interface ICreateRecordUseCase
{
    Task<CreateRecordOutput> ExecuteAsync(
        CreateRecordInput input,
        CancellationToken cancellationToken);
}
```

## Repository Usage Template

```csharp
public sealed class CreateRecordUseCase : ICreateRecordUseCase
{
    private readonly IAggregateRepository<Record, RecordId> _repository;

    public CreateRecordUseCase(IAggregateRepository<Record, RecordId> repository)
    {
        _repository = repository;
    }
}

// Compatibility is allowed only for existing products and must preserve the same contract:
// public interface IDomainRepository<TAggregate, TId>
//     : IAggregateRepository<TAggregate, TId> { }
```

## Query Repository Template (EF Core adapter example)

```csharp
public interface IRecordQueryRepository : IQueryRepository
{
    Task<RecordDto?> FindByIdAsync(string recordId);
    Task<IReadOnlyList<RecordDto>> FindAllAsync();
}

public sealed class EfRecordQueryRepository : IRecordQueryRepository
{
    private readonly AppDbContext _db;

    public EfRecordQueryRepository(AppDbContext db)
    {
        _db = db;
    }

    public async Task<RecordDto?> FindByIdAsync(string recordId)
    {
        return await _db.Records
            .Where(p => p.RecordId == recordId)
            .Select(RecordMapper.ToDto)
            .FirstOrDefaultAsync();
    }
}
```

## Mapper Template

```csharp
public static class RecordMapper
{
    public static RecordDto ToDto(Record record)
        => new(record.Id.Value, record.Name.Value);
}
```
