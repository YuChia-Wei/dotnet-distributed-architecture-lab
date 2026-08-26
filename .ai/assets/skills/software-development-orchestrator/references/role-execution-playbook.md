# Role Execution Aggregation Playbook

Use this playbook when an owning downstream skill selects an active canonical
sub-agent role for a development stage. The shared
[Provider-Neutral Role Execution Contract](../../../shared/ROLE-EXECUTION-CONTRACT.md)
owns the record schema and execution semantics.

## Boundaries

1. The owning skill evaluates its `role_bindings` applicability, loads the
   canonical `role_path` and mandatory references, and produces each complete
   `role_execution` record.
2. `software-development-orchestrator` aggregates records by `stage_id` and
   retains the producer's role, bounded output, and integration decision. It
   does not execute domain work or substitute its own domain conclusion.
   It may make the recorded integration decision only when that record
   explicitly names the orchestrator as `final_integration_owner.owner`.
3. `direct` is the default, including when a runtime has no child-delegation
   support but the parent can meet inline parity. Do not invent a child
   invocation for direct work.
4. `delegated` requires every shared safety gate, at least one shared
   material-value trigger, a `supports-delegation` cost/risk result, and
   genuine invocation evidence on the delegated attempt.

## Aggregation Checks

For every record returned by an owning skill, the orchestrator checks that:

- `role_path` identifies the canonical role manifest loaded for the same
  `role_asset_id`;
- applicability and disposition agree;
- a delegated attempt has non-empty genuine invocation evidence, while a
  direct attempt has `parent-inline` executor and null invocation evidence;
- the input/output/permissions/stop boundary and final integration owner are
  present;
- attempt `1` starts every executed record; attempt `2` follows a correctable
  failure plus material state change; any attempt `3` or later has new
  owner/workflow authorization;
- a delegated failure becomes direct only with shared inline-parity evidence;
  otherwise it is unavailable; and
- the final integration decision is visible as `pending`, `accepted`,
  `rejected`, or `reconciled` rather than inferred from a child response.

`not-applicable`, and `unavailable` before execution, have null top-level
executor and invocation evidence with an empty attempt list. A later
unavailable result retains its existing attempt history.

## Workflow and Conversation Projection

In workflow mode, store complete producer records under the task's
`execution.role_execution_records` and summarize stage aggregation in the
workflow plan. The task or an explicitly referenced durable artifact owns the
record; do not store runtime execution records under skill or wrapper paths.

In direct conversational work, return the same record semantics inline. No
workflow artifact, adapter, package, or child invocation is required solely to
make the record look delegated.

An existing `loaded_rule_ids` packet may appear only as a source reference in
the input envelope. Continue to use its owning resolver for packet semantics.
