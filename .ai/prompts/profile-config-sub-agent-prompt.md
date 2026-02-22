# Profile Config Sub-Agent Prompt (Dotnet)

Configure environment profiles using appsettings.

## Rules
- No hardcoded profile in tests
- Use environment variables + appsettings.{Environment}.json
- DI registration depends on environment
