# Sub-Agent System

This file is a derived, agent-facing discovery and parity view of active
sub-agent role bindings in the current .NET backend context framework. It
does not define role applicability, routing authority, or the provider-neutral
runtime execution contract.

## Canonical Sources

- Owning skill mapping and applicability: each owning
  `.ai/assets/skills/<skill-id>/skill.yaml` `role_bindings` entry
- Delegated sub-agent role contract: `.ai/assets/sub-agent-role-prompts/<role-id>/sub-agent.yaml`
- Provider-neutral execution record and evidence rules:
  `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`
- Provider-neutral capability contracts:
  `.ai/assets/shared/provider-neutral-capability-registry.yaml`
- Provider projection status:
  `.ai/assets/shared/provider-projection-registry.yaml`
- Human-facing taxonomy guide: `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- Workflow discovery: `.dev/workflows/<workflow-id>/workflow.yaml`
- Workflow artifact contract: `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`

An owning skill manifest is the sole canonical source for a role's mapping and
applicability. A sub-agent role prompt is the sole canonical source for that
role's bounded contract. Sub-agent role prompts are not top-level skills.

When this projection and a canonical `role_bindings` entry differ, follow the
owning skill manifest and repair this derived view. Do not use this document to
infer, create, or change a binding.

## Static Projection and Selection

SAG-001 projects the active role contracts below, including SAG-003 reusable
capability rows. A row establishes only
that an active canonical binding makes the role **statically-reachable** for
the stated applicability. It does not prove that the role applies to a
particular task, that it was directly applied, that a runtime delegation was
invoked, that an adapter is available, or that execution evidence exists.

For a task, first evaluate the canonical binding's applicability:

- A nonmatching condition is `not-applicable`; it is not an error and does not
  select the role.
- A matching condition requires an explicit disposition: `direct`, `delegated`,
  or `unavailable`. Do not silently skip a matching role.
- `direct` means the owning skill or main agent applies the role contract
  inline without a runtime sub-agent invocation.
- `delegated` means a caller has confirmed the live runtime,
  permission, invocation path, and resolved model before invoking the role.
- `unavailable` means the matching role cannot be used in either selected mode;
  record the reason and hand off or stop as the owning skill requires.

These are selection and evidence terms, not extra canonical binding fields.
Runtime invocation, retries, fallbacks, and execution evidence remain outside
this static projection and are handled only by
`ROLE-EXECUTION-CONTRACT.md`.

Every projected binding below has `expected_role_status: "active"` and
`load_obligation: "mandatory-when-applicable"`. On a matching applicability,
the owning skill must load the role contract and its mandatory references before
recording `direct`, `delegated`, or `unavailable`.

## Runtime Integration

Dynamic loading is the default. A canonical role with empty `wrapper_targets`
and empty `adapter_metadata` is read by the owning skill or main agent and
applied inline by default. Delegation through a generic worker is permitted
only after the shared execution gates pass and genuine invocation evidence can
be recorded. Runtime-native promotion is an evidence-backed exception for a
concrete model, tool, permission, or invocation need; symmetry alone is not a
promotion reason.

Only `context-translator` is currently promoted. Its role contract maps
exactly one thin adapter for each supported target:

- Codex: `.codex/agents/context-translator.toml`
- Claude: `.claude/agents/context-translator.md`
- GitHub Copilot: `.github/agents/context-translator.agent.md`

This selective adapter policy does not promote or add adapters for any other
role. Adapter presence proves a validated project configuration file, not that
every host or tool surface can invoke that named adapter in the current
session. Callers must confirm runtime availability and resolved model before
delegating. They must not add adapters, packages, or promoted roles merely to
make delegation appear available.

SAG-003 generic capability roles remain dynamically loaded canonical contracts.
Their separate provider projection registry distinguishes a canonical contract,
static Codex configuration, deferred Claude and Copilot projections, and
unknown current-session availability. A configured profile is not evidence of
runtime reachability or a genuine invocation. The existing `context-translator`
adapter family remains specialized and does not establish generic capability
support for any provider.

## Runtime Execution

For each applicable binding, the owning skill produces the provider-neutral
`role_execution` record defined in
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`. It identifies the loaded
canonical role path, stage, bounded envelope, permissions, executor,
invocation evidence, output, attempts, fallback, and final integration owner.

`direct` is the default. It applies the same canonical role contract and
mandatory references inline, records `parent-inline`, and never invents a
child invocation. `delegated` is permitted only after all contract safety
gates, a material-value trigger, and cost/failure/retry-risk assessment support
it; it requires genuine invocation evidence. Lack of delegation support routes
to `direct` whenever inline parity is satisfiable, not automatically to
`unavailable`.

The orchestrator may aggregate the owner-produced records by stage and verify
their execution evidence, but it does not take domain ownership or replace the
role's output. It retains or surfaces a final integration decision and may make
that decision only when explicitly named as its owner. A conversation-only direct execution follows the same semantics
without forcing a repository artifact; workflow mode embeds or references the
complete records in its owning task.

`loaded_rule_ids` packets may be referenced through the execution record's
existing input sources. Their resolver, provider, and effective-state semantics
remain outside this derived projection and this execution contract.

## SAG-001 Derived Role-Binding Projection

| Role Asset ID | Derived Owning Skill | Binding Kind | Canonical Applicability (Projection) |
| --- | --- | --- | --- |
| `command-sub-agent` | `slice-implementer` | `primary` | The bounded slice selects command as its exactly one primary execution mode. |
| `query-sub-agent` | `slice-implementer` | `primary` | The bounded slice selects query as its exactly one primary execution mode. |
| `reactor-sub-agent` | `slice-implementer` | `primary` | The bounded slice selects reactor as its exactly one primary execution mode. |
| `aggregate-sub-agent` | `slice-implementer` | `conditional` | The selected slice needs an aggregate or event-sourced domain implementation shape without replacing its one primary execution mode. |
| `controller-sub-agent` | `slice-implementer` | `conditional` | The selected slice needs an ASP.NET Core controller or endpoint implementation shape without replacing its one primary execution mode. |
| `outbox-sub-agent` | `slice-implementer` | `conditional` | The selected slice needs outbox persistence or publishing work without replacing its one primary execution mode. |
| `profile-config-sub-agent` | `slice-implementer` | `conditional` | The selected slice needs environment-profile or appsettings configuration work without replacing its one primary execution mode. |
| `problem-frame-sub-agent` | `problem-frame-author` | `primary` | Problem-frame authoring is selected for one bounded use case or workpiece. |
| `usecase-test-sub-agent` | `slice-implementer` | `conditional` | The selected slice includes concrete use-case test implementation; a test-only slice uses generic as its one primary execution mode, while BDD design and test execution remain separate. |
| `aggregate-test-sub-agent` | `slice-implementer` | `conditional` | The selected slice includes concrete aggregate test implementation; a test-only slice uses generic as its one primary execution mode, while BDD design and test execution remain separate. |
| `controller-test-sub-agent` | `slice-implementer` | `conditional` | The selected slice includes concrete controller or API test implementation; a test-only slice uses generic as its one primary execution mode, while BDD design and test execution remain separate. |
| `reactor-test-sub-agent` | `slice-implementer` | `conditional` | The selected slice includes concrete reactor test implementation; a test-only slice uses generic as its one primary execution mode, while BDD design and test execution remain separate. |
| `context-translator` | `ai-context-init` | `conditional` | A derived Traditional Chinese translation is requested after its English source is final and a caller-verified runtime can honor the role's low-cost model precondition. |
| `mechanical-evidence-worker` | `ai-context-upgrader` | `conditional` | The selected upgrade stage needs bounded deterministic evidence collection or verification preparation; deterministic CLI and validators remain authority. |
| `reconciliation-worker` | `ai-context-upgrader` | `conditional` | The selected upgrade stage needs a bounded base/target/incoming or expected/actual reconciliation projection without an owner-sensitive semantic decision. |
| `semantic-governance-analyst` | `ai-context-upgrader` | `conditional` | The selected upgrade stage needs read-only semantic analysis of governance, policy, customization, or target-owned truth. |
| `evidence-report-synthesizer` | `ai-context-upgrader` | `conditional` | The selected upgrade stage needs a bounded report, assessment, handoff, or feedback synthesis from verified evidence only. |
| `fixed-head-independent-auditor` | `ai-context-upgrader` | `conditional` | An explicitly selected terminal or high-risk gate requires a read-only audit against one fixed clean commit. |
| `code-review-sub-agent` | `code-reviewer` | `primary` | A .NET code-review scope is selected. |
| `aggregate-code-review-sub-agent` | `code-reviewer` | `conditional` | The selected code-review scope includes aggregate, event-sourcing, or domain-invariant behavior. |
| `controller-code-review-sub-agent` | `code-reviewer` | `conditional` | The selected code-review scope includes an ASP.NET Core controller, endpoint, DTO boundary, or HTTP semantics. |
| `reactor-code-review-sub-agent` | `code-reviewer` | `conditional` | The selected code-review scope includes reactor event handling, DI registration, or cross-aggregate integration behavior. |
| `mutation-testing-sub-agent` | `slice-implementer` | `conditional` | Owner-authorized mutation-coverage or test-strengthening work is in the selected bounded slice; test execution remains a separate capability. |

`slice-implementer` selects exactly one primary `command`, `query`, `reactor`,
or `generic` execution mode. Aggregate, controller, outbox, and profile
configuration are conditional slice-shape bindings; they do not replace the
single primary mode. `generic` has no active primary role binding. A
nonmatching slice shape is `not-applicable`, while each matching conditional
binding must receive an explicit `direct`, `delegated`, or `unavailable`
disposition under the rules above.

`bdd-gwt-test-designer` owns Given-When-Then scenario and assertion design
only. It does not own concrete test implementation. The four test role
contracts above are `slice-implementer` bindings; test execution remains a
separate target-owned capability and is not a sub-agent binding in this table.

## Reusable Role Boundary

The SAG-003 rows are reusable capability contracts, not upgrade-only runtime
agents. `ai-context-upgrader` is their initial current binding. The capability
registry itself never declares ownership or applicability; additional skills may
add reconciled explicit canonical `role_bindings` later and retain their own
execution evidence.

## Delegation Rules

- Delegate only bounded work with a clear output contract.
- Keep the main agent responsible for integration, review, and final validation.
- Do not let a delegated role redefine architecture direction, skill boundaries, or workflow scope.
- If a delegated task discovers architecture uncertainty, return to `ddd-ca-hex-architect` or the main workflow owner.
- If a delegated task discovers formal review findings, route them through `code-reviewer`.
- If a delegated task becomes a bounded implementation slice, route execution through `slice-implementer`.
- If a delegated task is a small local technical change, route execution through `local-change-implementer`.

## Artifact Routing

Use durable workflow artifacts when delegated work persists repository state,
mutates repository files, performs remediation, or otherwise meets
`.dev/standards/WORKFLOW-GATE-POLICY.md`. That policy owns the workflow-mode
decision; crossing skills, stages, or sub-agents is not sufficient by itself
when the work remains transient and read-only.

Conversation-only read-only analysis may cross skills, stages, or sub-agents in
direct mode when it creates no repository artifact, mutates no repository file,
and remediates no finding. Return that result through the main agent and do not
create a workflow solely to record delegation.

Every new workflow keeps `.dev/workflows/<workflow-id>/workflow.yaml` as its locator. Read the locator for the owning skill, artifact root, entrypoint, status, and timestamps, then follow the owning skill's artifact layout.

Shared project context should come from `.dev/` source-of-truth documents, not from temporary prompts or ad hoc notes.

## Artifact Permissions

| Actor | Default Artifact Permission |
| --- | --- |
| `ddd-ca-hex-architect` | May create or update `workflow-plan.md` when architecture workflow planning is in scope. |
| `code-reviewer` | May create or update `review-report.md` when formal review is in scope. |
| `slice-implementer` / `local-change-implementer` | May update assigned `tasks/<task-id>.json` when task execution requires it. |
| General sub-agent | Read-only by default; may update task state only when explicitly assigned. |

Do not store runtime workflow records under `.ai/assets/skills/`, runtime wrapper directories, generated folders, or temporary files. A non-default artifact root must remain repository-relative and discoverable through the locator.

## Reference Inputs

Use these source areas when assigning sub-agent work:

- Requirements: `.dev/requirement/`
- Specs and test specs: `.dev/specs/`
- Problem frames: `.dev/problem-frames/`
- Operations guidance: `.dev/operations/`
- Dotnet backend shared rules: `.ai/assets/tech-stacks/dotnet-backend/`
- Workflow state: `.dev/workflows/*/workflow.yaml`, then the declared artifact root
