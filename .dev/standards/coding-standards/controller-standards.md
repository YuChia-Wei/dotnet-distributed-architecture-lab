# Controller Coding Standards (.NET)

This document defines coding standards for the ASP.NET Core Controller layer, including Controller structure, Request/Response DTOs, and error handling.

---

## 📌 Overview

Controllers are responsible only for the transport layer and input validation; they must not contain business logic.

- **Execution delegation**: By default, a Controller delegates only to an explicit Use Case interface.
- **Request validation**: Use ASP.NET Core Model Validation.
- **Error responses**: Use the unified `ProblemDetails` format.

---

## 🏷️ Pattern Markers (for Automated Checks)

The following markers are used by automated code review scripts:

```yaml
# Controller rules
Pattern (required): \[ApiController\]
Pattern (required): async Task<IActionResult>|async Task<IResult>

# Forbidden rules
Pattern (forbidden, ignore-comment): DbContext
Pattern (forbidden): SaveChanges
Pattern (forbidden): new .*Handler
Pattern (forbidden): new .*UseCase
Pattern (forbidden, i, ignore-comment): IMessageBus|IMediator|IDispatcher
```

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. REST API Path Design Principles

**Use nested creation endpoints and flat resource addresses.**

When handling relationships between Aggregate Roots, follow these design principles:

#### Core Rules
1. **Create**: Use a nested path to express ownership.
   - Example: `POST /api/v1/resources/{resourceId}/work-items`
   - Semantics: Add an item to the Work Item collection of a specific Resource.

2. **Resource address (Canonical URL)**: Use a flat path to preserve independence.
   - Example: `GET/PATCH/DELETE /api/v1/work-items/{workItemId}`
   - Semantics: A Work Item, as an Aggregate Root, has an independent resource address.

#### Complete Routing Example

```csharp
// WorkItems routes
[HttpPost("/api/v1/resources/{resourceId}/work-items")]    // Create a Work Item (verify that the Resource exists)
[HttpGet("/api/v1/work-items/{workItemId}")]               // Get one Work Item
[HttpPatch("/api/v1/work-items/{workItemId}")]             // Update a Work Item
[HttpDelete("/api/v1/work-items/{workItemId}")]            // Delete a Work Item
[HttpGet("/api/v1/resources/{resourceId}/work-items")]     // List all Work Items for a Resource

// Task routes
[HttpPost("/api/v1/work-items/{workItemId}/tasks")]        // Create a Task (verify that the Work Item exists)
[HttpGet("/api/v1/tasks/{taskId}")]                        // Get one Task
[HttpPatch("/api/v1/tasks/{taskId}")]                      // Update a Task
[HttpDelete("/api/v1/tasks/{taskId}")]                     // Delete a Task
```

---

### 2. Delegate Application Flow Execution to a Use Case

```csharp
// ✅ Allowed: map HTTP DTO to Use Case input and invoke the inbound port
[HttpPost("/resources")]
public async Task<IActionResult> Create(
    CreateResourceRequest request,
    CancellationToken cancellationToken)
{
    var input = new CreateResourceInput(request.Name, request.UserId);
    var output = await this.createResourceUseCase.ExecuteAsync(
        input,
        cancellationToken);

    return Ok(output);
}

// ❌ Forbidden: controller contains business logic
[HttpPost("/resources")]
public IActionResult Create(CreateResourceRequest request)
{
    var entity = new Resource(request.Name);
    _dbContext.Add(entity);
    _dbContext.SaveChanges();
    return Ok();
}
```

Controllers must not inject a concrete Handler, `IMessageBus`, mediator/dispatcher, write
Repository, Aggregate, or Domain Service.

Only an explicitly designated pure-query endpoint may directly inject a read-only
`IQueryRepository`-derived port or query service. This exception is allowed but discouraged;
unless explicitly designated, create and invoke a query Use Case. Direct query-handler dispatch
is not covered by this exception.

---

### 3. Request/Response DTO Design

Define Request/Response DTOs with `record`:

```csharp
// ✅ Correct: define Request DTOs with record
public sealed record CreateResourceRequest(
    [Required] string Name,
    [Required] string UserId,
    string? Description = null);

public sealed record UpdateResourceRequest(
    [Required] string Name,
    string? Description = null);

// ✅ Correct: define Response DTOs with record
public sealed record ResourceResponse(
    string Id,
    string Name,
    string State,
    DateTime CreatedAt);

// ❌ Incorrect: define DTOs with class
public class CreateResourceRequest  // Use record instead
{
    public string Name { get; set; }
    public string UserId { get; set; }
}
```

---

### 4. Dependencies Must Be Injected Through the Constructor

Do not use `[FromServices]` or other injection mechanisms:

```csharp
// ✅ Correct: Constructor Injection
[ApiController]
[Route("api/v1/resources")]
public class ResourcesController : ControllerBase
{
    private readonly ICreateResourceUseCase createResourceUseCase;
    
    public ResourcesController(ICreateResourceUseCase createResourceUseCase)
    {
        this.createResourceUseCase = createResourceUseCase;
    }
}

// ❌ Incorrect: [FromServices] injection
[HttpPost]
public async Task<IActionResult> CreateResource(
    [FromBody] CreateResourceRequest request,
    [FromServices] ICreateResourceUseCase useCase)  // FORBIDDEN!
{
    // ...
}
```

---

## 🎯 HTTP Status Code Mapping

### Success Status Codes

```csharp
// GET - 200 OK
return Ok(resourceDto);

// POST - 201 Created
return CreatedAtAction(nameof(GetResource), new { id = resourceId }, response);

// PUT - 200 OK
return Ok(updatedResource);

// DELETE - 204 No Content
return NoContent();

// Async operation - 202 Accepted
return Accepted(operationId);
```

### Error Status Codes

```csharp
// 400 Bad Request - validation error
if (!result.IsSuccess)
    return BadRequest(new ProblemDetails 
    { 
        Detail = result.Error,
        Status = 400 
    });

// 404 Not Found - resource does not exist
if (resource is null)
    return NotFound();

// 409 Conflict - resource conflict
if (result.Error?.Contains("already exists") == true)
    return Conflict(new ProblemDetails { Detail = result.Error });
```

---

## 🎯 Error Handling

### Use ProblemDetails

```csharp
// ✅ Correct: use standard ProblemDetails
return BadRequest(new ProblemDetails
{
    Title = "Validation Failed",
    Detail = "Resource name is required",
    Status = StatusCodes.Status400BadRequest,
    Instance = HttpContext.Request.Path,
    Extensions = 
    {
        ["traceId"] = Activity.Current?.Id ?? HttpContext.TraceIdentifier
    }
});

// Or use ValidationProblemDetails
return ValidationProblem(ModelState);
```

---

## 🎯 Request Validation

### Use FluentValidation (Recommended)

```csharp
public class CreateResourceRequestValidator : AbstractValidator<CreateResourceRequest>
{
    public CreateResourceRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Resource name is required")
            .MaximumLength(100).WithMessage("Resource name must not exceed 100 characters");
            
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("User ID is required");
            
        RuleFor(x => x.Price)
            .GreaterThan(0).When(x => x.Price.HasValue)
            .WithMessage("Price must be positive");
    }
}
```

---

## 🔍 Checklist

### Controller Structure
- [ ] Inherits from `ControllerBase` (not `Controller`).
- [ ] Has the `[ApiController]` attribute.
- [ ] Has a `[Route]` that defines the base path.
- [ ] Uses Constructor Injection.
- [ ] Injects only Use Case interfaces by default.
- [ ] Does not inject concrete Handlers, buses, mediators/dispatchers, write Repositories, or Domain Services.
- [ ] A direct Query Repository/Service dependency for a pure query has an explicit endpoint-level rationale.
- [ ] The path includes a version number (for example, `/api/v1`).

### HTTP Rules
- [ ] Uses the correct HTTP method.
- [ ] Returns an appropriate status code.
- [ ] Uses RESTful URL design.
- [ ] Uses plural resource names.

### Request/Response
- [ ] Defines DTOs with `record`.
- [ ] Has appropriate validation attributes.
- [ ] Returns errors with `ProblemDetails`.

### Documentation
- [ ] Has `[ProducesResponseType]` attributes.
- [ ] Has Swagger documentation when needed.

---

## 📂 Code Examples

For more complete examples, see:

| Example | Path |
|------|------|
| Controller examples | [../examples/controller/](../examples/controller/) |
| ASP.NET Core examples | [../examples/aspnet-core/](../examples/aspnet-core/) |
| DTO examples | [../examples/dto/](../examples/dto/) |

---

## Related Documents

- [usecase-standards.md](usecase-standards.md)
- [test-standards.md](test-standards.md)
