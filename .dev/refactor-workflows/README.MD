# Refactor Workflows

本目錄是跨 skill 重構 workflow artifact 的正式存放位置。

## 目的

- 保存跨 skill handoff 所需的 `plan`、`review-report`、`task`
- 讓人類與 agent 都能在固定位置找到同一批 workflow 資料
- 避免 workflow artifact 散落在 feature 目錄、skill 目錄或臨時文件中

## 建議結構

```text
.dev/refactor-workflows/
  <workflow-id>/
    refactor-plan.md
    review-report.md
    tasks/
      <task-id>.json
```

## 命名原則

- `<workflow-id>`: 使用可追蹤的主題名稱，例如 `2026-03-ordering-boundary-cleanup`
- `refactor-plan.md`: 單一 workflow 的 architect plan
- `review-report.md`: 單一 workflow 的 reviewer report
- `tasks/<task-id>.json`: 單一 stage 或單一 tactical work item

## 使用原則

- 小任務或單一 skill 任務，不強制建立本目錄內容
- 只有進入 optional workflow mode 時，才建立對應 workflow 資料夾
- 若同一 workflow 有多輪 review，可在 `review-report.md` 中追加輪次，或由使用者明確決定是否拆新 workflow
