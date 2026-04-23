# Workflows

本目錄是跨 skill / subagent workflow artifact 的正式存放位置。

## 目的

- 保存跨 skill handoff 所需的 `plan`、`review-report`、`task`
- 讓人類與 agent 都能在固定位置找到同一批 workflow 資料
- 避免 workflow artifact 散落在 feature 目錄、skill 目錄或臨時文件中

補充：

- 本目錄不只用於程式碼重構，也可用於文件重構、文件補全、與 source-of-truth 校準 workflow
- 當工作先補文件、後做程式碼時，可在同一 workflow 下分成 document stages 與 code stages

## Location Rule

- `workflows/` 目前保留在 `.dev/` 之下，因為它屬於專案知識治理的一部分，不是 build / runtime / deployment artifact
- 它與 `.dev/specs/`、`.dev/operations/`、`.dev/standards/` 共享同一條 knowledge-system 邊界
- 只有當 repo 未來出現獨立的 repo-wide operational workflow system，才再評估是否升格到根目錄

## 建議結構

```text
.dev/workflows/
  <workflow-id>/
    workflow-plan.md
    review-report.md
    tasks/
      <task-id>.json
```

## 命名原則

- `<workflow-id>`: 使用可追蹤的主題名稱，例如 `2026-03-ordering-boundary-cleanup`
- `workflow-plan.md`: 單一 workflow 的 architect plan
- `review-report.md`: 單一 workflow 的正式 review artifact，可承載 architecture、implementation、document、或 workflow review
- `tasks/<task-id>.json`: 單一 stage 或單一 tactical work item

## Templates

- `templates/workflow-plan-template.md`
- `templates/review-report-template.md`
- `templates/workflow-task-template.json`

## 使用原則

- 小任務或單一 skill 任務，不強制建立本目錄內容
- 只有進入 optional workflow mode 時，才建立對應 workflow 資料夾
- 若同一 workflow 有多輪 review，可在 `review-report.md` 中追加輪次，或由使用者明確決定是否拆新 workflow
- workflow 進入實作階段後，不應把全部結果累積到最後一次 commit；每個可驗證、可回顧、可回滾的切片都應形成獨立 commit
- 「可提交切片」至少應滿足：範圍有邊界、主要調整已完成、最小驗證已執行，或已明確記錄無法驗證的原因
- 若 workflow 明顯分 stage，至少每個 stage 結束時都應有對應 commit；若單一 stage 仍很大，應再往下切成較小的 commit checkpoint

## Workflow 觸發條件

符合下列任一條件時，應建立 workflow 目錄：

- 需要兩個以上 stage
- 需要跨 skill handoff
- 需要保存 plan / review / task status
- 需要保存 document refactor 的 decision trail
- 需要整理 source-of-truth，而不是只做單次修改
- 需要在多輪作業中追蹤哪些內容已完成、哪些刻意延後

反之，若只是：

- 單輪分析
- 單次小修
- 單一 skill 任務
- 不需要保留長期上下文

可維持 direct mode，不強制建立 workflow artifact

## 文件工作使用原則

- 若問題核心是 requirement、spec、runbook、context map、event catalog、AI routing 文件不足，應優先建立 document workflow
- document workflow 的 stage 應以知識邊界切分，而不是以程式碼檔案切分
- 若後續需要 code refactor，應在 document stage 補齊最小必要真相後再展開

## Commit Discipline

- workflow commit 的目的，是保留每個中間可用狀態，而不是只在全部做完後一次傾倒
- commit 訊息應反映該切片的邊界，例如 `refactor: migrate product controllers to use case ports`
- 若當前切片尚未完成且無法安全提交，應先縮小切片，而不是延後到整個 workflow 結束再一次提交
- 若驗證受環境限制阻擋，仍應在 workflow artifact 中記錄阻擋原因，並在可獨立審查的範圍內先提交已完成部分

