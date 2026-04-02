# ADRs

This folder is the authoritative ADR set for this documentation system and its associated .NET development workflow.

## Usage Rules

- When a decision is active, document it here.
- When a decision becomes invalid, remove or replace it rather than keeping duplicate or conflicting ADRs active.
- Keep ADR numbering unique.
- Keep `INDEX.md` aligned with the files that actually exist in this folder.

## Status Model

`INDEX.md` 應將 ADR 至少區分為：

- `Active ADR`
  - 仍然是主要決策入口，尚未完全被其他 canonical 文件吸收
- `Landed in Standards`
  - 規則已被 `.dev/standards/`、`.dev/specs/`、`.dev/operations/`、`.dev/guides/` 或 `.ai/` 的正式文件承接
- `Historical / Superseded`
  - 主要用於保留決策脈絡，已不是 active source of truth

若規則已被正式標準文件完整承接，優先讓標準文件成為主要入口，而不是讓 ADR 繼續承擔日常使用入口。

## Maintenance Rules

- Do not keep migration-only duplicate ADRs as active records.
- Do not keep structurally invalid duplicates with the same ADR number.
- Prefer concise, current-state ADRs over translation notes.
- When an ADR's reusable value has been extracted into `.dev/standards/` or `.dev/standards/rationale/`, the ADR may be retired and removed.

## How to Add a New ADR

1. Choose the next available ADR number.
2. Write the ADR in this folder.
3. Add it to `INDEX.md`.
4. Update any high-traffic references if the new ADR changes active guidance.
