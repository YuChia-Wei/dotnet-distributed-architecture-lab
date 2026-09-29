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
    [ProducesResponseType<CreateTaskResponse>(StatusCodes.Status201Created)]
    [ProducesResponseType<CreateTaskResponse>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<CreateTaskResponse>(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<CreateTaskResponse>> CreateTaskAsync(
        [FromRoute] string planId,
        [FromRoute] string projectName,
        [FromBody] CreateTaskRequest request,
        CancellationToken cancellationToken)
    {
        var input = CreateTaskInput.Create();
        input.PlanId = PlanId.ValueOf(planId);
        input.ProjectName = ProjectName.ValueOf(projectName);
        input.TaskName = request.TaskName;

        var output = await _createTaskUseCase.ExecuteAsync(input, cancellationToken);

        if (output.ExitCode == ExitCode.Success)
        {
            var response = new CreateTaskResponse
            {
                TaskId = output.Id,
                Message = "Task created successfully",
                Success = true
            };
            return StatusCode(StatusCodes.Status201Created, response);
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
}
