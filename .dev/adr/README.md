# ADRs

This folder is the authoritative ADR set for this documentation system and its associated .NET development workflow.

## Usage Rules

- When a decision is active, document it here.
- When a decision becomes invalid, remove or replace it rather than keeping duplicate or conflicting ADRs active.
- Keep ADR numbering unique.
- Keep `INDEX.md` aligned with the files that actually exist in this folder.

## Maintenance Rules

- Do not keep migration-only duplicate ADRs as active records.
- Do not keep structurally invalid duplicates with the same ADR number.
- Prefer concise, current-state ADRs over translation notes.

## How to Add a New ADR

1. Choose the next available ADR number.
2. Write the ADR in this folder.
3. Add it to `INDEX.md`.
4. Update any high-traffic references if the new ADR changes active guidance.
