# Software Development Orchestrator Capability Profile

This profile maps generic `software-development-orchestrator` capability slots to this repository's concrete skills and local conventions.

Machine-readable source: [capability-profile.yaml](capability-profile.yaml). This
document explains the profile; the YAML file owns deterministic slot mappings
and capability contracts.

The core `software-development-orchestrator` skill should stay publishable. Repository-specific skill names belong in this profile.

## Profile Identity

- Profile name: `ai-collaboration-prompts-dotnet-backend`
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

Schema `1.2` also records deterministic orchestration invariants for
intent-class activation, approval pauses, selectable compliance, coherent
commit batches, fresh-session evidence, and separate closeout evidence.

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
