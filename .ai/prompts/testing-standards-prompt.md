# Testing Standards Prompt (Dotnet)

General testing standards for .NET migration.

## Rules
- xUnit + BDDfy (Gherkin-style naming only)
- NSubstitute only
- No BaseTestClass
- Async-safe event verification required
