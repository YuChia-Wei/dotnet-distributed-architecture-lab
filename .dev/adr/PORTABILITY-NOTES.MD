# ADR Governance Portability Notes

`.dev/adr/` 應保留作為 portable governance layer，但不應再攜帶舊專案的決策內容。

## Keep

- `README.md`
- `INDEX.md`
- `ADR-TEMPLATE.md`
- `WHEN-TO-CREATE-ADR.MD`

## Remove or Rewrite

- 任何 `ADR-*.md`
  - 若描述的是舊專案的既有決策，應刪除或重建

## Portable Rule

移植到新專案後：

1. 保留本目錄的治理文件
2. 刪除舊專案的 `ADR-*.md`
3. 只有在新專案真的出現重大結構性決策時，才重新建立新的 ADR
