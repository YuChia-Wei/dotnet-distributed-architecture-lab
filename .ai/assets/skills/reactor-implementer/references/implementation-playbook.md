# Reactor Implementer Playbook

Use this skill when the main task is to implement one bounded reactor for event-driven consistency or projection updates, not to redesign the cross-context architecture.

## Mandatory References

- `.dev/ARCHITECTURE.MD`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/references/implementation-playbook.md`

## Rules

- Use WolverineFx message handlers for reactor/event processing
- Reactors work on event data, not live domain entities
- Do not query another aggregate repository directly; use query services or established projection paths
- Keep MQ-driven consistency and integration effects explicit
- Keep validation notes explicit when tests or review are still pending

## Expected Output

- bounded implementation for the target reactor
- touched files or intended output paths
- validation notes
- explicit follow-up handoff when test design, review, or architecture work remains
