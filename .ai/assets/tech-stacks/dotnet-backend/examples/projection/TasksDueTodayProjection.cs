using System.Collections.Generic;

namespace Example.Plans.ReadModel;

public interface ITasksDueTodayProjection
{
    IReadOnlyList<TaskDueTodayDto> Query(TasksDueTodayProjectionInput input);
}

public sealed class TasksDueTodayProjectionInput
{
    public string UserId { get; }

    public TasksDueTodayProjectionInput(string userId)
    {
        UserId = userId;
    }
}
