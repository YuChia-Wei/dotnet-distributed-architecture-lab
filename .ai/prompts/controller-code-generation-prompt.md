# Controller Code Generation Prompt (Dotnet)

Generate ASP.NET Core controllers that are thin and map DTOs to Use Cases.

## Mandatory References
- `./shared/common-rules.md`
- `./shared/dto-conventions.md`
- `./shared/testing-strategy.md`

## Rules
- Controllers must not contain business logic
- Use Request/Response DTOs as separate files
- Return typed Response (ActionResult<T>)
- Use proper HTTP status codes

## Output Structure
`src/Api/Controllers/<Aggregate>/`
