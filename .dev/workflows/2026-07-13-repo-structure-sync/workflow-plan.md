# Repository Structure Sync Plan

## Metadata

- workflow_id: `2026-07-13-repo-structure-sync`
- owner_skill: `repo-structure-sync`
- status: `active`
- created_at: `2026-07-13T20:45:07+08:00`
- updated_at: `2026-07-13T20:56:07+08:00`
- template_source: `.ai/assets/skills/repo-structure-sync/skill.yaml`
- template_version: `1.0`
- branch: `codex/2026-07-13-repo-structure-sync`
- base_branch: `main`

## Goal

Preserve the reusable AI context introduced by commit `e8e3f85` while restoring or rebuilding repository-specific truth for `dotnet-mq-arch-lab` from current source, project files, infrastructure, documentation, and validated Git history.

## Scope

- Inventory the current .NET solution, projects, hosts, tests, persistence, messaging, and deployment evidence.
- Compare commit `e8e3f85` with its parent to locate overwritten or deleted repository-specific facts.
- Rebuild `.dev/project-config.yaml` and architecture-facing entry documents.
- Restore only historical project artifacts that remain valid for this repository.
- Keep reusable AI context, current governance rules, runtime wrappers, and completed-workflow cleanup from the context refresh.

## Tasks

| Task | Status | Purpose |
| --- | --- | --- |
| `RSS-001` | `completed` | Inventory repository facts and classify stale or removed project truth. |
| `RSS-002` | `in_progress` | Synchronize project config and architecture-facing documents. |
| `RSS-003` | `pending` | Validate AI context, workflow artifacts, references, and repository truth. |

## Completion Criteria

- Repo-specific entry documents describe the actual solution rather than the AI context source repository.
- `.dev/project-config.yaml` is regenerated from file-backed evidence.
- Historical project artifacts are restored only when current repository evidence supports them.
- Context and workflow validation pass, and Git changes are committed according to policy.
