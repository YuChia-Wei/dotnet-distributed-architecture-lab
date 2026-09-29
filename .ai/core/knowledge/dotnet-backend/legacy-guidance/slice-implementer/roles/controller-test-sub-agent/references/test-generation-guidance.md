# Controller Test Generation Prompt (Dotnet)

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Generate controller tests using WebApplicationFactory + xUnit with mandatory Given-When-Then structure and naming. BDDfy is the default profile; an explicit team opt-out permits plain xUnit GWT, not 3A. Support optional `.feature` design only when supplied/requested or selected by the target profile, without inferring a runner/package.

## Mandatory References
- `../sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`

## Rules
- Mock dependencies with the target `testing.mocking` selection; use NSubstitute by default
- Validate HTTP status codes and response shape
- DTOs are separate files

## Output Structure
`src/tests/Api/Controllers/<Aggregate>/`
