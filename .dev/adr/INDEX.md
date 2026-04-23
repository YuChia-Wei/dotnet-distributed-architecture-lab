# ADR Index

本目錄目前以治理文件為主，暫不保留 active `ADR-*.md`。

## Current Contents

| File | Role |
| --- | --- |
| `README.md` | ADR 治理說明 |
| `ADR-TEMPLATE.md` | 新 ADR 樣板 |
| `WHEN-TO-CREATE-ADR.MD` | 何時需要建立 ADR |
| `PORTABILITY-NOTES.MD` | 可攜移植說明 |

## Status Rule

- 若未來有新的重大結構性決策，應新增 `ADR-###-<topic>.md`
- 若該決策後續已完整收斂到 `.dev/standards/`、`.dev/guides/` 或 `.ai/`，可在此索引註記其 retired / landed 狀態
- 若沒有需要保留的 active decision record，`INDEX.md` 可以維持只有治理文件清單

## Naming Rule

- 檔名格式：`ADR-###-<topic>.md`
- `###` 使用三位數流水號
- `<topic>` 使用英文 kebab-case
