# Reactor Mode

Use this mode when the slice implements one bounded reactor for event-driven consistency, projection updates, or integration reactions.

## Mandatory References

- `.dev/ARCHITECTURE.md`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/references/implementation-playbook.md`
- `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`

## Rules

- Use WolverineFx message handlers for reactor/event processing.
- Reactors work on event data, not live domain entities.
- Do not query another aggregate's write repository directly; use a read-only
  `IQueryRepository` port or an established QueryService when composition or policy
  requires one.
- Keep MQ-driven consistency, projection, and integration effects explicit.
- Keep validation notes explicit when tests or review are still pending.

## Expected Output

- bounded implementation for the target reactor;
- touched files or intended output paths;
- event-processing summary;
- validation notes;
- explicit follow-up handoff when test design, review, or architecture work remains.
