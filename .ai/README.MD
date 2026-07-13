# Agent-Facing AI Context

This directory contains reusable AI collaboration assets for agents. It is not the human-facing guide root and not a runtime-specific wrapper directory.

## Purpose

Use `.ai/` for portable agent-facing context that can be reused across repositories or copied into target repositories as a framework layer.

## Usage

Start with `.ai/INDEX.MD` when you need a file or directory catalog. Use this README only to understand the role of `.ai/` and when content belongs here.

## Boundary

- Canonical reusable AI assets belong under `.ai/assets/`.
- Universal shared context belongs under `.ai/assets/shared/`.
- Tech-stack-specific context belongs under `.ai/assets/tech-stacks/<profile>/`.
- Canonical skill specs belong under `.ai/assets/skills/`.
- Canonical sub-agent role prompts belong under `.ai/assets/sub-agent-role-prompts/`.
- Runtime wrappers belong under `.agents/skills/` and `.claude/skills/`.
- Human-facing guides and workflow artifacts belong under `.dev/`.

Detailed file and directory descriptions belong in `.ai/INDEX.MD`.
