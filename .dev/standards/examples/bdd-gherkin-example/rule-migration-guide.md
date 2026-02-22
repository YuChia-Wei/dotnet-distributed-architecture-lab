# Rule Migration Guide (ezSpec -> Gherkin)

This guide migrates ezSpec Rule usage into Gherkin `Rule:` blocks.

## Migration Steps

### 1. Analyze Existing Scenarios
Group scenarios by business intent.

### 2. Define Rules as Gherkin Blocks
```gherkin
Rule: Successful operations
Rule: Input validation
Rule: Authorization checks
```

### 3. Move Scenarios Under Each Rule
```gherkin
Rule: Input validation
  Scenario: Reject empty name
  Scenario: Reject null owner
```

### 4. Use Background for Shared Setup
```gherkin
Background:
  Given a valid user
```

## Example

Before:
```gherkin
Feature: Create Order
  Scenario: create order successfully
  Scenario: reject duplicate order number
  Scenario: reject empty customer id
  Scenario: reject negative amount
```

After:
```gherkin
Feature: Create Order
  Rule: Successful creation
    Scenario: create order successfully

  Rule: Input validation
    Scenario: reject empty customer id
    Scenario: reject negative amount

  Rule: Duplicate validation
    Scenario: reject duplicate order number
```

## Checklist

- [ ] Group scenarios by business intent
- [ ] Create Rule blocks with meaningful names
- [ ] Use Background for shared setup
- [ ] Verify Rule grouping in test reports
