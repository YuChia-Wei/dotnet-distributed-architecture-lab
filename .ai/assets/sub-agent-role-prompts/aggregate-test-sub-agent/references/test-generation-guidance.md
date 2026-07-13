# Aggregate Test Generation Prompt (Dotnet)

Generate aggregate-level tests (not use case tests).

## Mandatory References
- `../assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`

## Rules
- Use GWT structure and naming for every test. BDDfy is the default profile; if the target team explicitly opted out, preserve GWT in plain xUnit rather than using 3A.
- `.feature` files are optional; support an explicitly supplied/requested feature or a selected target feature-runner profile without choosing the runner/package.
- No BaseTestClass
- Use NSubstitute for mocks (if needed)
- Verify event serialization/deserialization

## Output Location
`src/tests/Domain/<Aggregate>/`

