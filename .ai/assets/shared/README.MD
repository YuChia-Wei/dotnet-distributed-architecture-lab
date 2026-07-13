# Universal Shared Canonical Assets

This directory contains technology-neutral assets shared by skills and sub-agent roles.

Reusable, technology-specific agent-facing context belongs under `.ai/assets/tech-stacks/<profile>/`, such as `.ai/assets/tech-stacks/dotnet-backend/`.

## Allowed Content

- rules
- contracts
- prompt packages
- reusable templates
- examples

## Purpose

- Reduce duplication between skill specs and canonical sub-agent assets.
- Allow wrappers and human-facing guides to reference the same canonical source.
- Keep .NET backend-only rules out of universal shared context.
