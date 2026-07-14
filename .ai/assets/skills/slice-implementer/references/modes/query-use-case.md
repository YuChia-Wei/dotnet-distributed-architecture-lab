# Query Use Case Mode

Use this mode when the slice implements one bounded query-side use case.

## Mandatory References

- `.dev/ARCHITECTURE.md`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/references/implementation-playbook.md`
- `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`

## Rules

- Implement an explicit query Use Case interface and `*UseCase` implementation
  with `ExecuteAsync` and a non-optional `CancellationToken`.
- Add a query Handler only when an actual dispatch entry exists; keep Wolverine
  conditional.
- Queries must not modify domain state.
- Return DTOs, not domain entities.
- Prefer projections or read-side storage patterns already established by the repo.
- Keep read model shape, filter normalization, and client-facing state mapping explicit.
- Default Controllers to the query Use Case. Direct Query Repository/Service
  access is only for an explicitly selected pure-query endpoint.

## Expected Output

- bounded implementation for the target query use case;
- touched files or intended output paths;
- DTO/read-model notes;
- validation notes;
- explicit follow-up handoff when test design, review, or architecture work remains.
