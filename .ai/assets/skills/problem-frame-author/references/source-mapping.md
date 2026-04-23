# Source Mapping

Map source materials into problem-frame files with these defaults.

## Requirement Files

Use for:

- business goal
- actor intent
- success criteria
- hard constraints
- business failure outcomes

## Spec Files

Use for:

- request and response fields
- main flow and alternate flow
- validation rules
- external integration behavior
- observable acceptance outcomes

## ADR / Architecture Files

Use for:

- repository constraints
- messaging boundaries
- persistence strategy
- error-handling expectations

## Code and Tests

Use only to:

- recover missing details
- confirm likely aggregate method names
- identify domain events
- infer current behavior and mismatches

When a fact comes only from code/tests, label it as inferred or observed rather than source-of-truth.
