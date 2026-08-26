# Sub-Agent Role Prompts

This directory contains canonical owning-skill bounded role contracts.

## Purpose

Use `.ai/assets/sub-agent-role-prompts/` for worker-role prompts and optional
delegation templates that an owning skill can use for bounded work.

## Usage

Each sub-agent role should keep its canonical entry in `sub-agent.yaml`, with optional supporting material under `references/`.

The owning skill loads the canonical role contract. It may apply that contract
direct inline or, when eligible, use genuine delegated execution. Directory
category and loading a prompt do not prove a worker invocation; the optional
delegation template is not delegation evidence. Record execution disposition
and evidence through
`.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`.

Dynamic loading through the canonical `sub-agent.yaml` is the default. A role is
promoted only for a concrete runtime-specific need, and its exact adapter paths
are declared in `adapter_metadata`. Current portable roles include
`context-translator/`, which owns bounded low-cost Traditional Chinese (Taiwan)
derivation and is the only runtime-native role; its thin adapters remain under
their runtime directories.

Top-level skills belong under `.ai/assets/skills/`; sub-agent role prompts are not top-level skills.

## Boundary

- Keep role definitions and role-specific references here.
- Keep shared reusable rules under `.ai/assets/shared/` or the relevant tech-stack profile.
- Keep human-facing taxonomy and usage guidance under `.dev/guides/ai-collaboration-guides/`.
- Keep runtime wrappers outside this directory.
