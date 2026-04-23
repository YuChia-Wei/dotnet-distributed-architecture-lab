# Command Use Case Implementer Playbook

Use this skill when the main task is to implement one bounded command-side use case, not to redesign the architecture.

## Mandatory References

- `.dev/ARCHITECTURE.MD`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/command-sub-agent/references/implementation-playbook.md`

## Rules

- Use WolverineFx command handlers
- Keep repository access aligned with the current DI model
- Do not add custom repository interfaces for write-side flows
- Follow the active storage profile and architecture configuration already chosen by the repo
- Keep validation notes explicit when tests or review are still pending

## Expected Output

- bounded implementation for the target command use case
- touched files or intended output paths
- validation notes
- explicit follow-up handoff when test design, review, or architecture work remains
