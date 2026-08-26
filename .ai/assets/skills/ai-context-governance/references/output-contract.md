# Output Contract

## Inventory Output

Return:

1. `Evidence Used`
2. `Classification Summary`
3. `Boundary Hotspots`
4. `Recommended Actions`
5. `Deferred Items`

## Policy or Cleanup Output

Return:

1. `Docs Updated`
2. `Boundary Decisions`
3. `Validation`
4. `Next Task`

## Audit Remediation Lifecycle Output

Keep the baseline assessment immutable and produce separate lifecycle records:

1. `.dev/assessments/<baseline-assessment-id>/report.md` from `ai-context-auditor`;
2. `<artifact-root>/reports/remediation-report.md` from `ai-context-governance`;
3. `.dev/assessments/<verification-assessment-id>/report.md` from `ai-context-auditor`.

The remediation report must map every stable `<assessment-id>#<finding-id>` to `resolved`, `partially-resolved`, `deferred`, `not-addressed`, or `regressed`, and include changed files, validation, commit evidence when applicable, residual risk, and the independent verification assessment.

Do not claim lifecycle closure while any finding lacks an explicit outcome or while the required post-remediation audit is missing. A workflow may close with deferred findings only when the owner, reason, and next action are recorded.

## Skill Routing Output

When the main result is skill routing, include:

- skill to use;
- skills explicitly not used;
- reason for each boundary decision;
- files or indexes updated.
