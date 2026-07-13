# Product Aggregate Test Spec

## Scope

Aggregate-focused verification for `Product` invariant enforcement and event recording.

## Related Production Spec

- `.dev/specs/domains/product/entity/product-spec.md`

## Scenario List

- Happy path: product creation records valid state and `ProductCreated`
- Happy path: product update records new state and `ProductUpdated`
- Happy path: product deletion records `ProductDeleted`
- Failure path: blank name or description is rejected
- Failure path: negative price is rejected

## Given-When-Then

### Scenario 1: create product with valid values

- Given:
  - valid name, description, and non-negative price are provided
- When:
  - a `Product` aggregate is constructed
- Then:
  - aggregate state contains the provided values
  - a valid identifier exists
  - a `ProductCreated` domain event is recorded

### Scenario 2: update product with valid values

- Given:
  - an existing `Product` aggregate
  - valid replacement name, description, and non-negative price
- When:
  - `Product.Update` is invoked
- Then:
  - aggregate state reflects the new values
  - a `ProductUpdated` domain event is recorded

### Scenario 3: delete an existing product

- Given:
  - an existing `Product` aggregate
- When:
  - `Product.Delete` is invoked
- Then:
  - the aggregate records a `ProductDeleted` domain event
  - no additional invalid mutation is required before deletion intent is observable

### Scenario 4: reject blank text values

- Given:
  - name or description is null, empty, or whitespace
- When:
  - product creation or update is attempted
- Then:
  - the aggregate rejects the operation
  - no invalid state is applied
  - no success domain event is recorded

### Scenario 5: reject negative price

- Given:
  - price is below zero
- When:
  - product creation or update is attempted
- Then:
  - the aggregate rejects the operation
  - no invalid state is applied
  - no success domain event is recorded

## Assertions

- aggregate field values
- invariant enforcement behavior
- domain event recording behavior

## Test Level

- Primary: `unit`
- Secondary: `application`

## Notes / Deferred Cases

- Exact hard-delete versus soft-delete persistence semantics should stay aligned with the application and repository contract.
