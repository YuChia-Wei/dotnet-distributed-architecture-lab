# Profile Config Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on environment profile configuration.

## Rules

- No hardcoded profile in tests
- Use environment variables with `appsettings.{Environment}.json`
- DI registration depends on environment

## Output Focus

- profile wiring
- environment-specific configuration
- DI registration boundaries
