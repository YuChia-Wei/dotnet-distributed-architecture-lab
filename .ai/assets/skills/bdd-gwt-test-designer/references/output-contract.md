# Output Contract

Use this structure for `design` unless the user asks for another format.
For `review`, use the shared artifact design/review contract and `review-criteria.md`;
do not replace the submitted artifact with an authored scenario set.

The default artifact is scenario notes. If the user provides or explicitly requests a `.feature` file, or the target profile selects a feature runner, render the same scenario set as valid Gherkin feature/scenario design and record the selected runner only when project evidence names it.

## 1. Inputs Used

- requirement/spec/doc paths
- code paths if reverse-engineering existing behavior
- assumptions

## 2. Scenario Set

For each scenario provide:

- stable scenario ID and name, source binding and traced requirement/AC IDs
- test level
- Given
- When
- Then
- optional And

Use the [GWT handoff contract](../../../shared/GWT-TEST-HANDOFF-CONTRACT.md)
for concrete data, parameterized-row identities, observable outcomes and
explicit unknowns. Preserve the user's artifact format; this does not require
another specification or executable test code from the designer.

## 3. Assertion Notes

- which Then items need explicit assertions
- special event/message/state verification points
- setup or fixture notes, controllable dependency/time/data inputs and evidence limitations

## 4. Coverage Gaps

- missing rules
- unresolved ambiguities
- scenarios intentionally deferred

## 5. Recommended Test Spec Path

- recommend one concrete output path under `.dev/specs/tests/`
- choose the category that best matches the test target:
  - `aggregate/`
  - `use-cases/`
  - `integration/`
  - `app-services/` when explicitly needed
  - `domain-services/` when explicitly needed
  - `cross-domain/` for multi-BC flows
  - `e2e/` for full journeys

Examples:

- `.dev/specs/tests/<context>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<context>/integration/<integration-target>.test-spec.md`
- `.dev/specs/tests/cross-domain/<scenario>.test-spec.md`

## 6. Implementation And Execution Handoff

State whether concrete test implementation is separately authorized. If it is
not, return only the scenario/assertion design. If it is, hand the source paths,
scenario set, assertion notes, selected test level, and open questions to
`slice-implementer`; do not claim that this design authorizes a code change.
Keep the later implementation result separate from target-owned test-execution
commands and outcomes.

Carry the scenario identities and outcome assertions into the receiving
implementation. The receiver completes the scenario-to-test/step/assertion
mapping defined by the shared contract; the designer does not invent future
test locations, review results or execution evidence.
