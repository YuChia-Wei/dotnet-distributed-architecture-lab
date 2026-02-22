# Aggregate Test Generation Prompt (Dotnet)

Generate aggregate-level tests (not use case tests).

## Mandatory References
- `./shared/testing-strategy.md`
- `./shared/common-rules.md`

## Rules
- Use xUnit + BDDfy with Gherkin-style naming (no `.feature` files)
- No BaseTestClass
- Use NSubstitute for mocks (if needed)
- Verify event serialization/deserialization

## Output Location
`src/tests/Domain/<Aggregate>/`
