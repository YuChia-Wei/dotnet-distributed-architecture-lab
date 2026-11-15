# Controller Coding Standards (.NET)

This document provides guidance for the ASP.NET Core Controller layer, including Controller structure, Request/Response DTOs, and error handling.

This is unregistered guidance, not a registered normative rule. The target owns
adoption of these conventions; reading this document or its review route does not
establish normative coverage. The engineering rule catalog retains its
unpacketized status until stable rule identities are explicitly allocated.

---

The direct UseCase policy keeps HTTP delivery separate from reusable operation
orchestration. It costs explicit mapping; other application-handler architectures
require separate selection. See [rationale](../../references/policy-rationale.md#controller-usecase-handler-and-operation-shape).

## 📌 Overview

Controllers are responsible only for the transport layer and input validation; they must not contain business logic.

- **Execution delegation**: Where the target adopts the Use Case profile, a Controller delegates only to an explicit Use Case interface by default.
- **Access**: Verify route and resource access against the actual HTTP contract. Preserve any authorization the application operation owns.
- **Request validation**: Use ASP.NET Core Model Validation for the attribute-based examples. FluentValidation applies only when explicitly selected by the target; it is not a default dependency.
- **Error responses**: Use the unified `ProblemDetails` format.

---

## 🏷️ Illustrative Pattern Markers

These hints describe the conventions below. They do not prove that an automated
check is configured or executed; target-selected checks require separate evidence.

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

## 🔴 Controller Conventions (When Adopted by the Target)

### 1. REST API Path Design Principles

**Use nested creation endpoints and flat resource addresses.**

Under this optional route convention, nesting expresses which parent's
collection accepts the creation. A stable flat address supports the new
resource's independent identity and lifecycle.

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

    return Created($"/resources/{output.Id}", output);
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

Map transport inputs to typed operation input and forward the request's
cancellation token for asynchronous calls. `Task<ActionResult<T>>` is another
possible action signature when supported by the HTTP contract. If an API
accepts a sentinel such as `all` or `unassigned`, normalize it before invoking
the read operation. Return canonical resource state for navigation when the
client needs it and keep client routing decisions in the client.

---

### 3. Request/Response DTO Design

Define Request/Response DTOs with `record`. Use action-named `*Request` records
for inbound data and `*Response` records for outgoing data. Keep them distinct
from Domain entities and Application `*Input` and `*Output` types. Use the
target's file layout and validation mechanism.

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

HTTP tests cover the real route, validation, access, status, body and error
shape. When the target uses `WebApplicationFactory`, replace the Use Case port
as needed to control its result. Exercise concrete Use Case behavior at its
own boundary. An explicitly selected pure-query endpoint has its own read
boundary.

### Success Status Codes

```csharp
// GET - 200 OK
return Ok(resourceDto);

// POST - 201 Created
return CreatedAtAction(nameof(GetResource), new { id = resourceId }, response);

// PUT / PATCH - 200 OK (or 204 No Content when no response body is returned)
return Ok(updatedResource);

// DELETE - 204 No Content
return NoContent();

// Async operation - 202 Accepted
return Accepted(operationId);
```

### Error Status Codes

The illustrative Application result exposes `IsSuccess`, `Error`, and a typed
`ErrorCode` using the enum below. The target owns this result contract. Map a
specific failure before a general failure; never classify errors by message text.

```csharp
public enum ResourceErrorCode
{
    None,
    InvalidRequest,
    AlreadyExists
}
```

```csharp
// 409 Conflict - resource conflict
if (!result.IsSuccess && result.ErrorCode == ResourceErrorCode.AlreadyExists)
    return Conflict(new ProblemDetails
    {
        Detail = result.Error,
        Status = StatusCodes.Status409Conflict
    });

// 400 Bad Request - invalid request (after specific failures have been mapped)
if (!result.IsSuccess)
    return BadRequest(new ProblemDetails
    {
        Detail = result.Error,
        Status = StatusCodes.Status400BadRequest
    });

// 404 Not Found - resource does not exist
if (resource is null)
    return NotFound();
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

### Optional FluentValidation Example

ASP.NET Core Model Validation is used by the attribute-based DTO examples above.
Use the following alternative only when the target explicitly selects
FluentValidation and its integration. This guidance neither installs the library
nor makes it a default dependency. The target owns the selection and its evidence.

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

        RuleFor(x => x.Description)
            .MaximumLength(500).WithMessage("Description must not exceed 500 characters")
            .When(x => x.Description is not null);
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

## Related Documents

- [Packaged API starters](../../tooling/generation/README.md)
- [usecase-standards.md](../../architecture/ddd-cqrs/usecase-standards.md)
- [test-standards.md](../../testing/test-standards.md)
