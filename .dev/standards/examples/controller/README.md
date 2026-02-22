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
    public IActionResult CreateTask(string planId, string projectName, CreateTaskRequest request)
    {
        var input = CreateTaskInput.Create();
        input.PlanId = PlanId.ValueOf(planId);
        input.ProjectName = ProjectName.ValueOf(projectName);
        input.TaskName = request.TaskName;

        var output = _useCase.Execute(input);
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
3. Use DTOs for request/response models.
4. Return appropriate HTTP status codes.

## Related Resources
- `../usecase/`
- `../dto/`
