# Refactor Workflow Portability Notes

`.dev/workflows/` 分成兩種內容：

- 可重用的 workflow contract
- 不可重用的歷史 workflow artifact

## 可保留

- `README.MD`
  - workflow artifact 的 canonical contract

## 應刪除

- `<workflow-id>/workflow-plan.md`
- `<workflow-id>/review-report.md`
- `<workflow-id>/tasks/*.json`

除非新專案要直接承接同一件尚未完成的工作，否則這些 artifact 不應隨框架一起移植。

