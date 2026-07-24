# Workflows

[Workflow Index](INDEX.MD)

本目錄是跨 skill / subagent workflow artifact 的正式存放位置。

跨 model、runtime、host、machine 與 fresh-session 的 machine-readable
checkpoint 統一登錄於 `handoff-checkpoints.yaml`，並依
`.dev/standards/WORKFLOW-HANDOFF-POLICY.md` 驗證。

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

## Discovery 結構

```text
.dev/workflows/
  <workflow-id>/
    workflow.yaml
```

`workflow.yaml` 是固定 locator。真正 artifact 預設放在相同目錄，也可由 workflow-owning skill 宣告其他 repository-relative `artifact_root`。詳細共通契約見 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`。

`INDEX.MD` 是降低認知負載的 discovery view；locator 仍擁有 status、owner、updated time 與 entrypoint。跨 workflow 的 durable 待辦由 `.dev/backlog/` 管理，不應塞入本目錄的 index。

建立新 workflow 時，必須先從預定 base branch 建立獨立 workflow branch，再建立 locator。Codex 預設使用 `codex/<workflow-id>`。Workflow 尚未完成時的 merge/push 只算 checkpoint，不得把 status 改成 completed；push-only 從遠端 workflow branch 接續，checkpoint merge 後才從更新後的 target 建立新的 continuation branch。Workflow branch 預設以 `--no-ff` 合併。

## 命名原則

- `<workflow-id>`：新 workflow 使用 `YYYY-MM-DD-<skill-owned-topic>[-<sequence>]`，例如 `2026-07-10-ordering-boundary-cleanup`
- `workflow.yaml`：固定 discovery locator，記錄 owner、狀態、時間、artifact root 與 entrypoint
- plan、task 與 report 結構：由能建立該類 workflow 的 skill 自行管理
- 舊有 `YYYY-MM-*` workflow 保留歷史名稱，不為形式一致而全面 rename

## Template Ownership

- 本目錄不擁有萬用 workflow template。
- `dev-workflow` 管理 software-development workflow templates。
- `ai-context-governance` 管理 AI context maintenance workflow 與 remediation templates。
- `ai-context-auditor` 管理 audit report templates。
- 其他能建立 workflow 的 skill 應在自己的 canonical skill 目錄宣告 templates、ID 規則與 artifact layout。

## 使用原則

- 小任務或單一 skill 任務，不強制建立本目錄內容
- 進入 workflow mode 時，建立對應 workflow 資料夾
- workflow mode 的判斷以 `.dev/standards/WORKFLOW-GATE-POLICY.md` 為準
- 多輪 review、audit 或 remediation report 是否拆檔，由 owning skill 的 artifact contract 決定；final baseline 不得被後續修正靜默覆寫

## Workflow 觸發條件

符合下列任一條件時，應建立 workflow 目錄：

- 需要兩個以上 stage
- 需要跨 skill handoff
- 需要保存 plan / review / task status
- 需要保存 document refactor 的 decision trail
- 需要整理 source-of-truth，而不是只做單次修改
- 需要在多輪作業中追蹤哪些內容已完成、哪些刻意延後
- 會影響未來 agent 行為、AI context 邊界、skill routing、或 runtime wrapper 結構

詳細 gate 規則見 `.dev/standards/WORKFLOW-GATE-POLICY.md`。

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

