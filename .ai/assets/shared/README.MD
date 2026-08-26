# Universal Shared Canonical Assets

This directory contains technology-neutral assets shared by skills and sub-agent roles.

Reusable, technology-specific agent-facing context belongs under `.ai/assets/tech-stacks/<profile>/`, such as `.ai/assets/tech-stacks/dotnet-backend/`.

## Allowed Content

- rules
- contracts
- [Provider-Neutral Role Execution Contract](ROLE-EXECUTION-CONTRACT.md)
- [Product Source and Projection Contract](PRODUCT-SOURCE-PROJECTION-CONTRACT.md)
- prompt packages
- reusable templates
- examples
- `governance/engineering-rule-catalog.yaml` for the canonical portable
  baseline records of registered universal engineering rules

## Purpose

- Reduce duplication between skill specs and canonical sub-agent assets.
- Allow wrappers and human-facing guides to reference the same canonical source.
- Keep .NET backend-only rules out of universal shared context.
- Treat the shared rule catalog as the owner only for its registered universal
  records; profile catalogs remain exact projections of profile Markdown owners.
