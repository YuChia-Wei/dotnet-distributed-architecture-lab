# CreateProduct Test Spec

## Scope

Application and aggregate-facing verification for `CreateProduct`.

## Implementation Status

- Status: `planned`
- Current tests cover Product construction invariants, but do not directly exercise `ICreateProductUseCase`.

## Related Production Spec

- `.dev/specs/domains/product/usecase/create-product.json`

## Scenario List

- Happy path: valid product data creates a new product
- Failure path: blank name or description is rejected
- Failure path: negative price is rejected

## Given-When-Then

### Scenario 1: create succeeds with valid input

- Given:
  - valid name, description, and non-negative price are provided
- When:
  - `ICreateProductUseCase.ExecuteAsync` is invoked with `CreateProductInput`
- Then:
  - a new product aggregate is created with a generated id
  - persistence is performed
  - a `ProductCreated` domain event is recorded

### Scenario 2: blank text input is rejected

- Given:
  - name or description is blank
- When:
  - `ICreateProductUseCase.ExecuteAsync` is invoked with `CreateProductInput`
- Then:
  - creation fails with validation or domain rejection
  - no product is persisted
  - no `ProductCreated` domain event is recorded

### Scenario 3: negative price is rejected

- Given:
  - the requested price is less than zero
- When:
  - `ICreateProductUseCase.ExecuteAsync` is invoked with `CreateProductInput`
- Then:
  - creation fails with validation or domain rejection
  - no product is persisted
  - no `ProductCreated` domain event is recorded

## Assertions

- created aggregate fields
- generated identifier existence
- repository save behavior
- domain event recording behavior
- validation or domain error semantics

## Test Level

- Primary: `application`
- Secondary: `unit`

## Notes / Deferred Cases

- API-level validation mapping belongs to later adapter or end-to-end specs.
