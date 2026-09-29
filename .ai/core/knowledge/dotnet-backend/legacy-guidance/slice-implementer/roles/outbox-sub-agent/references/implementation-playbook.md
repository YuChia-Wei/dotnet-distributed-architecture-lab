# Outbox Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for Outbox Pattern implementation. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/common-rules.md`
- `../../../../../shared/architecture-config.md`

## Rules

- Persist events before publish
- Use the target repository's selected message-store adapter; when EF Core is
  selected, apply the EF Core tracking and asynchronous materialization rules
- Keep metadata for audit
- Configure outbox services in DI

## Output Structure

- `src/Infrastructure/Outbox/`
