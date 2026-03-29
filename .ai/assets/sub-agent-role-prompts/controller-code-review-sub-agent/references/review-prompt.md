# Controller Code Review Prompt (Dotnet)

Review controllers for thinness, correct DTO mapping, and HTTP semantics.

## Rules
- See `../assets/sub-agent-role-prompts/controller-code-review-sub-agent/sub-agent.yaml` for the canonical delegated review role.
- No business logic in controllers
- DTOs are separate files
- Input validation applied
- Tests must pass
