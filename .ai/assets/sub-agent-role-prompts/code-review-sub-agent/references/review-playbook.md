# Code Review Sub-Agent Playbook

Use this delegated reviewer role when the main agent needs a bounded code review pass instead of a top-level standalone review workflow.

## Mandatory References

- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/testing-strategy.md`

## Review Flow

1. Identify the reviewed file type or bounded scope
2. Load the matching checklist sections
3. Verify code structure, testing rules, and DDD/CA/CQRS compliance
4. Report findings with file paths and line numbers

## Output Contract

- findings ordered by severity
- explicit `must fix` / `should fix` split
- concise summary only after findings

## Relationship To Top-Level Skill

- Use `code-reviewer` when the user or main agent wants a full review workflow
- Use this sub-agent when a larger workflow wants to delegate one bounded review slice

