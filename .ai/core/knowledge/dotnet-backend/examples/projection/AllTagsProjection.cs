using System.Collections.Generic;

namespace Example.Tags.ReadModel;

public interface IAllTagsProjection
{
    IReadOnlyList<TagDto> Query(AllTagsProjectionInput input);
}

public sealed class AllTagsProjectionInput
{
    public string PlanId { get; }

    public AllTagsProjectionInput(string planId)
    {
        PlanId = planId;
    }
}
