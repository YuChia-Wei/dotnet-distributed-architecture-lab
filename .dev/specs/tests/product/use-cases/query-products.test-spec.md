# Query Products Test Spec

## Inputs Used

- `PRD-005`, `PRD-006`, `API-001`, and `API-002` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/domains/product/usecase/get-all-products.json`
- `.dev/specs/domains/product/usecase/get-product-by-id.json`

## Implementation Status

- Status: `planned`
- Product command tests exist, but the two query use cases and soft-delete filtering need explicit test ownership.

## Scenario Set

### Scenario 1: return active products only

- Test level: `application`
- Given: active and soft-deleted rows exist.
- When: `IGetAllProductsUseCase.ExecuteAsync` runs.
- Then: each active row is mapped once; deleted rows are absent; an empty active set returns an empty collection rather than failure.

### Scenario 2: return one active product

- Test level: `application`
- Given: an active row exists for the requested id.
- When: `IGetProductByIdUseCase.ExecuteAsync` runs.
- Then: the result succeeds and every response field matches the query model.

### Scenario 3: hide missing or deleted product

- Test level: `application`
- Given: the id is absent or resolves only to a soft-deleted row.
- When: the get-by-id use case runs.
- Then: the result is failure/not-found and does not expose deleted content.

## Assertion Notes

- Assert repository call count and cancellation propagation.
- Assert field-by-field DTO mapping, not object reference equality.
- Assert the deleted-row filter at PostgreSQL integration level as a separate persistence test.

## Recommended Test Spec Path

`.dev/specs/tests/product/use-cases/query-products.test-spec.md`

## Implementation and Execution Handoff

Concrete tests and test execution are not authorized by this design-only workflow.
