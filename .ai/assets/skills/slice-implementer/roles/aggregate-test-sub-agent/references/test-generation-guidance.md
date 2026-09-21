# Aggregate Test Generation Prompt (Dotnet)

Generate aggregate-level tests (not use case tests).

## Mandatory References
- `.ai/assets/skills/slice-implementer/roles/aggregate-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`

## Rules
- Use GWT structure and naming for every test. BDDfy is the default profile; if the target team explicitly opted out, preserve GWT in plain xUnit rather than using 3A.
- `.feature` files are optional; support an explicitly supplied/requested feature or a selected target feature-runner profile without choosing the runner/package.
- No BaseTestClass
- Resolve the target `testing.mocking` selection; use NSubstitute by default
- Verify event serialization/deserialization
- Consume `.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md` and return concrete
  scenario/data-row-to-test/step/assertion mappings with honest execution status.
- Apply the canonical .NET step-method responsibilities, including visible
  scenario data and isolated result state. Keep the runnable step-method
  example's use-case fixture separate from this role's aggregate test level.

## Output Location
`src/tests/Domain/<Aggregate>/`
