# Reactor Code Review Prompt (Dotnet)

Review reactor implementations for correctness.

## Rules
- See `../assets/sub-agent-role-prompts/reactor-code-review-sub-agent/sub-agent.yaml` for the canonical delegated review role.
- Must handle correct event types
- Must not throw unhandled exceptions
- Must be registered via DI
- Must not use direct repository cross-aggregate queries
