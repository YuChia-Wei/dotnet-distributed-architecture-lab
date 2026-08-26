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

- test code implementation: `slice-implementer` with a separately authorized,
  bounded test-implementation slice. A test-only slice selects `generic` as
  its primary mode and evaluates the applicable concrete test bindings.
- architecture ambiguity: `ddd-ca-hex-architect`
- concrete code defects: `code-reviewer`

## Design Does Not Authorize Implementation Or Execution

This skill has no `role_bindings` and does not produce a `role_execution`
record. Its scenario, assertion, and test-level recommendations are evidence
for a later authorization decision, not an instruction to change test or
production code. The receiving `slice-implementer` owns concrete test
implementation; target-owned commands or the selected test-execution contract
own execution and result evidence. Keep those handoffs distinct.
