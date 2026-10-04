# Workflows

[Workflow Index](INDEX.MD)

本目錄保存既有跨 skill / subagent 的 plan、review、task 與執行證據。
新工作依 [AGENTS.md](../../AGENTS.md)、本次授權範圍及選定 owning skill
的實際操作與輸出契約進行；需要保存紀錄時，再選定該次工作的存放位置。

跨 model、runtime、host、machine 或 fresh-session 接續工作時，可在選定紀錄
留下已完成事項、未完成事項、精確下一步與驗證限制。
舊 framework 的 workflow／handoff 驗證程式已退役，目前沒有對應的自動 gate；
既有紀錄保留原格式，不能把文件檢查當成程式執行或驗收通過。

## 既有紀錄

- 本目錄包含程式碼與文件工作的 `plan`、`review-report`、`task` 及證據。
- 紀錄保留在 `.dev/`，屬於專案知識，並非 build / runtime / deployment artifact。
- 舊有名稱、格式、身分與原始結論維持其歷史範圍。

既有 locator 的常見位置：

```text
.dev/workflows/
  <workflow-id>/
    workflow.yaml
```

含有 `workflow.yaml` 的紀錄，以該檔案讀取當時的 status、owner、updated time、
artifact root 與 entrypoint。這是既有紀錄的導航方式，不是新工作的必備 schema。

2026-09-29 的資料遷移已將兩筆 software-development-orchestrator 主紀錄整合回各自既有的主題目錄：`workflow-plan.md` 為人類閱讀入口，`tasks/<原 task ID>.json` 保留任務與依賴，`migration-map.md` 對照 acceptance、decision、evidence、reference ID。前端 `evidence/v2-source.workflow.json` 保存原始位元組；採購 `evidence/v2-history.workflow.json` 保存路徑改指向 tracked 證據後的完整歷史，其原始位元組留在 Git 歷史。RC1 pilot 的第三筆 v2 紀錄是支援性證據，保留於其原有 AI-context workflow 的 `evidence/`，沒有升格為第二個主 workflow。舊 store 的導覽已由負責人移除；保留的 migration-map 與 evidence 記錄當時遷移，不是目前 portable skill 或 store 的啟用指示。

`INDEX.MD` 是 discovery view；請回到具體紀錄核對狀態與證據。
既有紀錄或待辦本身不授權後續修改。

## 後續有限任務

- 依 `AGENTS.md` 選擇需要的 skill；`software-development-orchestrator` 可協調階段與專業 skill，入口存在不代表提供紀錄 store 或通用 template。
- AI context maintenance 與 audit 分別使用選定的 `ai-context-governance`、`ai-context-auditor`，依該次任務與實際 output contract 決定是否保存紀錄。
- 只執行已授權且與問題相關的檢查，記錄實際結果、未執行項目與限制。
- 紀錄完成、runtime 驗收、commit、push、PR 與整合是不同狀態，依實際請求及證據分開回報。
