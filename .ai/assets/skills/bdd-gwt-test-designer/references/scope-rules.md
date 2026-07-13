# Scope Rules

Use `bdd-gwt-test-designer` when the main task is to design or review test scenarios before writing code.

## In Scope

- derive GWT scenarios from requirement/spec text
- convert acceptance criteria into test cases
- identify positive, negative, and edge scenarios
- plan Then assertions and setup needs
- suggest the right test level
- suggest the right `.dev/specs/tests/` storage category and output path
- design a `.feature` artifact when the user supplies one, explicitly requests it, or the target profile has selected a feature runner

## Out of Scope

- generating the final xUnit/BDDfy test class
- fixing test infrastructure
- changing production code to make tests pass
- using Gherkin `.feature` files as the default output
- choosing a feature runner or package for the target team

## Escalate or Handoff

Use other workflows when:

- the user needs implemented test code
- the test problem is actually architecture ambiguity
- the codebase behavior conflicts with the stated requirement

Recommended handoffs:

- test code implementation: existing test generation prompt/workflow
- architecture ambiguity: `ddd-ca-hex-architect`
- concrete code defects: `code-reviewer`
