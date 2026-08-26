# Controller Patterns (.NET)

Controllers live in the Adapter layer. They translate HTTP requests into Use Case inputs,
invoke the application layer, and format responses.

## Responsibilities

- Validate HTTP input
- Map request -> Use Case input
- Call Use Case
- Map output -> HTTP response

## Structure

```
controller/
├── README.md
├── CreateTaskController.cs
├── CreateTaskRequest.cs
├── CreateTaskResponse.cs
└── (TODO) GlobalExceptionHandler.cs / filters
```

## Base Pattern (ASP.NET Core)

```csharp
[ApiController]
[Route("api/v1")]
public sealed class CreateTaskController : ControllerBase
{
    private readonly ICreateTaskUseCase _useCase;

    public CreateTaskController(ICreateTaskUseCase useCase)
    {
        _useCase = useCase;
    }

    [HttpPost("plans/{planId}/projects/{projectName}/tasks")]
    public async Task<ActionResult<CreateTaskResponse>> CreateTaskAsync(
        string planId,
        string projectName,
        CreateTaskRequest request,
        CancellationToken cancellationToken)
    {
        var input = CreateTaskInput.Create();
        input.PlanId = PlanId.ValueOf(planId);
        input.ProjectName = ProjectName.ValueOf(projectName);
        input.TaskName = request.TaskName;

        var output = await _useCase.ExecuteAsync(input, cancellationToken);
        if (output.ExitCode == ExitCode.Success)
        {
            return Created("", new { taskId = output.Id });
        }

        return BadRequest(new { error = output.Message });
    }
}
```

## Global Error Handling (Recommended)

Use ASP.NET Core exception handling middleware or filters:

```csharp
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        context.Response.StatusCode = StatusCodes.Status500InternalServerError;
        await context.Response.WriteAsJsonAsync(new { code = "USE_CASE_FAILURE" });
    });
});
```

## Design Rules

1. No domain logic in controllers.
2. Controllers depend on Use Case abstractions only.
3. Invoke `ExecuteAsync` and forward the non-optional request
   `CancellationToken`.
4. Use separate `record` DTOs for request/response models.
5. Return `ActionResult<TResponse>` with appropriate HTTP status codes.

## Related Resources
- `../usecase/`
- `../dto/`
