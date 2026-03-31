# UpdateProduct Test Spec

## Scope

Application-level verification for `UpdateProduct`.

## Related Production Spec

- `.dev/specs/domains/product/usecase/update-product.json`

## Scenario List

- Happy path: existing product data is updated successfully
- Failure path: target product does not exist
- Failure path: invalid text or price input is rejected

## Given-When-Then

### Scenario 1: update succeeds for an existing product

- Given:
  - an existing product is loaded by id
  - valid name, description, and non-negative price are provided
- When:
  - `UpdateProductCommand` is handled
- Then:
  - the product aggregate is updated with the new values
  - persistence is performed
  - a `ProductUpdated` domain event is recorded

### Scenario 2: product does not exist

- Given:
  - no product exists for the requested id
- When:
  - `UpdateProductCommand` is handled
- Then:
  - the operation fails with `KeyNotFoundException` or equivalent not-found semantics
  - no update is persisted
  - no `ProductUpdated` domain event is recorded

### Scenario 3: invalid update input is rejected

- Given:
  - an existing product is loaded
  - the requested name or description is blank, or the price is negative
- When:
  - `UpdateProductCommand` is handled
- Then:
  - the operation fails with validation or domain rejection
  - no invalid update is persisted
  - no `ProductUpdated` domain event is recorded

## Assertions

- repository load and save behavior
- updated aggregate field values
- domain event recording behavior
- not-found and validation failure semantics

## Test Level

- Primary: `application`
- Secondary: `unit`

## Notes / Deferred Cases

- Concurrency/version-conflict scenarios should be added later if optimistic concurrency becomes part of the documented contract.
