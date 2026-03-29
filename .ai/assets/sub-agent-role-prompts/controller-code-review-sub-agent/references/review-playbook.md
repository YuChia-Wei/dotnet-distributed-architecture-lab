# Controller Code Review Sub-Agent Playbook

Use this delegated reviewer role when the main agent needs a bounded review of ASP.NET Core controllers and HTTP boundary behavior.

## Mandatory References

- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/testing-strategy.md`

## Focus Areas

- thin controller boundary
- DTO mapping and separation
- HTTP status semantics
- input validation

## Must-Fail Patterns

- business logic inside controllers
- DTOs embedded as inner classes
- missing or misleading HTTP status semantics
- missing validation at the boundary when required

## Relationship To Top-Level Skill

- Use `code-reviewer` for a full review workflow and final reporting
- Use this sub-agent when a larger workflow needs one controller-specific review slice

