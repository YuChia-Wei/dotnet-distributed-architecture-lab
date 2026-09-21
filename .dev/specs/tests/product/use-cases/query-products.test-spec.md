# Query Products Test Spec

## Inputs Used

- `PRD-004`, `PRD-005`, `API-001`, `API-002`, and `API-003` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/domains/product/usecase/get-all-products.json`
- `.dev/specs/domains/product/usecase/get-product-by-id.json`

## Implementation Status

- Status: `implemented-partial`
- `tests/SaleProducts.Tests/ProductHandlersTests.cs` covers get-all delegation/result count and get-by-id not-found. Found-item field mapping, empty results, cancellation propagation, and PostgreSQL soft-delete filtering still need explicit assertions.

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
- Then: the returned DTO's fields match the query model.

### Scenario 3: hide missing or deleted product

- Test level: `application`
- Given: the id is absent or resolves only to a soft-deleted row.
- When: the get-by-id use case runs.
- Then: the use case reports not-found semantics (currently `KeyNotFoundException`) and does not expose deleted content; the adapter's required HTTP mapping is specified separately.

## Assertion Notes

- Assert repository call count and cancellation propagation.
- Assert field-by-field DTO mapping, not object reference equality.
- Assert the deleted-row filter at PostgreSQL integration level as a separate persistence test.

## Recommended Test Spec Path

`.dev/specs/tests/product/use-cases/query-products.test-spec.md`

## Implementation and Execution Handoff

The existing query tests provide partial coverage only. The remaining scenario assertions need an implementation slice and actual execution before they may be reported as passed.
