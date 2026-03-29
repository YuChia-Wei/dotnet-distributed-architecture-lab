# Aggregate Test Generation Prompt (Dotnet)

Generate aggregate-level tests (not use case tests).

## Mandatory References
- `../assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`

## Rules
- Use xUnit + BDDfy with Gherkin-style naming (no `.feature` files)
- No BaseTestClass
- Use NSubstitute for mocks (if needed)
- Verify event serialization/deserialization

## Output Location
`src/tests/Domain/<Aggregate>/`

