using System.ComponentModel.DataAnnotations;

namespace Example.Plans.Api.Controllers;

public sealed record CreateTaskRequest(
    [Required, MinLength(1)] string TaskName);
