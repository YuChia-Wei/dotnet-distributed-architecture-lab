---
name: software-development-orchestrator
description: Keep authorized bounded work resumable through one project-selected workflow record, task dependencies, attributed evidence, retrospective handoff candidates and read-only retention previews.
---

# Portable Workflow Orchestration

Own organizational records and continuation, not specialist artifacts or permission.
Use this skill when work needs durable task/progress/decision/resume state. A specialist
may be used directly without a workflow. Do not manufacture phases or knowledge.

1. Read the explicit request and project authority; select existing absolute project
   and package roots and optional explicit config files. No upward policy search.
2. Read [configuration](references/configuration.md) and [operations](references/operations.md).
   Explain resolves settings; it does not prove authorization or runtime capability.
3. Create from minimal semantic input, then checkpoint actual attributed progress.
   Preserve failed/deferred evidence, stable IDs, dependencies and exact next action.
4. Resume from the saved record and selected store binding. Never turn a stored
   claim, command, reference or owner string into permission or executed work.
5. Retrospect may conclude no new knowledge. Use [composition](references/composition.md)
   for semantic specialist handoffs; never import or invoke foreign tools implicitly.
6. Use [retention](references/retention.md) only on explicit request. All modes are
   previews; no scheduler, compaction/archive/delete writer or history rewrite.

The ten operations are explain, create, inspect, query, checkpoint, transition,
resume, retrospect, render and retention-preview. Tool:
`scripts/workflow.py --request <absolute JSON file or ->` under the selected package,
using Python >=3.11,<4, PyYAML >=6,<7, jsonschema >=4.18,<5 (except explain).
No required or optional skill dependencies. Missing runtime is unavailable; no
manual write substitute or fallback disk. See the [inert example](references/example.md).

Source package 0.1.0 uses metadata/config v2 and record schema 1.0.0. Implemented
means source exists, not installed or behavior/platform certified. No source-repository
workflow, fixed artifact directory, technology stack, provider, project standards,
migration service or release policy is a dependency.
