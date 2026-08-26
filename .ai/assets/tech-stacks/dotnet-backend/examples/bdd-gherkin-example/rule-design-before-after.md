# Gherkin Rule Design: Before and After

## Before: Rules Too Fine-Grained

```gherkin
Rule: Plan creation with valid ID, name, and user
Rule: Plan ID must be unique within the system
Rule: Plan name is required and cannot be empty
Rule: Plan ID must be a valid non-empty string
Rule: A user can own multiple plans with different IDs
Rule: Different users can create plans with the same name
```

Result:
- Many Rules with 1 scenario each
- Hard to navigate and maintain

## After: Rules with Meaningful Scope

```gherkin
Rule: Plan must have a valid and unique identifier
Rule: Plan must have valid name and owner information
Rule: Users can own and manage multiple plans
```

Result:
- 3 Rules with 3-5 scenarios each
- Scenarios grouped by business intent

## Why This Is Better

1. Related scenarios are grouped under the same business rule.
2. Each Rule includes positive, negative, and edge cases.
3. Rule names are business-readable (not technical).

## Rule Granularity Checklist

- Does the Rule represent a single business concept?
- Does it group 3-5 related scenarios?
- Are Rule names phrased in business language?

## Example Refactor (Tag Creation)

Before:
```gherkin
Rule: A tag can be created with valid ID, name, color, and plan
Rule: Tag color must be a valid HEX format
```

After:
```gherkin
Rule: Tag must have valid properties and belong to a plan
```

Scenarios under the Rule:
- create_a_tag_successfully
- create_tag_with_invalid_color_format
- create_tag_with_null_name
- create_tag_with_empty_name
- create_multiple_tags_for_same_plan
