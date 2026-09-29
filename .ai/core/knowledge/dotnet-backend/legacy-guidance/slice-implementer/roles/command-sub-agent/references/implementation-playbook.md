# Command Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for command-side use case implementation. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/common-rules.md`
- `../../../../../shared/architecture-config.md`
- `../../../../../shared/testing-strategy.md`

## Rules

- Implement `I<Operation>UseCase` and `<Operation>UseCase` with `ExecuteAsync`.
- Use a dedicated transport-neutral input except for no-input or one scalar
  built-in/BCL input.
- Include a non-optional `CancellationToken`.
- Return only the transport-neutral output produced by the operation; use `Task`
  when there is no output.
- Add a Command Handler only when an actual dispatch/message entry exists; it maps
  the Command and invokes one Use Case.
- Keep Wolverine conditional and out of the portable Use Case.
- Repository dependencies come from DI; use `IAggregateRepository` for Aggregate
  Root writes and do not add generic writable CRUD or query methods to it
- Tests use mandatory Given-When-Then structure and naming with no `BaseTestClass`; BDDfy is the default unless the target team explicitly opted out, and 3A is not a substitute

## Output Structure

- `src/Application/UseCases/<Operation>/`
