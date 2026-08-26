using System;
using System.Collections.Generic;

namespace Example.Plans.ReadModel;

public interface ITasksByDateProjection
{
    IReadOnlyList<TaskDueTodayDto> Query(TasksByDateProjectionInput input);
}

public sealed class TasksByDateProjectionInput
{
    public string UserId { get; }
    public DateOnly TargetDate { get; }

    public TasksByDateProjectionInput(string userId, DateOnly targetDate)
    {
        UserId = userId;
        TargetDate = targetDate;
    }
}
