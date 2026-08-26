# Problem Frame Author Role Execution

The problem-frame author owns a provider-neutral `role_execution` record for
its problem-frame role binding. Use the exact schema in
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; role bindings alone remain only a static
reachability declaration.

When a #114 `loaded_rule_ids` packet is relevant, cite it only as an opaque
`input_envelope.source_refs` entry. This skill does not resolve or redefine its
provider or effective-state semantics.

Evaluate whether authoring one bounded use case or workpiece is selected. A
nonmatch is `applicability.result: does-not-apply`,
`selection.disposition: not-applicable`, and
`selection.delegation_evaluation: null`. On a match, retain the binding
`role_asset_id` and exact `role_path`; load the `problem-frame-sub-agent`
manifest and every reference it declares. Record those reference paths in
`input_envelope.mandatory_references`, role stops in
`input_envelope.stop_conditions` as bounded stage stops, and source facts, scope, non-goals,
constraints, actual permissions, and bounded expected/returned authoring
output.

Use `direct` by default. Record `selection.delegation_evaluation`, and select
`delegated` only when every safety gate is true (`applicable_role`,
`current_session_runtime_support_verified`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
and `named_parent_and_final_integration_owner`), at least one
`material_value_triggers` value is present, and
`cost_failure_retry_risk.result: supports-delegation`. In a no-delegation
runtime, apply the same role workflow inline, record
`executor.kind: parent-inline` and `direct`, and keep
`invocation_evidence: null` whenever inline parity is satisfiable. Its
child-runtime safety gate is false; the inline executor separately proves
parent support.

Use `unavailable` only for an unmet mandatory model, tool, permission, or
isolation requirement that blocks both inline and eligible-worker execution.
Delegated attempts require genuine non-empty structured invocation evidence and
remain evidence for this skill's own CBF/SWF selection, extracted facts,
inferred items, and open questions.

When execution occurs, record attempts in the same record with their own
disposition, executor, and invocation evidence. Attempt 2 requires a
correctable failure plus material state change; attempt 3 or later requires
fresh owner or workflow authorization. Not-applicable and
unavailable-before-execution use null top-level executor/invocation evidence
and empty attempts. Only a failed delegated result may fall back to `direct`,
and only when every `fallback.inline_contract_evidence` boolean is true:
`same_role_path_and_mandatory_references`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
`named_parent_and_final_integration_owner`, and
`current_inline_support_verified`; otherwise mark it unavailable. Supply the
unchanged record to `software-development-orchestrator`, naming the responsible
parent, decision, and evidence in `final_integration_owner`. The orchestrator
aggregates evidence only and does not take over framing or claim validator
compliance from a draft.
