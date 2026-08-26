# Slice Implementer Role Execution

`role_bindings` establishes static reachability only. For every binding
considered by a bounded slice, this skill owns one provider-neutral
`role_execution` record. Follow the field contract in
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; do not redefine it in a runtime adapter or
transfer this domain record to the orchestrator.

When a #114 `loaded_rule_ids` packet is relevant, cite it only as an opaque
`input_envelope.source_refs` entry. This skill neither resolves nor changes its
provider or effective-state semantics.

## Per-Binding Procedure

1. Evaluate the binding's applicability against the selected primary mode,
   overlays, and concrete implementation scope. A genuine nonmatch records
   `applicability.result: does-not-apply`,
   `selection.disposition: not-applicable`, and
   `selection.delegation_evaluation: null`.
2. For an applicable binding, retain the binding `role_asset_id` and exact
   `role_path`; load that role manifest and every reference it declares. Put
   every loaded reference path in `input_envelope.mandatory_references` and
   the bounded stage's explicit stop conditions in
   `input_envelope.stop_conditions`, together with the goal, scope, non-goals,
   source references, and constraints.
3. Start with `selection.disposition: direct`. Populate
   `selection.delegation_evaluation` for every applicable role. Delegation is
   eligible only when every safety gate is true: `applicable_role`,
   `current_session_runtime_support_verified`,
   `bounded_input_output_permissions_stop`,
   `approval_security_credential_boundaries_satisfied`,
   `disjoint_mutation_scope`, and
   `named_parent_and_final_integration_owner`; at least one
   `material_value_triggers` value is present; and
   `cost_failure_retry_risk.result: supports-delegation`.
4. If delegation is not eligible, execute the same loaded role workflow inline
   and record `executor.kind: parent-inline`, a direct first attempt, and
   `invocation_evidence: null`. A runtime without child delegation follows this
   same path whenever inline parity is satisfiable. Its
   `current_session_runtime_support_verified` delegation gate is false while
   the inline executor independently verifies parent support; it never
   synthesizes a child invocation.
5. Select `delegated` only after a genuine runtime-worker invocation. Its
   delegated attempt has non-empty structured `invocation_evidence`, and the
   child output is input to, not replacement for, this skill's slice decision
   and validation.
6. Select `unavailable` only when a mandatory model, tool, permission, or
   isolation requirement cannot be met inline or through an eligible worker.
   Record the failed requirement and the preflight/attempt evidence; do not use
   `unavailable` for a nonmatch or merely because child delegation is absent.

## Retry, Fallback, And Handoff

When execution occurs, record attempts in the same record with their own
disposition, executor, and invocation evidence. Attempt 2 is allowed only
after attempt 1 has a correctable failure and a material state change; record
both facts and the authorization source. Attempt 3 or later requires fresh
owner or workflow authorization in the attempt evidence. For not-applicable or
unavailable-before-execution, set top-level `executor` and
`invocation_evidence` to `null` and `attempts` to an empty list.

Only a failed delegated attempt may consider a direct fallback. It may result
in `direct` only when `fallback.inline_contract_evidence` sets every required
boolean true: `same_role_path_and_mandatory_references`,
`bounded_input_output_permissions_stop`,
`approval_security_credential_boundaries_satisfied`, `disjoint_mutation_scope`,
`named_parent_and_final_integration_owner`, and
`current_inline_support_verified`. A material-value trigger and child-runtime
support are delegation gates, not direct-fallback gates; otherwise the fallback
result is `unavailable`. Direct, not-applicable, and unavailable paths never
invent invocation evidence.

For every record, set `permissions` to the actual read/write/external-action
scope and `secret_handling: no-secret-values`; set a bounded expected and
returned `output`; and name the responsible parent plus decision/evidence in
`final_integration_owner`. Hand each unchanged, skill-owned record to
`software-development-orchestrator` for stage aggregation. The orchestrator
may check evidence and attempt limits, but this skill retains ownership of
slice mode, implementation, validation, and domain synthesis.

## Concrete Test Boundary

This skill owns concrete use-case, aggregate, controller, reactor, and
owner-authorized mutation-test implementation. A test-only slice uses
`generic` as its one primary mode and evaluates the applicable concrete-test
bindings. BDD/GWT design supplies scenarios and assertion intent only; it does
not authorize code changes. Test implementation and target-owned test execution
produce separate stage outcomes. Mutation testing remains conditional on the
selected bounded slice and does not make test execution implicit.
