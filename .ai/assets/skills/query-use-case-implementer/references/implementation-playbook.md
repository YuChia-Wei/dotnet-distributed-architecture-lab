# Query Use Case Implementer Playbook

Use this skill when the main task is to implement one bounded query-side use case, not to redesign read-model architecture from scratch.

## Mandatory References

- `.dev/ARCHITECTURE.MD`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/references/implementation-playbook.md`

## Rules

- Use WolverineFx query handlers
- Queries must not modify domain state
- Return DTOs, not domain entities
- Prefer projections or read-side storage patterns already established by the repo
- Keep filter normalization and client-facing state mapping explicit

## Expected Output

- bounded implementation for the target query use case
- touched files or intended output paths
- validation notes
- explicit follow-up handoff when test design, review, or architecture work remains
