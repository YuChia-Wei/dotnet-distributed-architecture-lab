# Product Repository Persistence Test Spec

## Scope

Integration-focused verification for product persistence boundaries.

## Related Production Spec

- `.dev/specs/domains/product/usecase/create-product.json`
- `.dev/specs/domains/product/usecase/update-product.json`
- `.dev/specs/domains/product/usecase/delete-product.json`
- `.dev/specs/domains/product/entity/product-spec.md`

## Scenario List

- Happy path: created product can be persisted and loaded back
- Happy path: updated product persists new values
- Happy path: deleted product is no longer retrievable through normal product lookup
- Failure path: invalid aggregate state is not persisted through normal application flow

## Given-When-Then

### Scenario 1: persist and reload a newly created product

- Given:
  - a valid `Product` aggregate exists in memory
- When:
  - the repository persists the aggregate and it is loaded again by id
- Then:
  - stored values match the original aggregate state
  - the identifier remains stable across the round trip

### Scenario 2: persist an updated product

- Given:
  - an existing product has already been stored
- When:
  - the aggregate is updated and saved again
- Then:
  - the reloaded aggregate contains the updated name, description, and price

### Scenario 3: persist product deletion

- Given:
  - an existing product has already been stored
- When:
  - the aggregate is deleted through normal application flow
- Then:
  - the product is no longer returned by normal lookup semantics
  - no stale active record remains visible to normal callers

### Scenario 4: invalid product state is blocked before persistence

- Given:
  - invalid product input such as blank text or negative price
- When:
  - normal application flow attempts create or update
- Then:
  - the invalid aggregate is not committed to persistence

## Assertions

- repository save and load round-trip behavior
- persisted field accuracy
- delete persistence and lookup behavior
- absence of invalid writes in normal flow

## Test Level

- Primary: `integration`
- Secondary: `contract`

## Notes / Deferred Cases

- Database schema details and migration verification remain out of scope for this Stage 4 baseline.
