# Code Reviewer Role Execution

For every review-role binding considered, `code-reviewer` produces the
provider-neutral `role_execution` record defined by
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`. Bindings prove static reachability, not that a
reviewer ran; the record supplies runtime evidence without transferring review
judgment or finding ownership to the orchestrator.

The canonical route selector is
`.ai/assets/skills/code-reviewer/references/review-routing.yaml`. The role
manifest's static references are execution scaffolding. After route selection,
record the selected route IDs and canonical standards under
`input_envelope.source_refs`; do not add unselected standards or compatibility
entries. A multi-file scope may select multiple routes, but references are
de-duplicated before review.

When a #114 `loaded_rule_ids` packet is relevant, cite it only as an opaque
`input_envelope.source_refs` entry. This skill does not create, resolve, or
modify its provider or effective-state semantics.

## Record And Selection

Evaluate each binding against the actual reviewed scope. A nonmatching binding
uses `applicability.result: does-not-apply`,
`selection.disposition: not-applicable`, and
`selection.delegation_evaluation: null`. For a matching binding, retain the
binding `role_asset_id` and exact `role_path`; load that manifest plus every
reference it declares. List those static references under
`input_envelope.mandatory_references` and its stop conditions under
`input_envelope.stop_conditions`. Those are the bounded stage's explicit stop
conditions. Populate the bounded reviewed scope,
selected-route source references, constraints, actual permissions, expected and
returned review output, and the parent in `final_integration_owner`.

Applicable roles default to `direct`. Record
`selection.delegation_evaluation` and allow `delegated` only when all of these
are true: `applicable_role`, `current_session_runtime_support_verified`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
and `named_parent_and_final_integration_owner`; at least one
`material_value_triggers` value is present; and
`cost_failure_retry_risk.result: supports-delegation`. A no-delegation runtime
performs the same review checklist and role workflow inline as `parent-inline`,
records `direct`, and sets `invocation_evidence: null` whenever inline parity
is satisfiable. Its child-runtime safety gate is false; parent inline support
is proved by the executor instead.

Use `unavailable` only when a mandatory model, tool, permission, or isolation
requirement cannot be met inline or through an eligible worker. A delegated
attempt requires genuine non-empty structured invocation evidence; its findings
remain input for this skill's own classification, severity, and final review
result.

## Attempts, Fallback, And Aggregation

When execution occurs, record attempts in the same record with their own
disposition, executor, and invocation evidence. Attempt 2 is permitted only
for a correctable first failure after a material state change; attempt 3 or
later requires fresh owner or workflow authorization. Not-applicable and
unavailable-before-execution use null top-level executor/invocation evidence
and empty attempts. Only a failed delegated attempt can consider direct
fallback. It must set every
`fallback.inline_contract_evidence` boolean true:
`same_role_path_and_mandatory_references`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
`named_parent_and_final_integration_owner`, and
`current_inline_support_verified`; otherwise the result is `unavailable`.
Never synthesize child evidence for direct, unavailable, or not-applicable
paths.

Hand the complete record to `software-development-orchestrator` unchanged for
stage aggregation. The orchestrator may verify disposition and evidence bounds,
but it neither replaces this review's findings nor authorizes remediation.
