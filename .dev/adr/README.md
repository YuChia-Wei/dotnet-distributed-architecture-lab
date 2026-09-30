# ADR Governance

This directory is the architecture decision governance area. It is not the daily rules entry point.

## Purpose

Use `.dev/adr/` to keep project decision records and retained historical decision context when a decision still has governance value. New portable authoring uses [adr-author](../../.ai/core/skills/adr-author/SKILL.md); it does not migrate retained Markdown decisions or replace their target authority.

## Usage

Start with `.dev/adr/INDEX.md` for the ADR catalog and retained status. Use this README only to understand when ADR content belongs here.

## Boundary

- Put current implementation rules under `.dev/standards/`.
- Put human-facing workflow guides under `.dev/guides/`.
- Put one-time workflow records under `.dev/workflows/`.
- Use ADRs for structural decisions and rationale, not for routine checklists or tutorials.
