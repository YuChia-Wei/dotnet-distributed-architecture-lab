# Software Development Orchestrator Capability Profile

This profile maps generic `software-development-orchestrator` capability slots to this repository's concrete skills and local conventions.

Machine-readable source: [capability-profile.yaml](capability-profile.yaml). This
document explains the profile; the YAML file owns deterministic slot mappings
and capability contracts.

The core `software-development-orchestrator` skill should stay publishable. Repository-specific skill names belong in this profile.

## Profile Identity

- Profile name: `ai-collaboration-framework`
- Repository role: AI collaboration knowledge base and .NET backend context framework
- Workflow artifact root: `.dev/workflows/<workflow-id>/`
- Commit policy: `.dev/standards/GIT-COMMIT-POLICY.md`
- Workflow gate policy: `.dev/standards/WORKFLOW-GATE-POLICY.md`

## Capability Mapping

| Capability slot | Local skill | Use when |
| --- | --- | --- |
| `workflow-orchestration` | `software-development-orchestrator` | The task needs stage planning, workflow artifacts, skill routing, validation checkpoints, or commit checkpoints. |
| `requirements` | `requirement-author` | Rough notes, stakeholder inputs, or code facts need to become `.dev/requirement/`-aligned requirement docs. |
| `specification` | `spec-author` | Requirement truth needs to become retained specs under `.dev/specs/`. |
| `problem-framing` | `problem-frame-author` | Requirement, spec, code, or tests need a first problem-frame draft. |
| `architecture` | `ddd-ca-hex-architect` | The task needs DDD, Clean Architecture, CQRS, ports/adapters, bounded context, aggregate, or .NET backend architecture direction. |
| `test-design` | `bdd-gwt-test-designer` | The task needs Given-When-Then scenarios, assertion points, or test design notes. |
| `implementation` | `slice-implementer` | A bounded implementation slice is ready, using exactly one command, query, reactor, or generic execution mode plus applicable intent overlays such as remediation. |
| `local-change` | `local-change-implementer` | A local class, object, method, symbol, SQL/ORM, or direct-call-site technical change is ready. |
| `diagnosis` | `diagnostic-analyst` | An observed failure or performance symptom needs falsification and reproduction before repair. |
| `review` | `code-reviewer` | .NET backend code or dotnet-backend implementation guidance needs review. |
| `compliance-validation` | `spec-compliance-validator` | Problem-frame workflows need a 100% coverage gate. |

## Test Execution Capability Contract

`test-execution` is an allowed optional capability, not a required slot or a
mapping to a new local skill. Resolve a provider in this order:

1. target-profile commands;
2. a separately evaluated external skill;
3. the portable fallback contract.

The target repository owns the command, working directory, prerequisites,
credential requirements, environment access, and policy. The orchestrator must
record the selected target-owned contract without storing secret values and
must not invent credentials, bypass controls, or escalate privileges
implicitly.

Unit and integration are the default levels. E2E, browser, Playwright, and
environment-dependent tests are conditional and run only when a target policy,
requirement, approved plan, or owner decision selects them.

Every selected test level records exactly one of these outcomes:

- `passed`
- `failed`
- `blocked-by-environment`
- `not-applicable`
- `deferred-with-owner`

`blocked-by-environment` is blocked, never passed. For a mandatory selected
test, `not-applicable` is not a successful substitute; `deferred-with-owner`
requires an identified owner and the target policy's explicit permission to
defer. Closeout pauses while any mandatory selected test lacks an acceptable
target-policy outcome.

Each task records `required_for_closeout` as a subset of `selected_levels`.
Unit and integration remain the default selected levels; every conditional
level needs a recorded selection source.

Long-running validation uses a separate execution surface without changing the
selected checks or their result semantics. Classify `release`, `nightly-full`,
full-matrix, and any command with expected or observed wall time of at least 120
seconds as long-running. Finish tracked mutations and focused checks first, then
bind the exact command to a clean immutable commit.

Dispatch the command to a separate external runtime task using the least
expensive capable execution profile. Every prompt contains exactly one marked
dispatch envelope conforming to
`../templates/external-task-delegation.schema.yaml`; use the companion dispatch
and completion templates and validate retained envelopes with
`../scripts/validate-external-task-delegation.py`.

The dispatch names the source-task identity as explicit or runtime-injected and
selects either a source-task callback or one parent event wait. A callback must
target the source task; an event wait subscribes once to the delegated task and
does not repeatedly poll. The external task is read-only except for ignored
validation artifacts, performs no repair, and emits exactly one terminal report
with the commit, command, duration, outcome counts when available, evidence, and
final worktree state.
The terminal message similarly contains exactly one
`BEGIN_EXTERNAL_TASK_COMPLETION` / `END_EXTERNAL_TASK_COMPLETION` envelope so
the source task can validate it before accepting the outcome.

Before callback or terminal read-back delivery, the delegated task persists
the dispatch and completed report in its ignored-artifact scope, validates that
exact pair with the canonical validator, and records the successful validator
argument vector and artifact references in the completion. It sends that
validated record without post-validation edits; missing, failed, or drifting
pre-send validation is non-passing.

An execution timeout, interruption, invalid subject, missing terminal report,
or blocked execution remains non-passing. A parent event-wait timeout is only a
pending transport state. If callback delivery fails after the delegated task
has terminated, the parent may perform one terminal read-back and accept the
report only when it satisfies the completion schema. This recovery does not
authorize progress polling or relabel an execution failure. `progress_updates`
governs messages delivered to the source task; runtime-required commentary that
stays inside the delegated task is runtime-local and is not a source progress
callback.

Parallel aggregate execution is a separate implementation decision. It needs
independent contract coverage for the dependency DAG, artifact isolation,
bounded concurrency, deterministic evidence, and fail-closed cancellation
before it may replace sequential aggregate execution.

## Selectable Spec Compliance

Spec compliance is unselected by default and reports `not-applicable`. A target
profile, problem-frame workflow, requirement, or owner decision may explicitly
select it. Once selected, configuration must be complete and coverage must be
100%; partial configuration, missing execution evidence, or coverage below
100% fails closed.

The profile's `required_slots` list requires deterministic provider mappings to
exist; it does not select every mapped capability in every workflow.
Accordingly, the `compliance-validation` mapping remains available while the
spec-compliance gate itself remains selectable.

## Quality Boundary

- This profile covers the software and product development lifecycle only. AI context audit, AI context governance, documentation-only cleanup, and repository initialization use their own skill-owned workflow contracts.
- Full local workflow quality depends on the mapped downstream skills and repository standards.
- If a mapped skill is unavailable, `software-development-orchestrator` should switch that stage to fallback-mode instead of pretending the specialist review, design, or implementation was performed.
- Fallback-mode output is suitable for planning, handoff, and minimum viable checklist coverage. It is not equivalent to a specialist skill result.

## Profile Update Rules

Schema `1.2` records deterministic orchestration invariants for intent-class
activation, approval pauses, selectable compliance, coherent commit batches,
fresh-session evidence, and separate closeout evidence. Schema `1.3` adds the
repository-owned routine-validation activation policy without changing the
explicit command and lifecycle-command contracts. Schema `1.4` adds the
long-running validation delegation, schema-bound dispatch/completion envelopes,
event-driven completion delivery, no-repeated-polling rule, and safe
parallelization prerequisites.

Deterministic activation acceptance starts from the preclassified envelope
defined in `acceptance-oracle.md`. Natural-language classification remains a
model-in-loop EVAL concern. Fresh-session acceptance requires the complete
repository-verified checkpoint fixture from that reference, not only a local
continuation mapping.

- Add or change mappings in `capability-profile.yaml`, then synchronize this explanatory table before changing runtime wrappers or root routing tables.
- Keep capability names generic.
- Keep local skill names in this profile or root routing docs, not in the portable core contract.
- Keep `test-execution` optional and unmapped until a dedicated provider has
  been separately evaluated and deliberately adopted.
- If a downstream skill is renamed, update this profile and run reference searches.

## Routine Validation Activation

Routine automatic validation is target policy, not a Python runtime. The tracked
default is `validation.routine.local.mode: manual`, which performs zero routine
probes, executions, and retries. The only persistent opt-in is ignored
`.dev/validation.local.conf`, exactly one data line
`validation.routine.local=<approved-mode>`; it may strengthen but never weaken
the tracked mode. Agents never source or write it, and no environment override
exists. CI modes are `unconfigured`, `advisory`, and `required`; required needs
tracked workflow, exact command/profile, provisioned prerequisites, durable
evidence, and separately verified merge settings when claimed.

An applicable but unselected routine check records `outcome: not-applicable`
and `selection_reason: not-run-by-policy`; it is not passed. Explicit commands
and lifecycle gates are outside this switch.

## Role Execution Coordination

The capability profile maps stages to owning skills; it does not grant a
runtime child invocation. When an owning skill selects an applicable canonical
role, that skill produces a provider-neutral `role_execution` record according
to `../../../shared/ROLE-EXECUTION-CONTRACT.md`. The orchestrator aggregates
those records by stage without claiming the downstream domain result.

`direct` is the default, including a no-child runtime when inline parity is
available. `delegated` requires all shared safety gates, at least one material
value trigger, a `supports-delegation` cost/failure/retry-risk result, and
genuine child evidence. Records retain bounded envelope and permission data
without secrets, attempts and fallback, and a final integration decision.
`loaded_rule_ids` can be an opaque source reference only; its existing owner
retains resolver and effective-state semantics.
