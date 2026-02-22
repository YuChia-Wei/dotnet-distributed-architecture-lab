# Controller Test Generation Prompt (Dotnet)

Generate controller tests using WebApplicationFactory + xUnit + BDDfy (Gherkin-style naming).

## Rules
- Mock dependencies with NSubstitute
- Validate HTTP status codes and response shape
- DTOs are separate files

## Output Structure
`src/tests/Api/Controllers/<Aggregate>/`
