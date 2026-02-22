using System;
using System.Collections.Generic;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

// TODO: Replace these placeholders with the .NET ports of ezDDD/ezSpec/uContract.
public interface IInput { }

public interface ICommand<in TInput, out TOutput> where TInput : IInput { }

public interface IQuery<in TInput, out TOutput> where TInput : IInput { }

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

public interface IRepository<TAggregate, in TId>
{
    TAggregate? FindById(TId id);
    void Save(TAggregate aggregate);
}

public interface IPlanProjection
{
    PlanDto? FindById(string planId);
}

public sealed class PlanDtosProjectionInput
{
    public string? UserId { get; set; }
    public string? SortBy { get; set; }
    public string? SortOrder { get; set; }
}

public interface IPlanDtosProjection
{
    IReadOnlyList<PlanDto> Query(PlanDtosProjectionInput input);
}

public interface ITasksByDateProjection
{
    IReadOnlyList<TaskDto> FindTasksByDate(string userId, DateOnly targetDate);
}
