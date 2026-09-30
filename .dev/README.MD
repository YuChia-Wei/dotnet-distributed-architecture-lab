# Project Knowledge And Governance

This directory contains the repository's human-facing governance, standards, guides, requirements, specs, operations guidance, durable backlog, and workflow records.

## Purpose

Use `.dev/` for durable project knowledge and governance that humans and agents can share during collaboration. This includes source-of-truth standards, workflow records, authoring guides, requirements, specs, domain language templates, and operations guidance.

## Usage

Start with `.dev/INDEX.md` when you need to find a specific file or directory. Use this README only to understand the role of `.dev/` and when content belongs here.

For this repository, begin with `.dev/ARCHITECTURE.md` and `.dev/project-config.yaml` for current product structure, then use `.dev/INDEX.md` to locate requirements, specs, operations records, standards, and workflows.

When selected AI context changes, use the target-authorized `ai-context-governance` route and official installation evidence. Reconcile requirements, specs, domain language, operations, backlog and workflow facts against target-owned source; installation does not make them current automatically. Generic authoring guidance lives in the selected knowledge/skill packages. Existing ordinary workflows remain manually governed by target policy; retired init/upgrader and portable orchestrator routes are unavailable.

## Boundary

- Keep human-facing guides and project governance under `.dev/`.
- Keep reusable agent-facing canonical assets under `.ai/`.
- Keep runtime-specific skill wrappers under `.agents/skills/` and `.claude/skills/`.
- Keep cross-workflow durable work items under `.dev/backlog/` and execution artifacts under `.dev/workflows/`.

Detailed file and directory descriptions belong in `.dev/INDEX.md`.
