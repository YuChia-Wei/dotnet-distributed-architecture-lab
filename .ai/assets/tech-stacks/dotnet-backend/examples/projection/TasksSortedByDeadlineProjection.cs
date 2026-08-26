using System.Collections.Generic;

namespace Example.Plans.ReadModel;

public interface ITasksSortedByDeadlineProjection
{
    IReadOnlyList<TaskDueTodayDto> Query(TasksSortedByDeadlineProjectionInput input);
}

public sealed class TasksSortedByDeadlineProjectionInput
{
    public string UserId { get; }
    public string SortOrder { get; }

    public TasksSortedByDeadlineProjectionInput(string userId, string sortOrder)
    {
        UserId = userId;
        SortOrder = sortOrder;
    }
}
