# Command Use Case Mode

Use this mode when the slice implements one bounded command-side use case.

## Mandatory References

- `.dev/ARCHITECTURE.md`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/command-sub-agent/references/implementation-playbook.md`
- `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`

## Rules

- Implement an explicit Use Case interface and `*UseCase` implementation with
  `ExecuteAsync` and a non-optional `CancellationToken`.
- Use a dedicated transport-neutral input except for the approved no-input and
  single scalar built-in/BCL exceptions.
- Add a Command Handler only for an actual dispatch/message entry; keep Wolverine
  conditional and outside the portable Use Case.
- Commands may change aggregate state.
- Keep aggregate boundary and command responsibility explicit.
- Keep repository access aligned with the current DI model.
- Use `IAggregateRepository<TAggregate, TId>` (or the documented
  `IDomainRepository` compatibility alias) for Aggregate Root persistence.
- Do not add generic writable CRUD, query methods, or bulk convenience methods to
  the aggregate repository contract.
- Follow the active storage profile and architecture configuration.
- Keep validation notes explicit when tests or review are still pending.
- Use a project-owned outbound event publisher port; do not inject `IMessageBus`
  or another Use Case.

## Expected Output

- bounded implementation for the target command use case;
- touched files or intended output paths;
- validation notes;
- explicit follow-up handoff when test design, review, or architecture work remains.
