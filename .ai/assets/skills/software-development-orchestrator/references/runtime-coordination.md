# Software Development Orchestrator Runtime Coordination

Use this reference when `software-development-orchestrator` runs inside a runtime that has its own goal, workflow, command, routine, or automation feature.

Runtime features and `software-development-orchestrator` operate at different layers:

- runtime goal or objective tracking keeps the current task durable;
- runtime workflow or command features provide an execution surface;
- `software-development-orchestrator` defines the repository/team software-development lifecycle orchestration policy;
- downstream skills perform specialist work.

## Intent-Based Runtime Activation

A runtime should select this contract from a high-level multi-stage
software-development request even when the user does not write
`$software-development-orchestrator`, `software-development-orchestrator`, or downstream skill names. A named command may
remain a convenience, but the activation signal is the requested outcome,
current lifecycle artifacts, mutation scope, and need for approval or durable
tracking.

This is a model-in-loop runtime responsibility. The deterministic acceptance
oracle begins only after the runtime or evaluator produces a preclassified
envelope with normalized stage intents. It does not parse arbitrary prose or
prove natural-language classifier quality; those claims remain in `EVAL`.
See `acceptance-oracle.md`.

After activation:

- map intent to generic capability slots before resolving providers;
- pause before implementation while requirement, design, or specification
  approval is pending;
- use repository and target policy as process truth;
- do not treat runtime completion, a skill invocation, a push, or a merge as
  product closeout.

For a fresh session, resume from the registered repository handoff checkpoint,
pinned Git state, workflow locator, current task, target policy, recorded test
state, and exact next action with `hidden_context_required: false`. Do not
reconstruct required state from prior chat context.

The DEVWF acceptance fixture invokes
`validate-workflow-handoff.py --verify-repository` against a complete temporary
Git repository, then validates locator/task continuity and exact recorded test
outcomes. A partial checkpoint-shape check is not fresh-session acceptance.

## Layer Model

| Layer | Responsibility | Typical examples |
| --- | --- | --- |
| Runtime tracker | Preserve the durable objective, session state, or continuation rule. | Codex Goal, thread objective, long-running task tracker. |
| Runtime workflow | Start or automate a repeatable runtime procedure. | Claude workflow, slash command, routine, automation. |
| `software-development-orchestrator` | Decide the development entry point, workflow mode, development capability routing, artifacts, validation, and commit checkpoints. | `.dev/workflows/<workflow-id>/`, development stage routing, handoff packets. |
| Downstream skills | Execute specialist stages. | requirements, specs, architecture, implementation, review, compliance. |

## Long-Running Validation Runtime Pattern

Classify `release`, `nightly-full`, full-matrix, and validation expected or
observed to take at least 120 seconds as long-running. The owning conversation
first completes tracked mutations and focused checks, pins a clean immutable
commit, and bounds the exact command and working directory.

Create a separate external runtime task with the least expensive capable
execution profile. Its prompt contains exactly one
  `BEGIN_EXTERNAL_TASK_DELEGATION` / `END_EXTERNAL_TASK_DELEGATION` YAML envelope
that conforms to `../templates/external-task-delegation.schema.yaml`. Start from
the dispatch template, bind either an explicit or runtime-injected source-task
identity, and name the source task as final integration owner.

Before dispatch, the owning skill creates and validates the exact
`agent-execution-packet` defined by
`../../../shared/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md`. Bind its reference,
digest, exact subject SHA, and passing validator argv in `execution_packet`.
The external worker is read-only, may write only declared ignored validation
artifacts, and must not start when the packet or worktree snapshot lease is
missing, stale, or conflicts with another tracked writer.

Select one completion path before dispatch:

- `source-task-callback`: the delegated task sends its single schema-valid
  terminal report to the source task;
- `parent-event-wait`: the source task subscribes once to a completion event for
  the delegated task and does not issue repeated status probes.

The terminal message contains exactly one
`BEGIN_EXTERNAL_TASK_COMPLETION` / `END_EXTERNAL_TASK_COMPLETION` envelope.

Before sending it, the delegated task writes the dispatch and complete
completion record to the ignored paths bound in `pre_send_validation`, runs the
canonical delegation validator against that exact pair, and records the
passing validator command and artifact references in `delivery.schema_validation`.
It must then deliver that validated completion record without any
post-validation edit. A missing or failed validation, mismatched artifact
reference, or different delivered record is non-passing.

At integration, validate the acceptance-evidence ledger against its human
report projection. Actual-execution requirements cannot be satisfied by a
fixture, mock, synthetic test, or unit result, even when that supporting test
passes.

Use an event wait as the normal callback fallback. A wait transport timeout
leaves validation pending; it is not an execution failure. If callback delivery
fails after a terminal task state is independently visible, one terminal
read-back is allowed. The read-back is acceptable only when it contains the
matching schema-valid completion report; it must not become a polling loop.
The dispatch's `progress_updates` field applies to delivery into the source
task. Runtime-required commentary that remains inside the delegated task is
allowed and must not wake or consume the source task as a progress callback.

The delegated task may write only ignored validation artifacts and must not
repair or broaden scope. It reports exactly one terminal outcome with source
and delegated task identities, commit, exact argument vector, duration, counts
when available, evidence, and final tracked state. Runtime interruption,
execution timeout, blocked execution, subject drift, or a terminal task without
a valid completion report is non-passing.

This runtime task is an execution surface, not proof of a canonical role or
external skill. Keep role applicability, provider selection, and workflow
integration under their existing owners. Do not enable parallel aggregate
execution until its dependency, isolation, concurrency, evidence-ordering, and
fail-closed cancellation contracts are independently verified.

## Codex Goal Pattern

Use a Codex Goal for the durable software-development objective. Put `software-development-orchestrator` inside that goal as the development orchestration policy.

Prompt shape:

```text
Goal:
- <durable software or product development objective>

Use $software-development-orchestrator as the orchestration policy.

Rules:
- Detect the current entry point from existing requirement/spec/workflow artifacts.
- Create or update workflow artifacts when workflow mode applies.
- Route stages through capability slots, local profile, or skill discovery.
- Use fallback-mode only when no downstream skill or reliable standard is available.
- Execute target-owned unit and integration tests by default; run specialized tests only when selected.
- Treat unselected spec compliance as not applicable and selected compliance as a 100% fail-closed gate.
- Commit after a validated durable stage or coherent bounded batch.
- Keep working until the goal is complete or a direction decision is required.
```

## Claude Workflow Pattern

Use a Claude workflow, slash command, or routine as the runtime trigger. Put `software-development-orchestrator` in the workflow prompt as the planning and routing policy.

Prompt shape:

```text
Run the team dev workflow.

Use $software-development-orchestrator as the orchestration policy for this repository.

Inputs:
- Objective: <software or product development objective>
- Existing artifacts: <requirements/specs/workflow/task paths, if any>
- Constraints: <branch, commit, validation, zero/one/multiple approved work-item identifiers, model/sub-agent constraints>

Execution:
- Detect the entry point.
- Plan stages with capability slots.
- Resolve skills from the active profile or discovery playbook.
- Create or update .dev/workflows/<workflow-id>/ when workflow mode applies.
- Honor approval pauses before implementation.
- Record exact target-owned test outcomes and selected compliance gates.
- Execute stages until done, blocked, or a user direction decision is required.

Return:
- selected mode
- stage plan
- skill routing and confidence
- workflow artifacts
- validation and commit checkpoints
- open decisions
```

## Entry Point Detection

`software-development-orchestrator` should not always restart from requirements.

| Available input | Starting point |
| --- | --- |
| Raw idea only | `requirements` |
| Requirement artifacts exist | `specification` or `architecture` |
| Requirement and spec artifacts exist | `architecture`, `test-design`, or `implementation` |
| Workflow task artifacts exist | current task status |
| Implementation exists | `review` or `compliance-validation` |

An artifact's existence does not prove approval. Before moving from requirement,
design, or specification work into implementation, verify and record the
authorization source.

## Runtime-Agnostic Prompt Contract

When writing prompts for any runtime, include:

1. objective;
2. current artifacts or state;
3. requested runtime behavior;
4. `software-development-orchestrator` orchestration rules;
5. validation expectations;
6. commit or handoff expectations;
7. target-owned test commands, prerequisites, policy, and selected levels;
8. whether spec compliance is selected;
9. when to ask the user for a direction decision.

Do not make runtime workflows the source of truth for repository process rules. Runtime workflows should invoke `software-development-orchestrator`; `software-development-orchestrator` should point to repository policies and downstream skills.

## Role Execution at Runtime

Runtime child-agent features are optional execution mechanisms, not proof that
a canonical role was delegated. For every applicable role, the owning skill
produces the provider-neutral `role_execution` record from
`../../../shared/ROLE-EXECUTION-CONTRACT.md`; the orchestrator aggregates it
by stage and remains the integration coordinator only.

Default to `direct`: the parent reads the same role manifest and mandatory
references, applies the same bounded input/output/permission/stop contract
inline, records `parent-inline`, and leaves direct invocation evidence null.
This is also the correct result when the runtime cannot launch a child but
inline parity is available.

Select `delegated` only after the shared all-gates plus material-value test and
a `supports-delegation` cost/failure/retry-risk result. The delegated attempt
must retain genuine invocation evidence. A delegated failure may become direct
only with recorded inline-parity evidence; otherwise it is unavailable. The
first execution attempt is `1`; attempt `2` follows correctable failure and
material state change; attempt `3` or later requires new owner/workflow
authorization.

Conversation-only direct use reports this same record inline without a
repository artifact. Workflow mode stores a complete record in the owning task
or references it from that task. Neither mode requires a new adapter or
package. An existing `loaded_rule_ids` packet remains an input source reference
whose resolver and effective-state semantics are unchanged.
