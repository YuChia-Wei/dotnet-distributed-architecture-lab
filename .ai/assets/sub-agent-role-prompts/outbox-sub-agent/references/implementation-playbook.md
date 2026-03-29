# Outbox Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on Outbox Pattern implementation.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/architecture-config.md`

## Rules

- Persist events before publish
- Use EF Core for the message store
- Keep metadata for audit
- Configure outbox services in DI

## Output Structure

- `src/Infrastructure/Outbox/`

