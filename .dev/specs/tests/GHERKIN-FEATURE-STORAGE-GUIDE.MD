# Gherkin Feature Storage Guide

This conditional-enablement guide defines the official storage conventions for a target project that decides to create or maintain Gherkin `.feature` files. It does not require every project to create `.feature` files.

## 0. Enablement Conditions

Create or maintain `.feature` files only when at least one of the following conditions applies:

- The user or requirement directly provides a `.feature` file.
- The user explicitly requests the design or generation of a `.feature` file.
- The target profile or team has adopted Reqnroll or another Gherkin runner.

When none of these conditions applies, do not proactively create `.feature` files, step definitions, or runner integration. Regardless of whether `.feature` support is enabled, every C# test must use Given-When-Then and must not substitute Arrange-Act-Assert (3A). BDDfy is the default tool, but the target team may explicitly opt out.

## 1. Purpose

A target project with `.feature` support enabled has two types of test artifacts:

- `.dev/specs/tests/`
  - Test intent, scenario design, assertion notes, coverage gaps, and traceability information
- `tests/Features/`
  - Officially maintained Gherkin `.feature` files that IDE and BDD tools can use directly

This separation aims to:

- Keep `.feature` files close to test code and step definitions for better IDE integration and long-term maintenance.
- Preserve `.dev/specs/tests/` as the test-intent and specification-traceability area.
- Avoid treating the specification-document area as the executable test-asset area.

## 2. Official Convention

Once enabled, place every official `.feature` file under:

```text
tests/Features/
```

Do not place official `.feature` files under:

- `.dev/specs/tests/`
- `.dev/standards/examples/`
- Any domain source-project directory

## 3. Directory Structure

### Domain-Local

```text
tests/Features/<domain>/<use-case>.feature
```

Examples:

- `tests/Features/order/place-order.feature`
- `tests/Features/product/create-product.feature`
- `tests/Features/inventory-item/decrease-stock.feature`

### Cross-Domain

```text
tests/Features/cross-domain/<flow-name>.feature
```

Example:

- `tests/Features/cross-domain/place-order-and-reserve-stock.feature`

### End-to-End

```text
tests/Features/e2e/<journey-name>.feature
```

Example:

- `tests/Features/e2e/customer-places-order.feature`

## 4. Naming Rules

- Use kebab-case filenames.
- Prefer a use-case or flow name over an ambiguous technical name.
- Keep each `.feature` file focused on one primary use case, cross-domain flow, or complete journey.

Recommended:

- `place-order.feature`
- `cancel-order.feature`
- `product-outbox-publication.feature`

Avoid:

- `OrderTests.feature`
- `Misc.feature`
- `Scenario1.feature`

## 5. Responsibility Split with `.dev/specs/tests/`

### A `.feature` File Should Contain

- Readable Gherkin flows using Feature, Rule, and Scenario
- Happy paths, failure paths, and edge cases
- Externally observable Given, When, and Then steps

### `.dev/specs/tests/*.test-spec.md` Should Contain

- Related production spec
- Assertion notes
- Setup and fixture notes
- Test level
- Supplementary event, message, and persistence verification
- Coverage gaps
- Deferred cases
- The corresponding `.feature` path

Simple decision rule:

- If the goal is for people or tools to read or execute a BDD scenario directly, place it under `tests/Features/`.
- If the goal is to preserve test-design context and supplementary specification details, place it under `.dev/specs/tests/`.

## 6. Step Definitions and Test Code

Place step definitions in a test project and maintain a clear mapping to the corresponding `.feature` files.

Recommended:

```text
tests/<TargetProject>.Tests/Steps/
tests/<TargetProject>.Tests/Fixtures/
tests/<TargetProject>.Tests/Support/
```

A project with a centralized BDD test project may instead use:

```text
tests/Features/Steps/
tests/Features/Support/
```

Principles:

- Keep `.feature` files close to test assets.
- Do not place step definitions under `.dev/`.
- Do not mix fixture or support code with specification documents.

## 7. Relationship to Skills and Workflows

By default, `bdd-gwt-test-designer` produces scenario designs and test-spec information without assuming that `.feature` files are required. When an enablement condition applies and the design must become official Gherkin:

1. Use `.dev/specs/domains/` as the source of truth for production behavior.
2. Capture scenario designs and assertion notes under `.dev/specs/tests/`.
3. Place executable Gherkin under `tests/Features/`.
4. Record the corresponding `.feature` path in the test spec.

## 8. Existing Examples

Files under `.dev/standards/examples/**/.feature` are examples only and are not an official storage location.

After `.feature` support is enabled, place every newly created or actively maintained file under `tests/Features/` according to this guide.
