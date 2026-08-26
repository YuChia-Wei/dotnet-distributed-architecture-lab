# Provider-Neutral Role Execution Contract

This contract records how an applicable canonical sub-agent role was executed
without making a runtime, adapter, model, or provider the source of truth. It
does not define role applicability, role bindings, `loaded_rule_ids`, provider
configuration, or effective-state semantics.

## Ownership and Use

- The owning skill evaluates its own canonical binding and produces each
  `role_execution` record.
- The role contract at `role_path` and its mandatory references remain the
  executable role source. The record proves which same contract was loaded.
- `software-development-orchestrator` aggregates complete records by
  `stage_id`, checks this contract's evidence boundaries, and coordinates
  integration. It does not take domain ownership or replace an owning skill's
  output. It retains or surfaces `final_integration_owner.decision` and may
  make that decision only when explicitly named as the final integration owner.
- In conversation-only direct work, use the same semantics without creating a
  repository artifact. In workflow mode, embed complete records in a task or
  reference a durable record from that task.
- A #114 `loaded_rule_ids` packet may be cited in `input_envelope.source_refs`.
  This contract neither creates, resolves, validates, nor redefines that
  packet.

## Selection

`direct` is the default disposition. A matching role may be `delegated` only
when every delegation safety gate passes, at least one material-value trigger
is present, the deterministic cost/risk result supports delegation, and a
genuine runtime child invocation occurs.

| Delegation safety gate | Meaning |
| --- | --- |
| `applicable_role` | The owning skill's canonical binding applies to this stage. |
| `current_session_runtime_support_verified` | The current session has verified child/delegation support and an invocation path. It is `false` for a no-delegation direct path; `executor.runtime_support_verified` separately proves inline parent support. |
| `bounded_input_output_permissions_stop` | Input, expected output, permissions, and stop conditions are bounded. |
| `approval_security_credential_boundaries_satisfied` | Required approvals and security boundaries are satisfied; no secret value is placed in the record. |
| `disjoint_mutation_scope` | Delegated mutation scope is disjoint from concurrent writers, or the record selects no mutation. |
| `named_parent_and_final_integration_owner` | A parent and final integration owner are named. |

Allowed `material_value_triggers` are:

- `independent_parallel_substantive_unit`
- `meaningful_isolation`
- `specialist_context_benefit`
- `elapsed_time_benefit`

`cost_failure_retry_risk.result` is exactly
`supports-delegation` or `favors-direct`, with a concise evidence-backed
reason. Cost includes total agent and tool work plus likely failure and retry
risk.

If child-runtime support is absent or delegation is not worthwhile, select
`direct` when the same inline role contract can be satisfied. Do not treat the
absence of delegation support as `unavailable` when inline parity is possible.

## `role_execution` Record Schema

Every record has these top-level fields:

| Field | Required content |
| --- | --- |
| `role_execution_id` | Stable record identifier within the task or conversation. |
| `role_asset_id` | Canonical role asset identifier. |
| `role_path` | Exact canonical `sub-agent.yaml` path loaded for this execution. |
| `owning_skill` | The skill that owns applicability and produces the record. |
| `stage_id` | The bounded stage receiving this role output. |
| `applicability` | `{ result: applies | does-not-apply, reason: ... }`. |
| `selection` | Final/current disposition, reason, and applicable delegation evaluation; earlier execution history remains in `attempts`. |
| `input_envelope` | Bounded goal, scope, sources, mandatory references, constraints, and stop conditions. |
| `permissions` | Read/write scope and external actions, without secret values. |
| `executor` | Exact copy of the final attempt's inline-parent or runtime-worker executor; `null` only when `attempts` is empty. |
| `invocation_evidence` | Exact copy of the final attempt's invocation evidence; it is `null` when that final attempt records no invocation, including direct execution. |
| `output` | Bounded expected and returned output plus evidence. |
| `attempts` | Ordered execution-attempt evidence starting at `1` when execution occurs; empty for not-applicable or unavailable before execution. |
| `fallback` | Whether a delegated failure needed a direct or unavailable result. |
| `final_integration_owner` | Named owner and the recorded integration decision. |

```yaml
role_execution_id: "<stage>-<role>-01"
role_asset_id: "<canonical-role-id>"
role_path: ".ai/assets/sub-agent-role-prompts/<role-id>/sub-agent.yaml"
owning_skill: "<canonical-skill-id>"
stage_id: "<bounded-stage-id>"
applicability:
  result: "applies" # applies | does-not-apply
  reason: "<canonical binding condition and task evidence>"
selection:
  disposition: "direct" # direct | delegated | unavailable | not-applicable
  reason: "<selection evidence>"
  delegation_evaluation:
    safety_gates:
      applicable_role: true
      current_session_runtime_support_verified: false
      bounded_input_output_permissions_stop: true
      approval_security_credential_boundaries_satisfied: true
      disjoint_mutation_scope: true
      named_parent_and_final_integration_owner: true
    material_value_triggers: []
    cost_failure_retry_risk:
      result: "favors-direct" # supports-delegation | favors-direct
      reason: "<agent/tool cost and failure/retry-risk assessment>"
input_envelope:
  goal: "<bounded role goal>"
  scope: ["<allowed target or artifact>"]
  non_goals: ["<excluded work>"]
  source_refs: ["<requirement, task, or loaded-rule-packet reference>"]
  mandatory_references: ["<role-contract reference path>"]
  constraints: ["<applicable constraint>"]
  stop_conditions: ["<condition that returns control to the parent>"]
permissions:
  read_scope: ["<repository-relative path or artifact>"]
  write_scope: []
  external_actions: []
  secret_handling: "no-secret-values"
executor: # exact copy of attempts[-1].executor; null only when attempts is empty
  kind: "parent-inline" # parent-inline | runtime-worker
  identity: "<session-safe parent or worker reference>"
  runtime_support_verified: true
invocation_evidence: null # exact copy of attempts[-1].invocation_evidence when attempts is non-empty
output:
  expected: ["<bounded output item>"]
  returned: ["<actual bounded output item>"]
  evidence_refs: ["<returned artifact or response reference>"]
  bounded: true
attempts:
  - number: 1
    disposition: "direct" # direct | delegated | unavailable
    executor:
      kind: "parent-inline" # parent-inline | runtime-worker
      identity: "<session-safe parent or worker reference>"
      runtime_support_verified: true
    invocation_evidence: null # required structured evidence for delegated
    outcome: "completed"
    correctable_failure: false
    material_state_change: ""
    authorization_source: []
    evidence_refs: ["<execution evidence>"]
fallback:
  considered: false
  reason: "not needed"
  resulting_disposition: null # direct | unavailable | null
  inline_contract_evidence:
    same_role_path_and_mandatory_references: false
    bounded_input_output_permissions_stop: false
    approval_security_credential_boundaries_satisfied: false
    disjoint_mutation_scope: false
    named_parent_and_final_integration_owner: false
    current_inline_support_verified: false
    evidence_refs: []
final_integration_owner:
  owner: "<named parent/integration owner>"
  decision: "pending" # pending | accepted | rejected | reconciled
  evidence_refs: []
```

`selection.disposition` is the record's final/current disposition. It may be
`direct` after an earlier delegated attempt; do not rewrite that earlier
delegated evidence. `selection.delegation_evaluation` is `null` when
`applicability.result` is `does-not-apply`. In that case the disposition is
`not-applicable`, `executor` and `invocation_evidence` are `null`, and
`attempts` is empty. The bounded output states why no role output was needed.
An applicable `unavailable` record uses the same null/empty values only when
execution never began. An unavailable result after an attempt retains its
attempt history and copies that final attempt's `executor` and
`invocation_evidence` to the top level.

## Disposition and Invocation Rules

| Disposition | Required meaning |
| --- | --- |
| `direct` | The parent applies the same `role_path`, mandatory references, input, output, permission, and stage obligations inline. Its direct attempt has `executor.kind: parent-inline` and `invocation_evidence: null`; no child invocation is invented. |
| `delegated` | Every safety gate is true, one or more material-value triggers exist, cost/risk supports delegation, and its delegated attempt has non-empty structured invocation evidence. That attempt has `executor.kind: runtime-worker`. A planned or adapter-visible child is not evidence of delegation. |
| `unavailable` | The role applies but neither a verified delegation nor a Q7-equivalent inline execution can satisfy the bounded contract. Record the blocking reason and integration owner decision. |
| `not-applicable` | The canonical applicability condition does not match. It is not an error or a silent skip. |

Only a delegated attempt may have non-null `invocation_evidence`. It contains
`invocation_id`, `started_at`, `completed_at`, `outcome`, and `evidence_refs`.
It proves a genuine child execution rather than an adapter file, a planned
call, or a parent summary. Top-level `executor` and `invocation_evidence`
must exactly equal the final attempt's corresponding fields. They may therefore
be direct/null after a genuine delegated attempt falls back inline, or remain a
delegated executor and genuine invocation summary when the final disposition is
unavailable after that delegated attempt.

## Attempts and Fallback

When execution occurs, the first attempt has `number: 1`. Each attempt
contains `number`, `disposition`, `executor`, `invocation_evidence`, `outcome`,
`correctable_failure`, `material_state_change`, `authorization_source`, and
`evidence_refs`. A direct attempt has `parent-inline` executor and null
invocation evidence; a delegated attempt has `runtime-worker` executor and
genuine structured invocation evidence. Each `authorization_source` item is a
stable reference to owner or workflow authorization evidence.

- Attempt `2` is allowed only when the preceding attempt recorded both a
  correctable failure and a material state change.
- Attempt `3` or later remains in the same record and requires a non-empty
  new owner or workflow authorization in `authorization_source`. At least one
  authorization reference must not appear in any earlier attempt in the same
  record; repeating only earlier references is not new authorization. The
  attempt must not erase earlier attempt evidence.
- A failed delegation may fall back to `direct` only when
  `fallback.inline_contract_evidence` proves inline parity with every required
  boolean true: `same_role_path_and_mandatory_references`,
  `bounded_input_output_permissions_stop`,
  `approval_security_credential_boundaries_satisfied`,
  `disjoint_mutation_scope`, `named_parent_and_final_integration_owner`, and
  `current_inline_support_verified`. Otherwise the fallback result is
  `unavailable`.

Inline fallback does not require child-runtime support or a material-value
trigger: those are delegation gates, not prerequisites for the direct default.

## Examples

### Direct because delegation is not worthwhile

```yaml
role_execution_id: "implementation-command-01"
role_asset_id: "command-sub-agent"
role_path: ".ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml"
owning_skill: "slice-implementer"
stage_id: "implementation"
applicability: { result: "applies", reason: "selected primary command mode" }
selection:
  disposition: "direct"
  reason: "one bounded edit has no material delegation benefit"
  delegation_evaluation:
    safety_gates:
      applicable_role: true
      current_session_runtime_support_verified: false
      bounded_input_output_permissions_stop: true
      approval_security_credential_boundaries_satisfied: true
      disjoint_mutation_scope: true
      named_parent_and_final_integration_owner: true
    material_value_triggers: []
    cost_failure_retry_risk: { result: "favors-direct", reason: "child setup exceeds the bounded work" }
input_envelope:
  goal: "implement the approved command behavior"
  scope: ["src/Orders/CreateOrderUseCase.cs"]
  non_goals: ["architecture redesign"]
  source_refs: ["REQ-17", "SPEC-17"]
  mandatory_references: [".ai/assets/sub-agent-role-prompts/command-sub-agent/references/implementation-playbook.md"]
  constraints: ["existing architecture rules"]
  stop_conditions: ["return when implementation and narrow validation are complete"]
permissions: { read_scope: ["src/Orders"], write_scope: ["src/Orders/CreateOrderUseCase.cs"], external_actions: [], secret_handling: "no-secret-values" }
executor: { kind: "parent-inline", identity: "parent-stage-owner", runtime_support_verified: true }
invocation_evidence: null
output: { expected: ["bounded command implementation"], returned: ["CreateOrderUseCase change"], evidence_refs: ["src/Orders/CreateOrderUseCase.cs"], bounded: true }
attempts: [{ number: 1, disposition: "direct", executor: { kind: "parent-inline", identity: "parent-stage-owner", runtime_support_verified: true }, invocation_evidence: null, outcome: "completed", correctable_failure: false, material_state_change: "", authorization_source: [], evidence_refs: ["parent execution record"] }]
fallback: { considered: false, reason: "direct selected initially", resulting_disposition: null, inline_contract_evidence: { same_role_path_and_mandatory_references: false, bounded_input_output_permissions_stop: false, approval_security_credential_boundaries_satisfied: false, disjoint_mutation_scope: false, named_parent_and_final_integration_owner: false, current_inline_support_verified: false, evidence_refs: [] } }
final_integration_owner: { owner: "workflow parent", decision: "accepted", evidence_refs: ["task result"] }
```

### Delegated failure with valid inline fallback

```yaml
selection: { disposition: "direct", reason: "delegated attempt failed; inline parity verified", delegation_evaluation: { safety_gates: { applicable_role: true, current_session_runtime_support_verified: true, bounded_input_output_permissions_stop: true, approval_security_credential_boundaries_satisfied: true, disjoint_mutation_scope: true, named_parent_and_final_integration_owner: true }, material_value_triggers: ["meaningful_isolation"], cost_failure_retry_risk: { result: "supports-delegation", reason: "initial independent review was valuable" } } }
executor: { kind: "parent-inline", identity: "parent-stage-owner", runtime_support_verified: true }
invocation_evidence: null # retained child evidence is in attempt 1
attempts:
  - { number: 1, disposition: "delegated", executor: { kind: "runtime-worker", identity: "worker-42", runtime_support_verified: true }, invocation_evidence: { invocation_id: "inv-42", started_at: "<ISO-8601>", completed_at: "<ISO-8601>", outcome: "failed", evidence_refs: ["runtime receipt"] }, outcome: "failed", correctable_failure: true, material_state_change: "child output was incomplete; parent narrowed the output envelope", authorization_source: [], evidence_refs: ["runtime receipt"] }
  - { number: 2, disposition: "direct", executor: { kind: "parent-inline", identity: "parent-stage-owner", runtime_support_verified: true }, invocation_evidence: null, outcome: "completed", correctable_failure: false, material_state_change: "", authorization_source: [], evidence_refs: ["inline response"] }
fallback:
  considered: true
  reason: "delegated worker did not return the bounded output"
  resulting_disposition: "direct"
  inline_contract_evidence:
    same_role_path_and_mandatory_references: true
    bounded_input_output_permissions_stop: true
    approval_security_credential_boundaries_satisfied: true
    disjoint_mutation_scope: true
    named_parent_and_final_integration_owner: true
    current_inline_support_verified: true
    evidence_refs: ["same role contract loaded", "inline bounded envelope"]
```

The delegated invocation remains genuine evidence in attempt `1`; a fallback
does not relabel it as a direct execution.
