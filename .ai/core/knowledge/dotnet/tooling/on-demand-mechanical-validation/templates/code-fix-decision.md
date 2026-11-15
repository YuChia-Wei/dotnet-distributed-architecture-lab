# Target-Owned Code-Fix Decision

Template status: `reference-only`. This file is target-owned after copy.

This framework does not supply, select, or claim an automated code fix. Record
one decision per selected diagnostic after the target has separately recorded
selection, readiness, compatibility, and test evidence.

## Decision Record

- Target diagnostic ID: `{{target-owned-diagnostic-id}}`
- Target decision: `{{declined | not-selected | selected-without-code-fix | selected-with-target-code-fix}}`
- Target owner and decision evidence: `{{target-owned-decision-evidence}}`
- False-positive and exception policy: `{{target-owned-exception-policy}}`
- Safe transformation boundary: `{{target-owned-safe-change-boundary}}`
- Rollback plan: `{{target-owned-rollback-plan}}`

## Required Evidence Before an Active Claim

- The target selection record identifies the diagnostic and scope.
- A fresh readiness receipt identifies the exact provider delivery selected by the target.
- A compatibility receipt covers the target compiler, framework, and analyzer API surface.
- Analyzer and code-fix tests use explicit Given / When / Then semantics.
- An execution receipt is retained only after the target runs its selected validation.

Until those records exist, keep the decision as `declined` or `not-selected`.
