# Controller Code Generation Prompt (Dotnet)

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Generate ASP.NET Core controllers that are thin and map DTOs to Use Cases.

## Mandatory References
- `../../../../../shared/common-rules.md`
- `../../../../../shared/dto-conventions.md`
- `../../../../../shared/testing-strategy.md`

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
