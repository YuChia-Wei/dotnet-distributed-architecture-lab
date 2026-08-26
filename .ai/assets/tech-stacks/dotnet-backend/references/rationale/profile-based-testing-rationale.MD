# Profile-Based Testing Rationale

## Decision Pattern

Tests need to support multiple profiles, such as:

- InMemory
- Outbox / PostgreSQL integration

Profile selection should not be hard-coded in a base test class.

## Why

### 1. The Same Tests Should Validate Different Implementation Strategies

If the command side supports both in-memory and outbox strategies, tests should not be bound to only one environment.

### 2. Environment Selection Is a Runtime Concern

The profile used for a test run is fundamentally a configuration concern, not part of the test-class inheritance structure.

### 3. Avoid Turning BaseTestClass into Hidden Global State

Putting environment selection in a base class:

- increases hidden coupling;
- makes switching test modes difficult;
- creates inconsistent CI, local, and integration behavior.

## Why Not

### Hard-Coded Environment in a Base Test Class

Drawbacks:

- The execution command does not clearly show which profile is under test.
- The test base class exercises excessive control.
- Maintenance and extension become difficult.

## Practical Rule

- Determine the profile through environment variables and `appsettings.{Environment}.json`.
- Tests themselves must not set the global execution environment implicitly.
- The same test suite should be repeatable under multiple profiles.
