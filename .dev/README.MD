# Project Knowledge And Governance

This directory contains the repository's human-facing governance, standards, guides, requirements, specs, operations guidance, durable backlog, and workflow records.

## Purpose

Use `.dev/` for durable project knowledge and governance that humans and agents can share during collaboration. This includes source-of-truth standards, workflow records, authoring guides, requirements, specs, domain language templates, and operations guidance.

## Usage

Start with `.dev/INDEX.md` when you need to find a specific file or directory. Use this README only to understand the role of `.dev/` and when content belongs here.

When this framework is copied into a target repository, run `repo-structure-sync` before treating target-specific requirements, specs, domain language, or operations files as current project truth.

## Boundary

- Keep human-facing guides and project governance under `.dev/`.
- Keep reusable agent-facing canonical assets under `.ai/`.
- Keep runtime-specific skill wrappers under `.agents/skills/` and `.claude/skills/`.
- Keep cross-workflow durable work items under `.dev/backlog/` and execution artifacts under `.dev/workflows/`.

Detailed file and directory descriptions belong in `.dev/INDEX.md`.
