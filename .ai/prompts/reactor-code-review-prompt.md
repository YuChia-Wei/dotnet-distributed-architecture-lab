# Reactor Code Review Prompt (Dotnet)

Review reactor implementations for correctness.

## Rules
- Must handle correct event types
- Must not throw unhandled exceptions
- Must be registered via DI
- Must not use direct repository cross-aggregate queries
