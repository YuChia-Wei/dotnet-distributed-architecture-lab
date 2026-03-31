# ADR Portability Notes

`.dev/adr/` 可攜移植時要分開看待：

- `README.md`
  - 可保留，因為它定義 ADR 的使用規則
- `INDEX.md`
  - 可保留結構，但內容應依新專案的有效 ADR 重建
- `ADR-*.md`
  - 預設視為 project-specific truth，不應直接複製到新專案

## 移植原則

- 若 ADR 是新專案仍然成立的決策，應重新建立新的 ADR，而不是直接沿用舊編號與舊上下文
- 若 ADR 只是本專案歷史脈絡，移植時應直接刪除
- 不保留無效、重複、已被取代的 ADR
