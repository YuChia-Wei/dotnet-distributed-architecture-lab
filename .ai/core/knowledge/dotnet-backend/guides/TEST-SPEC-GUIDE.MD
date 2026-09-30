# Test Spec Guide

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

This optional guide describes a target-selected formal-test specification. Use the
target's requested artifact, adopted GWT rules, template and configurable document
root. Example `.dev/specs` paths are conventions, not required storage bindings.

When the target adopts this GWT profile, preserve Given-When-Then in test designs and C# tests rather than silently substituting 3A. BDDfy is the default tool. If the target team decides not to introduce BDDfy, plain xUnit tests must still preserve an explicit Given, When, and Then structure. `.feature` files are optional; see [GHERKIN-FEATURE-STORAGE-GUIDE.MD](GHERKIN-FEATURE-STORAGE-GUIDE.MD) for enablement conditions and official storage conventions.

## 1. When to Create a Test Spec

Create a test spec when:

- A new use case will use BDD or TDD development.
- A cross-bounded-context flow needs an explicit verification path.
- A use case has multiple business branches that should be separated into scenarios first.
- Acceptance criteria must be converted into a test design.

## 2. Order Relative to Production Specs

One possible order for an explicitly requested multi-artifact task (not a required
authoring pipeline):

1. `.dev/requirement/`
2. `.dev/specs/domains/`
3. `.dev/specs/tests/`
4. Test design and test implementation

Exceptions:

- With TDD, a test spec may be created nearly simultaneously with `.dev/specs/domains/`.
- A test spec must not replace a production spec because they capture different information.

## 3. Filename Recommendations

- `[use-case].test-spec.md`
- Examples:
  - `place-order.test-spec.md`
  - `decrease-stock.test-spec.md`
  - `ship-order.test-spec.md`

## 3.1 Directory Recommendations

Classify domain-local test specs by their test target:

- `.dev/specs/tests/<domain>/aggregate/<aggregate-name>.test-spec.md`
- `.dev/specs/tests/<domain>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<domain>/integration/<target-name>.test-spec.md`

The following categories are optional and should be created only when they have actual content:

- `.dev/specs/tests/<domain>/app-services/<service-name>.test-spec.md`
- `.dev/specs/tests/<domain>/domain-services/<service-name>.test-spec.md`

Do not force cross-bounded-context flows or complete journeys under a single domain:

- `.dev/specs/tests/cross-domain/<flow-name>.test-spec.md`
- `.dev/specs/tests/e2e/<journey-name>.test-spec.md`

When a requirement directly provides or explicitly requests a `.feature` file, or the target profile uses a Gherkin runner, place the corresponding official file under:

- `tests/Features/<domain>/<use-case>.feature`
- `tests/Features/cross-domain/<flow-name>.feature`
- `tests/Features/e2e/<journey-name>.feature`

## 4. Recommended Sections

```markdown
# <Use Case> Test Spec

## Scope

## Related Production Spec

## Scenario List

## Given-When-Then

## Assertions

## Test Level

## Notes / Deferred Cases
```

## 5. Scenario-Writing Rules

Every scenario must define at least:

- Given: Precondition state and test data
- When: The triggered use case, command, or event
- Then: Observable results

Then may include:

- Aggregate state
- Domain event
- Integration event
- Returned DTO or result
- Error or failure branch

## 6. Test-Level Labels

Record the primary verification level in each test spec:

- `unit`
- `application`
- `integration`
- `contract`
- `end-to-end`

Common mappings:

- `aggregate/` -> `unit` or `application`
- `use-cases/` -> `application`
- `integration/` -> `integration` or `contract`
- `cross-domain/` -> `integration` or `contract`
- `e2e/` -> `end-to-end`

A test spec may have primary and secondary levels, but it must identify one clear primary level.

## 7. Distributed-System Details

When a use case involves cross-bounded-context or MQ behavior, also record:

- Trigger event or command
- Expected integration contract
- Idempotency concerns
- Retry or duplicate-delivery concerns
- Eventual-consistency expectations

## 8. Relationship to Skills and Workflows

- The target-selected test-spec root is the documentation owner for test intent; `.dev/specs/tests/` is an example.
- `bdd-gwt-test-designer` can convert requirements or specs into scenarios in this area.
- `bdd-gwt-test-designer` should also return a recommended storage category such as `use-cases/`, `integration/`, or `cross-domain/`.
- Subsequent test generation or implementation creates a `.feature` file only when an enablement condition applies, and places it under `tests/Features/` rather than `.dev/specs/tests/`.
- `.dev/specs/tests/` should preserve assertion notes, coverage gaps, traceability information, and non-Gherkin supplementary details.

## 9. Minimum Definition of Done

A test spec must at least:

- Refer to the actual behavior authority: a requirement, accepted contract or production spec when available; retain missing sources as unresolved.
- Include at least one happy path.
- Include at least one failure path or edge case.
- Identify the primary verification level.
