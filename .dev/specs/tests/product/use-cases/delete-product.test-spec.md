# DeleteProduct Test Spec

## Scope

Application-level verification for `DeleteProduct`.

## Related Production Spec

- `.dev/specs/domains/product/usecase/delete-product.json`

## Scenario List

- Happy path: existing product is deleted successfully
- Failure path: target product does not exist
- Domain path: successful deletion records `ProductDeleted`

## Given-When-Then

### Scenario 1: delete succeeds for an existing product

- Given:
  - an existing product is loaded by id
- When:
  - `DeleteProductCommand` is handled
- Then:
  - the product is deleted or removed according to repository behavior
  - persistence is performed
  - a `ProductDeleted` domain event is recorded

### Scenario 2: product does not exist

- Given:
  - no product exists for the requested id
- When:
  - `DeleteProductCommand` is handled
- Then:
  - the operation fails with not-found semantics
  - no delete persistence is performed
  - no `ProductDeleted` domain event is recorded

## Assertions

- repository load and delete/save behavior
- delete result semantics
- domain event recording behavior
- not-found failure semantics

## Test Level

- Primary: `application`
- Secondary: `unit`

## Notes / Deferred Cases

- Downstream read-model cleanup or integration side effects should be documented separately if product deletion later becomes externally observable.
