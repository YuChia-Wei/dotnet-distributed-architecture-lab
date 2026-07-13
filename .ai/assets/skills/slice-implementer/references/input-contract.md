# Slice Implementer Input Contract

Before implementing, confirm these fields:

- `intent`: feature, bug-fix, review-remediation, validation-failure-remediation, behavior-correction, refactor, or cleanup.
- `scope`: one bounded implementation slice.
- `mode`: command, query, reactor, generic, remediation, or refactor.
- `source_truth`: requirement, spec, workflow task, review findings, or architecture decision.
- `non_goals`: work explicitly excluded from this slice.
- `validation`: tests, reference checks, build checks, or stated skipped validation.

If the slice boundary, aggregate boundary, dependency direction, or domain language is unclear, stop and hand off to `ddd-ca-hex-architect` or `dev-workflow`.
