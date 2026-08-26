namespace Example.Plans.Api.Controllers;

public sealed record CreateTaskResponse
{
    public string? TaskId { get; init; }

    public string? Message { get; init; }

    public bool Success { get; init; }
}
