# Sub-Agent System

This file defines the active agent-facing routing rules for delegated sub-agent work in the current .NET backend context framework.

## Canonical Sources

- Top-level skill specs: `.ai/assets/skills/<skill-id>/skill.yaml`
- Delegated sub-agent role prompts: `.ai/assets/sub-agent-role-prompts/<role-id>/sub-agent.yaml`
- Human-facing taxonomy guide: `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- Workflow discovery: `.dev/workflows/<workflow-id>/workflow.yaml`
- Workflow artifact contract: `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`

Sub-agent role prompts are not top-level skills. They are bounded worker roles used by a main agent or a top-level skill.

## Runtime Integration

Dynamic loading is the default. A canonical role with empty `wrapper_targets`
and empty `adapter_metadata` is read by the owning skill or main agent and
delegated through a generic worker. Runtime-native promotion is an
evidence-backed exception for a concrete model, tool, permission, or invocation
need; symmetry alone is not a promotion reason.

Only `context-translator` is currently promoted. Its canonical manifest maps
exactly one thin adapter for each supported target:

- Codex: `.codex/agents/context-translator.toml`
- Claude: `.claude/agents/context-translator.md`
- GitHub Copilot: `.github/agents/context-translator.agent.md`

Adapter presence proves a validated project configuration file, not that every
host or tool surface can invoke that named adapter in the current session.
Callers must confirm runtime availability and resolved model before delegating.

## Active Role Routing

| Work Type | Top-Level Skill | Delegated Role Prompt |
| --- | --- | --- |
| Command use case implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml` |
| Query use case implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml` |
| Reactor implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml` |
| Aggregate implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/sub-agent.yaml` |
| Controller implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/controller-sub-agent/sub-agent.yaml` |
| Outbox implementation | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml` |
| Profile configuration | `slice-implementer` | `.ai/assets/sub-agent-role-prompts/profile-config-sub-agent/sub-agent.yaml` |
| Problem frame authoring support | `problem-frame-author` | `.ai/assets/sub-agent-role-prompts/problem-frame-sub-agent/sub-agent.yaml` |
| Use case test generation | `bdd-gwt-test-designer` | `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml` |
| Aggregate test generation | `bdd-gwt-test-designer` | `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml` |
| Controller test generation | `bdd-gwt-test-designer` | `.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/sub-agent.yaml` |
| Reactor test generation | `bdd-gwt-test-designer` | `.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/sub-agent.yaml` |
| Derived Traditional Chinese translation after English context is final | `ai-context-init` or the owning main workflow | `.ai/assets/sub-agent-role-prompts/context-translator/sub-agent.yaml` |
| General code review support | `code-reviewer` | `.ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml` |
| Aggregate code review support | `code-reviewer` | `.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/sub-agent.yaml` |
| Controller code review support | `code-reviewer` | `.ai/assets/sub-agent-role-prompts/controller-code-review-sub-agent/sub-agent.yaml` |
| Reactor code review support | `code-reviewer` | `.ai/assets/sub-agent-role-prompts/reactor-code-review-sub-agent/sub-agent.yaml` |
| Mutation testing support | `slice-implementer` or task-specific validation workflow | `.ai/assets/sub-agent-role-prompts/mutation-testing-sub-agent/sub-agent.yaml` |

## Non-Active Roles

A reconciler role is not active in this repository because `.ai/assets/sub-agent-role-prompts/reconciler-sub-agent/` does not exist. Do not route work to a reconciler sub-agent until a separate workflow creates and validates that canonical role prompt.

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
