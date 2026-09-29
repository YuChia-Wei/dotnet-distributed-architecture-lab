# Profile Config Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for environment profile configuration. Loading this material does not dispatch a worker.

## Rules

- No hardcoded profile in tests
- Use environment variables with `appsettings.{Environment}.json`
- DI registration depends on environment

## Output Focus

- profile wiring
- environment-specific configuration
- DI registration boundaries
