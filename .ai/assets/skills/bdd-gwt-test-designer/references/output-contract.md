# Output Contract

Use this structure unless the user asks for another format.

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

- `.dev/specs/tests/order/use-cases/place-order.test-spec.md`
- `.dev/specs/tests/inventory-item/integration/decrease-stock-repository.test-spec.md`
- `.dev/specs/tests/cross-domain/place-order-and-reserve-stock.test-spec.md`
