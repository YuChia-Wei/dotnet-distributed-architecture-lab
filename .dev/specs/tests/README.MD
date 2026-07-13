# Test Specs

This directory contains BDD, TDD, and acceptance-oriented test specification documents.

Given-When-Then is the minimum standard for every test design and C# test; Arrange-Act-Assert (3A) must not replace it. BDDfy is the default tool, but the target team may explicitly opt out of the package while retaining the GWT structure. `.feature` is a planned, optional asset that is enabled only when a requirement directly provides one, the user explicitly requests its design or generation, or the target profile adopts a runner.

## Purpose

- Preserve what must be verified rather than how to implement it.
- Provide a stable location for BDD, TDD, Given-When-Then, and scenario design.
- Avoid mixing test intent into production-facing specs or workflow tasks.

## Responsibility Split within `.dev/specs/`

- `.dev/specs/domains/`
  - Describes production behavior, aggregates, use cases, and adapter contracts.
- `.dev/specs/tests/`
  - Describes test scenarios, verification targets, preconditions, boundary conditions, and red-green-refactor slices.
- `tests/Features/` (conditional)
  - When `.feature` support is enabled, contains officially maintained Gherkin files integrated with IDE and BDD tools.
- `tests/**/*.Steps.cs`
  - Contains step definitions and test-support code corresponding to `.feature` files.

Simple decision rule:

- If the document answers "What should the system do?", place it under `.dev/specs/domains/`.
- If the document answers "How will I verify that it did so?", place it under `.dev/specs/tests/`.

## Recommended Structure

```text
.dev/specs/tests/
  README.MD
  GHERKIN-FEATURE-STORAGE-GUIDE.MD
  TEST-SPEC-GUIDE.MD
  <domain>/
    aggregate/
      <aggregate-name>.test-spec.md
    app-services/
      <service-name>.test-spec.md
    domain-services/
      <service-name>.test-spec.md
    integration/
      <target-name>.test-spec.md
    use-cases/
      <use-case>.test-spec.md
  cross-domain/
    <flow-name>.test-spec.md
  e2e/
    <journey-name>.test-spec.md

tests/
  Features/
    <domain>/
      <use-case>.feature
    cross-domain/
      <flow-name>.feature
    e2e/
      <journey-name>.feature
```

## Directory Classification Principles

- `aggregate/`
  - Verifies aggregate invariants, state transitions, and domain events.
- `app-services/`
  - Verifies application-service orchestration. It may remain unused when the repository primarily uses use-case handlers.
- `domain-services/`
  - Verifies domain-service decision logic. Use it only when an independent domain service actually exists.
- `integration/`
  - Verifies repository and database behavior, MQ contracts, consumers and producers, and external gateways.
- `use-cases/`
  - Verifies command or query handling, input and output, and collaboration logic.
- `cross-domain/`
  - Verifies flows across bounded contexts that do not belong to one domain.
- `e2e/`
  - Verifies a complete journey, such as an end-to-end path from UI or API to MQ or database.

## Classification Decision Order

First ask which layer is the primary verification target:

- Business invariant -> `aggregate/`
- Command or query flow -> `use-cases/`
- Database, MQ, or external adapter -> `integration/`
- Multiple domains -> `cross-domain/`
- Complete user journey -> `e2e/`

`app-services/` and `domain-services/` are reserved categories and do not need to be enabled initially.

## Suitable Content

- Given-When-Then scenarios
- Acceptance-criteria-to-assertion maps
- Red, green, and refactor test slices
- Edge cases and failure scenarios
- Test-level recommendations (`unit`, `integration`, `contract`, or `end-to-end`)
- Traceability and mapping for `.feature` files, plus supplementary details not expressed in Gherkin

## Unsuitable Content

- Implementation code
- Concrete repository implementation details
- Scratch notes used temporarily by an agent
- Production-behavior specifications that replace `.dev/specs/`
- Official enabled `.feature` files placed directly here; official Gherkin belongs under `tests/Features/`
