# Source-Independent Reconstruction Acceptance Test Spec

## Inputs Used

- `AC-001` through `AC-010` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/reconstruction/reconstruction-procedure.md`
- All manifests under `.dev/specs/reconstruction/`

## Implementation Status

- Status: `planned`
- This is the final destructive-copy acceptance oracle; it has not been executed in this workflow.

## Scenario Set

### Scenario 1: reconstruct twice without product source or hidden implementation evidence

- Test level: `end-to-end`
- Given: two independent disposable copies retain only the authorized reconstruction inputs and remove `src/`, `tests/`, `.git/`, `bin/`, `obj/`, code-knowledge caches, uncommitted artifacts, and conversation history.
- When: two fresh LUNA-class agents independently follow only the reconstruction entrypoint, record every question, and cannot read each other's prompts or outputs.
- Then: each recreates the 27-project graph, all 16 use cases, 15 HTTP endpoints, three database models including both source outboxes, and the canonical Kafka logical routes without reading original product source.

### Scenario 2: pass deterministic validation

- Test level: `end-to-end`
- Given: reconstruction is complete.
- When: restore, build, unit/application/integration tests, PostgreSQL migrations, and Kafka smoke tests run.
- Then: both attempts pass restore/build/default tests, opt-in PostgreSQL atomicity/failure-injection tests, Kafka connectivity and keyed-order smoke tests, and contract comparisons. RabbitMQ is tested only for its declared compatibility scope unless separately promoted; configuration alone never proves runtime behavior.

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

### Scenario 5: compare compatibility, not source similarity

- Test level: `end-to-end`
- Given: both reconstructions pass their own internal tests.
- When: the acceptance harness compares them with the normative HTTP, message, persistence, runtime, and failure contracts.
- Then: every external contract and hard reliability gate matches; internal class layout and algorithms may differ or improve.

## Assertion Notes

- Compare observable contracts and acceptance behavior, not line-by-line source similarity.
- Keep the two reconstruction workspaces isolated and archive their question logs plus validation evidence separately.
- Preserve the original repository; delete source only in a disposable copy after explicit authorization.

## Recommended Test Spec Path

`.dev/specs/tests/e2e/reconstruction-acceptance.test-spec.md`

## Implementation and Execution Handoff

The two clean-room exercises and any deletion of the original source each require separate authorization. Passing this specification never authorizes deletion by itself.
