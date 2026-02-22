# Contract Test Generation Prompt (Dotnet)

Contract tests validate DBC preconditions on aggregates.

## Rules
- Pure xUnit (no DI)
- One Nested class per command method (translate to separate test class in .NET)
- assertThrows -> Assert.Throws
- Validate PreconditionViolationException

## Output Location
`src/tests/Domain/<Aggregate>/Contracts/<Aggregate>ContractTests.cs`
