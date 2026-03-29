# Use Case Test Generation Prompt (Dotnet)

Generate use case tests using xUnit + BDDfy with Gherkin-style naming only (no `.feature` files).

## Mandatory References
- `../assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`

## Rules
- Follow ezSpec -> BDDfy mapping rules in .ai/assets/shared/testing-strategy.md
- No BaseTestClass
- Use NSubstitute for mocks
- Verify domain events with async-safe assertions
- Each AC maps to a Scenario; each then/and becomes an explicit Then/And assertion

## Output Structure
`src/tests/Application/<Aggregate>/UseCases/`

