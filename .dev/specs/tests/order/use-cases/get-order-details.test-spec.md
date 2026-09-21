# Get Order Details Test Spec

## Inputs Used

- `ORD-007`, `API-001`, `API-002`, and `API-003` in `.dev/requirement/reconstructable-system-baseline.md`
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
- Then: the non-null `OrderDetailsResponse` contains `OrderId` and exactly one `LineItems` entry with the projection's `ProductId` and `Quantity`. Date, amount, status, and reason are not fields required by this response contract.

### Scenario 2: return not found

- Test level: `application`
- Given: no projection exists for the id.
- When: the query use case runs.
- Then: the result is `null`; no placeholder order or invented Result wrapper is synthesized.

### Scenario 3: preserve endpoint contract

- Test level: `controller`
- Given: the use case returns a known projection.
- When: `GET /api/orders/{id}` is called.
- Then: HTTP 200 and the response DTO match the production API contract.

## Assertion Notes

- Each response field and status mapping needs an explicit assertion.
- Add the missing endpoint not-found assertion: a null use-case response maps to HTTP 404 under the existing `ORD-007` contract.

## Recommended Test Spec Path

`.dev/specs/tests/order/use-cases/get-order-details.test-spec.md`

## Implementation and Execution Handoff

The found-response endpoint test is the current executable anchor. Direct query mapping, null-result, and endpoint-404 assertions remain explicit test gaps; this document does not claim they have executed.
