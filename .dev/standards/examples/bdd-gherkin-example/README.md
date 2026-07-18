# Gherkin Rule Examples (ezSpec -> .NET)

This folder translates ezSpec Rule concepts into Gherkin `Rule:` blocks using Reqnroll.

Key mapping:
- ezSpec `Rule` -> Gherkin `Rule:` section
- ezSpec `Scenario` -> Gherkin `Scenario`
- ezSpec `Given/When/Then` -> Gherkin steps

Use these examples to keep BDD tests readable and reusable in .NET.

## Contents

- `complete-usecase-with-rules.feature`
  - Full-feature Use Case scenario example. Target-owned bindings are required.
- `create-task-usecase.feature`
  - Domain-oriented Use Case scenarios retained without placeholder step bindings.
- `rule-design-before-after.md`
  - Rule granularity guidance and examples.
- `rule-migration-guide.md`
  - Step-by-step migration guide from ezSpec to Gherkin Rule blocks.
- `../outbox/OUTBOX-TEST-CONFIGURATION.md`
  - Shared Outbox test configuration for both BDD modes.
- `aggregate-outbox-repository.feature`
  - Standard Outbox repository integration scenarios without placeholder bindings.

## Rule Design Principles

1. Each Rule should represent one business rule or capability.
2. Group 3-5 scenarios under the same Rule when they share intent.
3. Use business language in Rule names, not technical terms.
4. Prefer `Background` for shared setup, not repeated steps.
