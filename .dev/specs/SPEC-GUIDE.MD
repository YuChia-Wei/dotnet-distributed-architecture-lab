# Spec Guide

This document defines the format and authoring conventions for specifications under `.dev/specs/` and incorporates the organization rules from `SPEC-ORGANIZATION-GUIDE.md`.

In this framework repository, `.dev/specs/` currently retains only:

- `README.MD`
  - folder purpose, scope, and usage
- `SPEC-GUIDE.MD`
- `SPEC-ORGANIZATION-GUIDE.MD`
- `tests/`
  - BDD/TDD-oriented test specs and scenario design artifacts

Production/domain specs are target-repository outputs created by `repo-structure-sync` or a later workflow when source requirements exist; they are not an active subtree in this framework repository.

## 0) Terminology Boundary

- `use case`
  - the primary name of production behavior, such as `CreateProduct`
- `command` / `query`
  - the request model for that use case
- `handler`
  - the application executor in code

Specs should primarily describe:

- the use case the system must complete
- the corresponding aggregate/domain event/repository/output

They should not begin with implementation types such as:

- `CreateProductCommandHandler`
- `CreateProductUseCaseService`

In other words:

- `use case` is the subject of the spec
- `command`/`query` and `handler` are implementation mappings and do not need to become the primary spec filename

See the complete terminology rules in [`../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD).

## 1) Directory & Naming Rules
First follow:
- `SPEC-ORGANIZATION-GUIDE.MD`
- Aggregate as the smallest boundary

In a target repository, production specs conventionally live under:

- `.dev/specs/domains/<domain>/<entity|usecase|adapter>/...`

In this framework repository, however, `.dev/specs/domains/` is not used as a ready-made source-of-truth directory.

Test specs should live under:

- `.dev/specs/tests/<domain>/aggregate/<aggregate-name>.test-spec.md`
- `.dev/specs/tests/<domain>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<domain>/integration/<target-name>.test-spec.md`
- Add when needed: `.dev/specs/tests/<domain>/app-services/` and `.dev/specs/tests/<domain>/domain-services/`
- Cross-domain flows: `.dev/specs/tests/cross-domain/<flow-name>.test-spec.md`
- End-to-end journeys: `.dev/specs/tests/e2e/<journey-name>.test-spec.md`

### Use Case Spec
- Filename format: `[action]-[aggregate].json`
- Examples: `create-product.json`, `estimate-pbi.json`

### Entity / Value Object Spec
- Filename format: `[aggregate]-spec.md` or `*-spec.json`

### Adapter / Controller Spec
- Filename format: `[action]-[aggregate]-controller.json`

## 2) Use Case Spec (JSON)
### Required Keys
- `useCase`
- `behavior`
- `input`
- `aggregate`
- `aggregateId`
- `method`
- `domainEvent`
- `repository`
- `output`

### Interpretation Rules

- `useCase`
  - the business operation name, not a class name
- `input`
  - the data shape of the corresponding command/query request model
- `method`
  - an aggregate constructor, aggregate method, or other primary domain entry point
- `repository`
  - command-side aggregate persistence or the primary query-side data-access collaborator
- `output`
  - the result DTO or output model returned when the handler/use case completes

### Optional / Recommended Keys
- `domainModelNotes`
- `constructorPreconditions`
- `constructorPostconditions`
- `aggregates`
- `domainEvents`
- `entities`
- `valueObjects`
- `enums`

### Example (minimal)
```json
{
  "useCase": "CreateProduct",
  "behavior": "Create a new product",
  "input": [{ "name": "productId", "type": "String" }],
  "aggregate": "Product",
  "aggregateId": "ProductId",
  "method": "Product constructor",
  "domainEvent": "ProductEvents.ProductCreated",
  "repository": "ProductRepository",
  "output": "CqrsOutput with productId"
}
```

## 3) Adapter / Controller Spec (JSON)
### Required Keys
- `useCase`
- `behavior`
- `spec.basePath`
- `spec.endpoints`

### Recommended
- `spec.errorMapping`
- `contracts.dtos`
- `policies.validation`
- `policies.idempotency`
- `policies.observability`

### Example (minimal)
```json
{
  "useCase": "CreateProductController",
  "behavior": "Create a new product",
  "spec": {
    "basePath": "/v1/api/products",
    "endpoints": [
      { "method": "POST", "path": "", "summary": "Create Product" }
    ]
  }
}
```

## 4) Entity / Value Object Spec (JSON)
### Required Keys
- `entity`
- `type`
- `package`
- `description`
- `attributes`

### Example (from Hours)
```json
{
  "entity": "Hours",
  "type": "ValueObject",
  "package": "tw.teddysoft.aiscrum.common.entity",
  "description": "A value object representing hours with decimal calculations",
  "attributes": [
    { "name": "value", "type": "BigDecimal", "constraint": "nullable, >= 0, <= 99999" }
  ]
}
```

## 5) Cross References
Every spec must reference:
- the corresponding Aggregate
- related Domain Events
- related Use Cases/Controllers

## 6) Review Checklist
- Is the file in the correct Aggregate directory?
- Do the Use Case/Adapter/Entity structures conform to the JSON format?
- Are all required fields present?
- Does it map to actual code naming?

## 7) Boundary with Test Specs

- Production/domain specs (when created in a target repository) answer "What should the system do?"
- `.dev/specs/tests/` answers "How do I verify that it actually does so?"
- Test specs must not replace production specs.
- Test specs should primarily be classified by test target instead of placing every scenario directly under `<domain>/`.
- This framework repository retains only rules, templates, and test-spec materials; it does not retain an active production/domain spec subtree.
