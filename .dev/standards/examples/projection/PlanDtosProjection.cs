using System.Collections.Generic;
using Example.Plans.UseCases.Port;

namespace Example.Plans.ReadModel;

public interface IPlanDtosProjection
{
    IReadOnlyList<PlanDto> Query(PlanDtosProjectionInput input);
}

public enum PlanSortBy
{
    Name,
    LastModified
}

public enum PlanSortOrder
{
    Asc,
    Desc
}

public sealed class PlanDtosProjectionInput
{
    public string UserId { get; set; } = string.Empty;
    public PlanSortBy SortBy { get; set; } = PlanSortBy.Name;
    public PlanSortOrder SortOrder { get; set; } = PlanSortOrder.Asc;
}
