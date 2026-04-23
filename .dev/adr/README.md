# ADR Governance

本目錄保留作為架構決策治理層，不是日常規則主入口。

## 目錄角色

- 提供 ADR template
- 提供 ADR index
- 說明什麼情況需要新增 ADR
- 保留少量仍有必要的歷史決策脈絡

## Canonical Source Boundary

目前專案的正式規則入口仍是：

- `.dev/ARCHITECTURE.MD`
- `.dev/standards/`
- `.dev/guides/`
- `AGENTS.md`

ADR 的角色是記錄「為什麼做出某個結構性決策」，不是承載日常 implementation 規則。

## 本目錄內容

- `INDEX.md`
  - ADR index 與目前保留狀態
- `ADR-TEMPLATE.md`
  - 新 ADR 樣板
- `WHEN-TO-CREATE-ADR.MD`
  - 何時需要建立 ADR 的判斷規則
- `PORTABILITY-NOTES.MD`
  - 移植到新專案時如何保留本目錄

## Governance Rules

- 新 ADR 只用於重大且跨檔案/跨模組的結構性決策
- 已完整落到 canonical docs 的決策，可只保留簡短索引或直接刪除舊 ADR 內容
- 不要把操作教學、checklist、prompt 本體、或 implementation 細節寫成 ADR
