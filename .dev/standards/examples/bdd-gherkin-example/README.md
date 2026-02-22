# Gherkin Rule Examples (ezSpec -> .NET)

This folder translates ezSpec Rule concepts into Gherkin `Rule:` blocks using Reqnroll.

Key mapping:
- ezSpec `Rule` -> Gherkin `Rule:` section
- ezSpec `Scenario` -> Gherkin `Scenario`
- ezSpec `Given/When/Then` -> Gherkin steps

Use these examples to keep BDD tests readable and reusable in .NET.

## Contents

- `complete-usecase-with-rules.feature` + `CompleteUseCaseSteps.cs`
  - Full-feature use case example with multiple rules.
- `rule-design-before-after.md`
  - Rule granularity guidance and examples.
- `rule-migration-guide.md`
  - Step-by-step migration guide from ezSpec to Gherkin Rule blocks.
- `OUTBOX-TEST-CONFIGURATION.md`
  - Outbox test configuration for .NET.
- `product-outbox-repository.feature` + `ProductOutboxRepositorySteps.cs`
  - Standard Outbox repository integration scenarios.

## Rule Design Principles

1. Each Rule should represent one business rule or capability.
2. Group 3-5 scenarios under the same Rule when they share intent.
3. Use business language in Rule names, not technical terms.
4. Prefer `Background` for shared setup, not repeated steps.
