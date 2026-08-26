# Source-Independent Reconstruction Acceptance Test Spec

## Inputs Used

- `AC-001` through `AC-010` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/reconstruction/reconstruction-procedure.md`
- All manifests under `.dev/specs/reconstruction/`

## Implementation Status

- Status: `planned`
- This is the final destructive-copy acceptance oracle; it has not been executed in this workflow.

## Scenario Set

### Scenario 1: reconstruct without product source

- Test level: `end-to-end`
- Given: a disposable clone retains governance, requirements, specs, ADRs, operations docs, solution identity, and fixtures but removes `src/` and `tests/`.
- When: a fresh LUNA-class agent follows only the reconstruction entrypoint and records every question.
- Then: it recreates the 26-project graph, all 16 use cases, 15 HTTP endpoints, three persistence models, and the Kafka/RabbitMQ logical routes without reading original product source.

### Scenario 2: pass deterministic validation

- Test level: `end-to-end`
- Given: reconstruction is complete.
- When: restore, build, unit/application/integration tests, PostgreSQL migrations, and Kafka smoke tests run.
- Then: required gates pass; RabbitMQ is either proven by a trusted run or remains explicitly blocked, never inferred from configuration.

### Scenario 3: meet quality-uplift decisions

- Test level: `end-to-end`
- Given: the reconstruction agent encounters a behavior labeled `quality-uplift`.
- When: it implements the specified target contract.
- Then: positive quantity invariants, shared messaging configuration, typed HTTP errors, and independent Inventory tests are present even if the old source lacked them.

### Scenario 4: bound ambiguity

- Test level: `end-to-end`
- Given: the reconstruction attempt is complete.
- When: its question log is classified.
- Then: no unanswered question changes a bounded-context boundary, aggregate invariant, public contract, transaction boundary, or deployment profile; unresolved owner choices remain listed as decisions rather than guesses.

## Assertion Notes

- Compare observable contracts and acceptance behavior, not line-by-line source similarity.
- Preserve the original repository; delete source only in a disposable copy after explicit authorization.

## Recommended Test Spec Path

`.dev/specs/tests/e2e/reconstruction-acceptance.test-spec.md`

## Implementation and Execution Handoff

The destructive-copy reconstruction exercise requires separate authorization and is not executed by this documentation workflow.
