# Software Development Orchestrator Routing Playbook

Use this playbook after the workflow gate confirms that software or product development work needs stage planning, development skill orchestration, or durable task tracking.

## Intent-Based Activation

Activate this orchestration contract from the user's high-level
software-development intent. The user does not need to name `software-development-orchestrator` or
any downstream skill. Derive stages from the requested outcome, current
artifacts, repository policy, and approval state; do not infer the lifecycle
from skill names alone.

## Routing Model

Route in two steps:

1. Map each stage to a generic capability slot.
2. Resolve the slot through the active capability profile or skill discovery.

If the active profile has no matching downstream skill, use `skill-discovery-playbook.md` to inspect available skills. If discovery is low-confidence or finds no match, use `fallback-playbooks.md` and clearly mark the stage as fallback-mode.

## Generic Capability Slots

| Work intent | Capability slot | Expected specialist output |
| --- | --- | --- |
| Workflow planning, stage sequencing, task tracking, validation and commit checkpoints | `workflow-orchestration` | Stage plan, artifact decision, checkpoint plan, final evidence summary. |
| Requirement drafting or normalization | `requirements` | Requirement draft, assumptions, gaps, source-truth notes. |
| Spec drafting or normalization | `specification` | Behavior or component spec, source references, handoff notes. |
| First problem-frame extraction | `problem-framing` | Validator-ready problem frame draft and source evidence. |
| Architecture design or architecture refactoring direction | `architecture` | Bounded design decision, tradeoffs, target structure, non-goals. |
| GWT scenario and assertion design | `test-design` | Scenarios, assertion points, test level recommendation. |
| Bounded slice implementation | `implementation` | Code or document changes for a bounded slice, narrow validation. |
| Local technical change | `local-change` | Local class, object, method, symbol, SQL/ORM, or direct-call-site changes and narrow validation. |
| Execute target-selected tests | `test-execution` | Target-owned commands, exact outcomes, and environment or deferral evidence. |
| Code or artifact review | `review` | Findings, severity, evidence, residual risk. |
| Compliance or coverage gate | `compliance-validation` | Coverage result, missing evidence, pass/fail gate. |

## Local Profile Resolution

For this repository, resolve slots through the machine-readable
`capability-profile.yaml`; use `capability-profile.md` for rationale and human review.

The current local profile maps slots to these concrete skills:

| Capability slot | Local skill |
| --- | --- | --- |
| `workflow-orchestration` | `software-development-orchestrator` |
| `requirements` | `requirement-author` |
| `specification` | `spec-author` |
| `problem-framing` | `problem-frame-author` |
| `architecture` | `ddd-ca-hex-architect` |
| `test-design` | `bdd-gwt-test-designer` |
| `implementation` | `slice-implementer` |
| `local-change` | `local-change-implementer` |
| `review` | `code-reviewer` |
| `compliance-validation` | `spec-compliance-validator` |

`test-execution` is intentionally absent from the mapping table. It is an
optional capability contract, not a required dedicated skill. Resolve its
provider in the machine-readable order declared by `capability-profile.yaml`:
target-profile commands, a separately evaluated external skill, then the
fallback contract. Unit and integration are default levels; E2E, browser,
Playwright, and environment-dependent tests remain conditional.

## Skill Discovery Resolution

When no explicit profile exists, or when the profile does not cover a capability slot:

1. read `skill-discovery-playbook.md`;
2. inspect available skill metadata and wrapper descriptions;
3. prefer declared `capability_slots`;
4. infer only when the candidate is clear;
5. report confidence and evidence in the workflow plan;
6. fall back when confidence is low or no candidate exists.

## Orchestration Boundaries

- `software-development-orchestrator` may decide the stage sequence, update workflow task status, and request the next skill.
- `software-development-orchestrator` must not invent downstream skill findings or claim a domain result without running or applying the downstream workflow.
- Pause before creating or executing implementation work when a requirement,
  design, or specification discussion is awaiting approval. Record the pending
  direction and resume only after explicit authorization.
- For `test-execution`, use target-owned commands, working directory,
  prerequisites, and policy. Record one exact supported outcome per selected
  level; never count `blocked-by-environment` as passed.
- For a `release`, `nightly-full`, full-matrix, or at-least-120-second
  validation, finish local mutations and focused checks, pin a clean immutable
  commit, then dispatch the exact command to the least expensive capable
  external runtime task. Build the prompt and terminal report from the canonical
  external-task delegation schema and templates. Select a source-task callback
  or one parent event wait; do not poll from the primary conversation. A
  terminal callback failure may use one schema-valid terminal read-back, while
  a parent wait timeout remains pending rather than passed or failed. Before
  delivery, the delegated task persists the dispatch and completed report in
  ignored artifacts, validates that exact pair with the canonical validator,
  and sends the validated completion record without modifying it.
- Treat spec compliance as unselected and `not-applicable` unless a target
  profile, problem-frame workflow, requirement, or owner decision selects it.
  Once selected, incomplete configuration or coverage below 100% fails closed.
- AI context auditing, AI context governance, documentation-only cleanup, and repository initialization are outside this orchestration profile. Route them directly to their owning skill instead of representing them as development capability slots.
- When two capability slots could apply, route by the source of truth being changed:
  - product or code architecture truth: `architecture`
  - requirement truth: `requirements`
  - behavior specification truth: `specification`
  - test scenario truth: `test-design`
  - implementation truth: `implementation`
  - review truth: `review` or `compliance-validation`
- If no matching local skill exists, call out fallback-mode explicitly and use `fallback-playbooks.md`.

## Handoff Packet

When handing a stage to another skill or sub-agent, include:

1. workflow id and task id;
2. stage goal and non-goals;
3. source files and policies already read;
4. user constraints and open decisions;
5. expected output files or output sections;
6. target-owned test command, working directory, prerequisites, and policy when
   test execution is selected;
7. validation expected before returning;
8. approval state and the decision that would pause or resume execution.

For a separate runtime task, also include the single marked dispatch envelope
defined by `../templates/external-task-delegation.schema.yaml`. Do not rely on
free-form prose to identify the source task or terminal delivery route. Bind
the ignored dispatch/completion artifact references and canonical pre-send
validator argument vector in that envelope.

## Role Execution Handoff and Aggregation

When a selected stage has an applicable canonical sub-agent role, the owning
skill—not this orchestrator—loads the role manifest and mandatory references,
then produces the complete provider-neutral `role_execution` record defined in
`../../../shared/ROLE-EXECUTION-CONTRACT.md`.

Include the role record or its durable task reference in the handoff. The
orchestrator aggregates records by `stage_id`, checks disposition, genuine
delegation evidence, attempts, fallback, and final integration decision, then
keeps the owning skill's domain output intact. It must not infer a role result
from routing metadata or a runtime adapter.

Use `direct` by default. Delegation requires every shared safety gate, one or
more material-value triggers, a `supports-delegation` risk result, and a real
child invocation. If that route is unavailable but the parent can apply the
same role contract inline, select `direct`; otherwise select `unavailable`.
The existing `loaded_rule_ids` packet may be cited as an input source, without
changing its semantics.
