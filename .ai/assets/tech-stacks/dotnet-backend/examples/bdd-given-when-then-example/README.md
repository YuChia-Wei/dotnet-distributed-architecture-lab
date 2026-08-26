# BDDfy Rule Examples (.NET)

This folder shows how to express business rules as BDDfy tests with Gherkin-style naming.

Key mapping:
- Business rule -> Rule prefix in test method names or grouped test classes
- Scenario -> Test method
- Given/When/Then -> BDDfy step methods or fluent chain

Use these examples to keep BDD tests readable and reusable in .NET.

## Contents

- `CompleteUseCaseRuleTests.cs`
  - Full-feature use case example with multiple rules (BDDfy).
- `rule-design-before-after.md`
  - Rule granularity guidance and examples.
- `rule-migration-guide.md`
  - Rule-style grouping guidance for BDDfy tests.
- `../outbox/OUTBOX-TEST-CONFIGURATION.md`
  - Outbox test configuration for .NET.
- `AggregateOutboxRepositoryTests.cs`
  - Standard Outbox repository integration scenarios (BDDfy).

## Rule Design Principles

1. Each Rule should represent one business rule or capability.
2. Group 3-5 scenarios under the same Rule when they share intent.
3. Use business language in Rule names, not technical terms.
4. Prefer shared helper methods for setup; avoid base test classes.
