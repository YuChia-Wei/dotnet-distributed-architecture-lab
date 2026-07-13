# AI Assets

This directory is the canonical source root for portable AI assets.

## Purpose

Use `.ai/assets/` for runtime-neutral AI collaboration assets that should be reusable across agent tools. This includes canonical skill specs, delegated sub-agent role prompts, universal shared context, tech-stack profiles, and reusable templates.

## Usage

Use the nearest index file when you need a catalog of files or directories. Keep this README focused on the role and boundary of `.ai/assets/`.

## Boundary

- Keep canonical skill specs under `skills/`.
- Keep delegated sub-agent role definitions under `sub-agent-role-prompts/`.
- Keep universal shared materials under `shared/`.
- Keep stack-specific reusable context under `tech-stacks/`.
- Keep reusable asset templates under `templates/`.
- Keep runtime-specific wrappers outside `.ai/assets/`.
- Keep human-facing usage guides under `.dev/guides/`.
