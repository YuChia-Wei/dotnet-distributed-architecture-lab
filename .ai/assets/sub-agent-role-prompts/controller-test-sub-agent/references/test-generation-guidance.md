# Controller Test Generation Prompt (Dotnet)

Generate controller tests using WebApplicationFactory + xUnit + BDDfy (Gherkin-style naming).

## Mandatory References
- `../assets/sub-agent-role-prompts/controller-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`

## Rules
- Mock dependencies with NSubstitute
- Validate HTTP status codes and response shape
- DTOs are separate files

## Output Structure
`src/tests/Api/Controllers/<Aggregate>/`
