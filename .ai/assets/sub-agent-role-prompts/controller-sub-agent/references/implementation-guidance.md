# Controller Code Generation Prompt (Dotnet)

Generate ASP.NET Core controllers that are thin and map DTOs to Use Cases.

## Mandatory References
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/dto-conventions.md`
- `.ai/assets/shared/testing-strategy.md`

## Rules
- Controllers must not contain business logic
- Use Request/Response DTOs as separate files
- Return typed Response (ActionResult<T>)
- Use proper HTTP status codes

## Output Structure
`src/Api/Controllers/<Aggregate>/`

