# AI Context Init Role Execution

`ai-context-init` owns the provider-neutral `role_execution` record for its
conditional `context-translator` binding. Use the exact record shape in
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; the binding establishes static reachability,
not a translation invocation or completion claim.

When a #114 `loaded_rule_ids` packet is relevant, cite it only as an opaque
`input_envelope.source_refs` entry. This skill does not resolve or redefine its
provider or effective-state semantics.

## Applicability And Loaded Stage

The translator applies only when a derived Traditional Chinese translation is
requested, its English source is final, and the bounded source/output paths are
known. Otherwise record `applicability.result: does-not-apply`,
`selection.disposition: not-applicable`, and
`selection.delegation_evaluation: null`. On a match, retain the binding
`role_asset_id` and exact `role_path`; load the `context-translator` manifest
and every reference it declares. Put those references in
`input_envelope.mandatory_references`, role stop conditions in
`input_envelope.stop_conditions` as bounded stage stops, and the source packet, scope, non-goals,
constraints, and actual permissions in the envelope.

The role's low-cost-model precondition is mandatory. If the current executor
cannot meet that model, tool, permission, or required isolation condition
inline or through an eligible worker, record `unavailable` with preflight
evidence and defer translation. Do not use a higher-cost parent merely to avoid
an unavailable result.

## Direct, Delegated, And Inline Parity

For an applicable role start with `direct`. Populate
`selection.delegation_evaluation`; delegation needs every safety gate to be
true (`applicable_role`, `current_session_runtime_support_verified`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
and `named_parent_and_final_integration_owner`), a non-empty
`material_value_triggers`, and
`cost_failure_retry_risk.result: supports-delegation`. A no-delegation runtime
applies the identical finalized-source, structure-parity, and no-extra-files
stage inline as `parent-inline`, records `direct`, and never creates invocation
evidence when inline parity is satisfiable. Its child-runtime safety gate is
false; parent-inline executor support is recorded separately.

Use `delegated` only for a genuine runtime-worker invocation whose delegated
attempt has non-empty structured `invocation_evidence`. The returned translation
and parity report remain input to this skill's initialization result; they do
not let the worker claim initialization, governance, or release completion.

## Attempts, Fallback, And Aggregation

When execution occurs, record attempts in the same record with their own
disposition, executor, and invocation evidence. Retry once only after a
correctable failure and a material state change; attempt 3 or later requires
fresh owner or workflow authorization. Not-applicable and
unavailable-before-execution use null top-level executor/invocation evidence
and empty attempts. Only a failed delegation may consider direct fallback, and
only when every `fallback.inline_contract_evidence` boolean is true:
`same_role_path_and_mandatory_references`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
`named_parent_and_final_integration_owner`, and
`current_inline_support_verified`; otherwise record `unavailable`. Direct,
unavailable, and not-applicable records never synthesize invocation evidence.

Set actual `permissions` including `secret_handling: no-secret-values`, bounded
expected/returned `output`, and the responsible parent, decision, and evidence
in `final_integration_owner`. Hand the unchanged record to
`software-development-orchestrator` for aggregation; this skill retains
inventory, provenance, direct-update, and translation-parity ownership.
