# Use Case Test Generation Prompt (Dotnet)

Generate use case tests with mandatory Given-When-Then structure and naming. Use xUnit + BDDfy by default; if the target team explicitly opted out of BDDfy, retain GWT in plain xUnit and do not use 3A. `.feature` files are optional and supported when supplied/requested or selected by the target profile; do not infer a feature runner/package.

## Mandatory References
- `.ai/assets/skills/slice-implementer/roles/usecase-test-sub-agent/sub-agent.yaml`
- `../assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`

## Rules
- Follow the GWT mapping rules in .ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md
- No BaseTestClass
- Resolve the target `testing.mocking` selection; use NSubstitute by default
- Verify domain events with async-safe assertions
- Each AC maps to a Scenario; each then/and becomes an explicit Then/And assertion
- Consume `.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md` and return concrete
  scenario/data-row-to-test/step/assertion mappings with honest execution status.
- Follow the canonical .NET step-method contract and the bounded
  `examples/bdd-step-methods/` reference for visible data, one primary action,
  isolated results and async/exception handling. Do not copy incomplete legacy
  fixture snippets as if they were executable templates.

## Output Structure
`src/tests/Application/<Aggregate>/UseCases/`
