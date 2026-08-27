# Get Order Details Test Spec

## Inputs Used

- `ORD-006` and `API-006` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/domains/order/usecase/get-order-details.json`
- `tests/SaleOrders.Tests/GetOrderDetailsEndpointTests.cs`

## Implementation Status

- Status: `implemented-partial`
- The existing endpoint test covers the found response; direct use-case not-found behavior remains planned.

## Scenario Set

### Scenario 1: return the current projection

- Test level: `application`
- Given: the query repository returns an order projection.
- When: `IGetOrderDetailsUseCase.ExecuteAsync` runs.
- Then: the result succeeds; id, product, quantity, date, amount, status, and reason match the projection.

### Scenario 2: return not found

- Test level: `application`
- Given: no projection exists for the id.
- When: the query use case runs.
- Then: the result is a typed failure/not-found; no placeholder order is synthesized.

### Scenario 3: preserve endpoint contract

- Test level: `controller`
- Given: the use case returns a known projection.
- When: `GET /api/orders/{id}` is called.
- Then: HTTP 200 and the response DTO match the production API contract.

## Assertion Notes

- Each response field and status mapping needs an explicit assertion.
- Add an endpoint not-found assertion once the quality-uplift error mapping is implemented.

## Recommended Test Spec Path

`.dev/specs/tests/order/use-cases/get-order-details.test-spec.md`

## Implementation and Execution Handoff

Only scenario design is authorized; current executable evidence is limited to the existing endpoint test.
