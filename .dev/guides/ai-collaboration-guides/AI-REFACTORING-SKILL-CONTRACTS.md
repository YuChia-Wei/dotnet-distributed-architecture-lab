# AI Implementation Skill Contracts

本文件定義 architecture / review / implementer 在 direct mode 與 optional workflow mode 下的最小 input / output contract。

雖然檔名仍保留 refactoring 字樣，原因是維持既有 guide link；現行內容以 scope-first implementer taxonomy 為準。

## 目的

- 讓 skill 可以直接使用，不被流程文件綁死。
- 讓多 skill 接力時有穩定 handoff。
- 明確區分最低必要輸入與建議補充輸入。
- 避免 skill 之間因描述模糊而重複判斷或越權。

## 使用原則

### Direct Mode

當任務小、單純、由單一 skill 可完成時：

- 可直接呼叫 skill。
- 不強制建立 artifact。
- 只要提供該 skill 的最低必要輸入。

### Workflow Mode

當任務跨 skill、跨 stage、或需要保存決策時：

- 先建立 `codex/<workflow-id>` 或 runtime 對應的獨立 branch。
- 建立 `.dev/workflows/<workflow-id>/workflow.yaml` locator。
- 使用 `workflow-plan.md`。
- 需要正式 development review 時使用 `review-report.md`。
- 使用 `tasks/<task-id>.json`。
- 新 workflow ID 使用 `YYYY-MM-DD-<topic>[-NN]`。
- artifact 預設存放於 `.dev/workflows/<workflow-id>/`，也可由 `software-development-orchestrator` template 宣告其他 repository-relative root；locator 始終保留於 `.dev/workflows/`。
- locator 與 task 的共通欄位遵循 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`；development artifact body 使用 `software-development-orchestrator` 自有 templates。
- Workflow branch 預設以 `--no-ff` 合併；未完成時的 merge/push 保留 active/pending，並分別記錄 pushed branch 或 merge 後的 continuation branch。

## Artifact 與 Skill 對應

| Artifact | Owner Skill | 主要用途 |
| :--- | :--- | :--- |
| `workflow.yaml` | `software-development-orchestrator` | 固定 locator；保存 workflow ID、owner、status、artifact root、entrypoint 與時間 |
| `workflow-plan.md` | `software-development-orchestrator` 建立；`ddd-ca-hex-architect` 可更新 architecture sections | 保存 development objective、目標方向、stages、非目標與風險 |
| `review-report.md` | `code-reviewer` 或對應 development reviewer | 保存 architecture、implementation、test 或 development workflow review findings |
| `tasks/<task-id>.json` | `slice-implementer` / `local-change-implementer` | 保存單一 development task 的 scope、限制、驗證與結果 |

## AI Context 與純文件治理邊界

本 contract 只適用 software/product development lifecycle。當 workflow 核心是 AI context 或純文件治理：

- AI context 自檢使用 `ai-context-auditor`。
- AI context 修正與 audit-remediation lifecycle 使用 `ai-context-governance`。
- 使用 owner skill 自有 template，不套用本文件的 development template。
- 若治理結果形成後續 development input，再以新的或已宣告關聯的 development workflow 接續。

## `ddd-ca-hex-architect`

最低必要輸入：

- 問題描述。
- 目前 scope。
- 主要限制條件。

最低必要輸出：

- 架構診斷。
- 目標方向。
- 建議下一步使用哪個 skill。

若進入 workflow mode，至少應寫入：

- `workflow_id`
- `plan_id`
- `owner_skill`
- `status`
- `created_at`
- `updated_at`
- `template_source`
- `template_version`
- problem statement
- current scope
- target architecture summary
- constraints
- non-goals
- stage 或 slice plan

## `code-reviewer`

最低必要輸入：

- reviewed target。
- review reason。

最低必要輸出：

- review score。
- architecture-level findings。
- code-level、doc-level、或 workflow-level findings。
- recommended next skill。

## `slice-implementer`

最低必要輸入：

- slice goal。
- source truth。
- target scope。
- mode or intent。
- constraints and non-goals。

建議補充輸入：

- `workflow-plan.md`
- `review-report.md`
- `tasks/<task-id>.json`
- validation requirements

最低必要輸出：

- 本輪完成的 bounded slice。
- 使用的 mode reference。
- 變更檔案。
- 驗證方式。
- deferred items 或 handoff notes。

若進入 workflow mode，對應 task 至少應包含：

- `task_id`
- `workflow_id`
- `owner_skill`
- `status`
- `created_at`
- `updated_at`
- `template_source`
- `template_version`
- `scope.target`
- `scope.constraints`
- `scope.non_goals`
- `execution.operation_type`
- `execution.mode`
- `execution.steps`
- `execution.validation`

## `local-change-implementer`

最低必要輸入：

- 單一主要目標。
- 局部操作目標。
- 可接受依賴半徑。

最低必要輸出：

- 局部變更摘要。
- 觸及的直接依賴。
- 驗證方式。
- 超出範圍而被延後的項目。

若進入 workflow mode，對應 task 至少應包含：

- `task_id`
- `owner_skill`
- `status`
- `scope.target`
- `scope.files`
- `scope.dependency_radius`
- `scope.constraints`
- `execution.operation_type`
- `execution.steps`
- `execution.validation`
- `execution.deferred_items`

## 交接規則

### Architect -> Implementer

`slice-implementer` 至少要知道：

- 這一輪 slice 的目標。
- 哪些邊界已經決定。
- 哪些內容是 non-goal。
- 若有 command / query / reactor 語意，應使用哪個 mode reference。

### Reviewer -> Implementer

implementer 至少要知道：

- 哪些問題是 architecture-level。
- 哪些問題是 code-level、doc-level、或 workflow-level。
- 這一輪應優先處理哪些 finding。
- reviewer 建議下一步交給哪個 skill。

### Slice -> Local Change

`local-change-implementer` 只接收可局部處理的技術變更。若需要新增 class/interface、改 domain language、改 DTO/API/event 名稱、或跨 module boundary，必須回到 `slice-implementer` 或 `ddd-ca-hex-architect`。

## Contract 最小化原則

- 沒有跨 skill handoff 時，不強制建立 artifact。
- 建立 artifact 時，只要求最小欄位。
- 缺欄位時，應先補充必要資訊，而不是讓 skill 自行猜測。
- contract 的目的在於交接，不在於增加行政負擔。

## 相關文件

- `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`
- `../workflows/README.MD`
- `../../../.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `../../../.ai/assets/skills/software-development-orchestrator/templates/development-review-report-template.md`
- `../../../.ai/assets/skills/software-development-orchestrator/templates/development-workflow-task-template.json`
