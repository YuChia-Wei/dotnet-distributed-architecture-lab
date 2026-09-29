using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

// Framework-neutral placeholders; replace them with target-owned contracts.
public interface IInput { }

public enum ExitCode
{
    Success,
    Failure
}

public class CqrsOutput
{
    public string? Id { get; private set; }
    public ExitCode ExitCode { get; private set; }
    public string? Message { get; private set; }

    public static CqrsOutput Create() => new();

    public CqrsOutput SetId(string? id)
    {
        Id = id;
        return this;
    }

    public CqrsOutput SetExitCode(ExitCode exitCode)
    {
        ExitCode = exitCode;
        return this;
    }

    public CqrsOutput SetMessage(string? message)
    {
        Message = message;
        return this;
    }
}

public sealed class UseCaseFailureException : Exception
{
    public UseCaseFailureException(Exception inner) : base("Use case failed.", inner)
    {
    }
}

public interface IAggregateRepository<TAggregate, in TId>
{
    Task<TAggregate?> FindByIdAsync(TId id, CancellationToken cancellationToken = default);
    Task SaveAsync(TAggregate aggregate, CancellationToken cancellationToken = default);
}

public interface IQueryRepository { }

public interface IPlanProjection : IQueryRepository
{
    PlanDto? FindById(string planId);
}

public sealed class PlanDtosProjectionInput
{
    public string? UserId { get; set; }
    public string? SortBy { get; set; }
    public string? SortOrder { get; set; }
}

public interface IPlanDtosProjection : IQueryRepository
{
    IReadOnlyList<PlanDto> Query(PlanDtosProjectionInput input);
}

public interface ITasksByDateProjection : IQueryRepository
{
    IReadOnlyList<TaskDto> FindTasksByDate(string userId, DateOnly targetDate);
}
