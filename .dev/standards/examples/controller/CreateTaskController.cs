using Example.Plans.Domain;
using Example.Plans.UseCases;
using Microsoft.AspNetCore.Mvc;

namespace Example.Plans.Api.Controllers;

[ApiController]
[Route("api/v1")]
public sealed class CreateTaskController : ControllerBase
{
    private readonly ICreateTaskUseCase _createTaskUseCase;

    public CreateTaskController(ICreateTaskUseCase createTaskUseCase)
    {
        _createTaskUseCase = createTaskUseCase;
    }

    [HttpPost("plans/{planId}/projects/{projectName}/tasks")]
    public IActionResult CreateTask(
        [FromRoute] string planId,
        [FromRoute] string projectName,
        [FromBody] CreateTaskRequest request)
    {
        var input = CreateTaskInput.Create();
        input.PlanId = PlanId.ValueOf(planId);
        input.ProjectName = ProjectName.ValueOf(projectName);
        input.TaskName = request.TaskName;

        var output = _createTaskUseCase.Execute(input);

        if (output.ExitCode == ExitCode.Success)
        {
            var response = new CreateTaskResponse
            {
                TaskId = output.Id,
                Message = "Task created successfully",
                Success = true
            };
            return StatusCode(201, response);
        }

        var error = new CreateTaskResponse
        {
            Message = output.Message,
            Success = false
        };

        if (!string.IsNullOrWhiteSpace(output.Message) &&
            output.Message.Contains("not found", StringComparison.OrdinalIgnoreCase))
        {
            return NotFound(error);
        }

        return BadRequest(error);
    }

    public sealed class CreateTaskRequest
    {
        public string TaskName { get; set; } = string.Empty;
    }

    public sealed class CreateTaskResponse
    {
        public string? TaskId { get; set; }
        public string? Message { get; set; }
        public bool Success { get; set; }
    }
}
