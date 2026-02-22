# Reactor Test Generation Prompt (Dotnet)

## Mandatory References
- `./shared/testing-strategy.md`
- `./shared/common-rules.md`

Generate reactor tests using xUnit + BDDfy with Gherkin-style naming. No BaseTestClass.

## Rules
- Follow ezSpec -> BDDfy mapping rules in ./shared/testing-strategy.md
- Use NSubstitute for mocks
- Verify event handling and side effects
- Async verification required
- Each then/and condition must map to an explicit assertion step

## Output Structure
`src/tests/Application/<Aggregate>/Reactors/`
