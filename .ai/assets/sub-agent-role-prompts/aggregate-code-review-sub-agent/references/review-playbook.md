# Aggregate Code Review Sub-Agent Playbook

Use this delegated reviewer role when the main agent needs an aggregate-focused review instead of a general review pass.

## Mandatory References

- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/testing-strategy.md`

## Focus Areas

- aggregate boundary and invariant correctness
- event sourcing state mutation rules
- domain event metadata and serialization expectations
- aggregate-level test discipline

## Must-Fail Patterns

- direct state mutation in constructors
- missing event metadata or broken event immutability
- contract misuse across aggregate/entity/value-object boundaries
- aggregate tests that violate pure unit-test expectations

## Relationship To Top-Level Skill

- Use `code-reviewer` for a full review workflow and final reporting
- Use this sub-agent when a larger workflow wants one specialized aggregate review slice

