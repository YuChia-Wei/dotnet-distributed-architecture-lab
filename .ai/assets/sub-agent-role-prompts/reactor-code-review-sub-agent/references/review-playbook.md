# Reactor Code Review Sub-Agent Playbook

Use this delegated reviewer role when the main agent needs a bounded review of reactor/event-handler behavior and integration correctness.

## Mandatory References

- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/testing-strategy.md`

## Focus Areas

- correct event-type handling
- DI registration and lifecycle expectations
- unhandled exception risks
- forbidden cross-aggregate repository access

## Must-Fail Patterns

- wrong or incomplete event subscriptions
- missing DI registration
- unhandled exceptions in event handlers
- direct cross-aggregate repository reads that violate boundaries

## Relationship To Top-Level Skill

- Use `code-reviewer` for a full review workflow and final reporting
- Use this sub-agent when a larger workflow needs one reactor-specific review slice

