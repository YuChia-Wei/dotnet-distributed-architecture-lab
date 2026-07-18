# Sub-Agent Role Prompts

This directory contains canonical delegated sub-agent role definitions.

## Purpose

Use `.ai/assets/sub-agent-role-prompts/` for worker-role prompts and delegation templates that a main agent can use when assigning bounded work to sub-agents.

## Usage

Each sub-agent role should keep its canonical entry in `sub-agent.yaml`, with optional supporting material under `references/`.

Current portable roles include `context-translator/`, which owns bounded low-cost Traditional Chinese (Taiwan) derivation while runtime-specific adapters remain under their runtime directories.

Top-level skills belong under `.ai/assets/skills/`; sub-agent role prompts are not top-level skills.

## Boundary

- Keep role definitions and role-specific references here.
- Keep shared reusable rules under `.ai/assets/shared/` or the relevant tech-stack profile.
- Keep human-facing taxonomy and usage guidance under `.dev/guides/ai-collaboration-guides/`.
- Keep runtime wrappers outside this directory.
