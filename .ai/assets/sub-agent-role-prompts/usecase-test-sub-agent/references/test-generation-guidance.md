# Use Case Test Generation Prompt (Dotnet)

Generate use case tests with mandatory Given-When-Then structure and naming. Use xUnit + BDDfy by default; if the target team explicitly opted out of BDDfy, retain GWT in plain xUnit and do not use 3A. `.feature` files are optional and supported when supplied/requested or selected by the target profile; do not infer a feature runner/package.

## Mandatory References
- `../assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`

## Rules
- Follow ezSpec -> BDDfy mapping rules in .ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md
- No BaseTestClass
- Use NSubstitute for mocks
- Verify domain events with async-safe assertions
- Each AC maps to a Scenario; each then/and becomes an explicit Then/And assertion

## Output Structure
`src/tests/Application/<Aggregate>/UseCases/`

