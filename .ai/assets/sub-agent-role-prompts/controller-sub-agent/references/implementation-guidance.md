# Controller Code Generation Prompt (Dotnet)

Generate ASP.NET Core controllers that are thin and map DTOs to Use Cases.

## Mandatory References
- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/dto-conventions.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`

## Rules
- Controllers must not contain business logic
- Inject explicit Use Case interfaces, never concrete Handlers, `IMessageBus`,
  mediators/dispatchers, write repositories, Aggregates, or Domain services
- Map Request DTOs to transport-neutral Use Case inputs
- Invoke `ExecuteAsync(input, cancellationToken)` and forward the non-optional
  request `CancellationToken`
- Use direct Query Repository/Service injection only when the endpoint is
  explicitly designated as a pure-query exception
- Use Request/Response DTOs as separate files
- Return typed Response (`Task<ActionResult<T>>`)
- Use proper HTTP status codes

## Output Structure
`src/Api/Controllers/<Aggregate>/`

