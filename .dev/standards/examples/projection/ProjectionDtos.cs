using System;

namespace Example.Plans.ReadModel;

public sealed record TaskDueTodayDto(
    string TaskId,
    string Name,
    bool IsDone,
    DateOnly? Deadline,
    string PlanId,
    string PlanName,
    string ProjectName
);

public sealed record TagDto(
    string TagId,
    string Name,
    string Color
);
