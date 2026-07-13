# Output Contract

Use this structure unless the user asks for another format.

The default artifact is scenario notes. If the user provides or explicitly requests a `.feature` file, or the target profile selects a feature runner, render the same scenario set as valid Gherkin feature/scenario design and record the selected runner only when project evidence names it.

## 1. Inputs Used

- requirement/spec/doc paths
- code paths if reverse-engineering existing behavior
- assumptions

## 2. Scenario Set

For each scenario provide:

- scenario name
- test level
- Given
- When
- Then
- optional And

## 3. Assertion Notes

- which Then items need explicit assertions
- special event/message/state verification points
- setup or fixture notes

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
