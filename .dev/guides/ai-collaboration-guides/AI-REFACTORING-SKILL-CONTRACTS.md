# AI Refactoring Skill Contracts

本文件定義四個重構 skill 在 direct mode 與 optional workflow mode 下的最小 input / output contract。

補充：

- 本文件中的「重構」同時包含程式碼重構與文件重構。
- 當目標是補齊 requirement、spec、runbook、context map、AI asset routing 等文件系統時，workflow artifact 仍然適用。
- 只有在 execution step 明確涉及 production code / tests 時，才應使用 code-centric 的切片與驗證語言。

## 目的

- 讓 skill 可以直接使用，不被流程文件綁死
- 讓多 skill 接力時有穩定 handoff
- 明確區分最低必要輸入與建議補充輸入
- 避免 skill 之間因描述模糊而重複判斷或越權

## 使用原則

### Direct Mode

當任務小、單純、由單一 skill 可完成時：

- 可直接呼叫 skill
- 不強制建立 artifact
- 只要提供該 skill 的最低必要輸入

### Workflow Mode

當任務跨 skill、跨 stage、或需要保存決策時：

- 使用 `workflow-plan.md`
- 使用 `review-report.md`
- 使用 `tasks/<task-id>.json`
- 預設存放於 `.dev/workflows/<workflow-id>/`
- artifact 欄位應至少滿足本文件的最小 contract

常見 workflow mode 類型：

- code refactor workflow
- document refactor workflow
- mixed workflow（先補文件真相，再進入 code stage）

## Artifact 與 Skill 對應

| Artifact | Owner Skill | 主要用途 |
| :--- | :--- | :--- |
| `workflow-plan.md` | `ddd-ca-hex-architect` | 保存診斷、目標方向、stages、非目標、風險，可用於 code 或 document workflow |
| `review-report.md` | `code-reviewer` | 保存正式 review 結果，可承載 architecture、implementation、documentation、workflow findings 與建議下一步 |
| `tasks/<task-id>.json` | `staged-refactor-implementer` / `tactical-refactor-implementer` | 保存單一 workflow task 的執行 scope、限制、驗證、結果，可承載 code、document、或 mixed stage |

## Artifact 存放位置

Workflow artifact 的正式存放根目錄為：

- `.dev/workflows/`

每個 workflow 應使用獨立資料夾：

- `.dev/workflows/<workflow-id>/workflow-plan.md`
- `.dev/workflows/<workflow-id>/review-report.md`
- `.dev/workflows/<workflow-id>/tasks/<task-id>.json`

若 task 不只一個，應放在同一個 `tasks/` 子目錄下，而不是散落在其他路徑。

## 文件重構補充規則

當 workflow 目標是文件系統時：

- stage 應以 source-of-truth 邊界切分，而不是以程式碼模組切分
- validation 應優先檢查完整性、一致性、權責清楚度、與維護情境覆蓋
- non-goals 應明確防止「順手把 code 也一起改掉」
- 若文件缺口會影響後續 code refactor，應先完成文件 stage，再啟動 code stage

常見 document stage 類型：

- workflow definition / governance
- inventory and gap mapping
- terminology normalization
- requirement completion
- spec completion
- runtime operations documentation
- AI asset alignment

## `ddd-ca-hex-architect`

### 最低必要輸入

- 問題描述
- 目前 scope
- 主要限制條件

### 建議補充輸入

- 現行模組結構
- 相關 ADR
- 既有混亂點或 smell
- 是否已有 reviewer findings

### 最低必要輸出

- 架構診斷
- 目標方向
- 建議下一步使用哪個 skill

### 若進入 Workflow Mode，至少應寫入 `workflow-plan.md`

- `plan_id`
- `owner_skill`
- `status`
- `Problem statement`
- `Current scope`
- `Target architecture summary`
- `Key constraints`
- `Non-goals`
- 至少一個 `Stage`
- `Recommended implementer`

若是 document workflow，建議另外明確寫出：

- 文件邊界或知識域
- source of truth 放置位置
- 文件完成定義（definition of done）

## `code-reviewer`

### 最低必要輸入

- reviewed target
- review reason

### 建議補充輸入

- 明確檔案或模組清單
- 相關測試或使用情境
- 是否已有 architect plan

### 最低必要輸出

- review score
- architecture-level findings
- code-level findings 或 doc-level findings
- recommended next skill

### 若進入 Workflow Mode，至少應寫入 `review-report.md`

- `report_id`
- `owner_skill`
- `review_kind`
- `Reviewed target`
- `Review reason`
- `Review boundaries`
- `Architecture Compliance`
- `Implementation Quality`、`Documentation Quality`、`Workflow Integrity` 至少擇一適用欄位
- `Test Adequacy`
- 至少一筆 architecture-level、implementation-level、doc-level、或 workflow-level finding
- `Decision`
- `Recommended Next Skill`

補充：

- `review-report.md` 是 workflow review artifact，不限於純 code review
- 若本輪是文件或治理工作，應優先填寫 document / workflow findings，而不是硬塞 code-level 欄位

## `staged-refactor-implementer`

### 最低必要輸入

- stage goal
- target scope
- constraints

### 建議補充輸入

- `workflow-plan.md`
- `review-report.md`
- 驗證要求
- 明確 non-goals

### 最低必要輸出

- 本輪要處理的 safe slice
- 執行限制
- 驗證方式
- deferred items

### 若進入 Workflow Mode，至少應寫入對應的 `tasks/<task-id>.json`

- `task_id`
- `owner_skill`
- `status`
- `scope.target`
- `scope.constraints`
- `scope.non_goals`
- `inputs.architecture_target`
- `execution.operation_type`
- `execution.steps`
- `execution.validation`

若是 document workflow，建議：

- `scope.target` 以文件系統、知識域、或 source-of-truth slice 表示
- `execution.operation_type` 使用如 `workflow-definition`、`documentation-analysis`、`terminology-normalization`、`document-completion`
- `execution.validation` 明確描述 completeness / consistency / maintainability checks

## `tactical-refactor-implementer`

### 最低必要輸入

- 單一主要目標
- 局部操作目標
- 可接受依賴半徑

### 建議補充輸入

- 是否僅限 local rename / extract method
- 不能動的檔案或邊界
- 是否已有 architect 覆核

### 最低必要輸出

- 局部變更摘要
- 觸及的直接依賴
- 驗證方式
- 超出範圍而被延後的項目

### 若進入 Workflow Mode，至少應寫入對應的 `tasks/<task-id>.json`

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

### Architect -> Reviewer

- reviewer 至少要知道：
  - 哪個 stage 或哪個目標區塊需要 review
  - 哪些限制是 architect 已經定義好的
  - 哪些議題仍然開放

### Reviewer -> Implementer

- implementer 至少要知道：
  - 哪些問題是 architecture-level
  - 哪些問題是 code-level 或 doc-level
  - 這一輪應優先處理哪些 finding
  - reviewer 建議下一步交給哪個 skill

### Architect / Reviewer -> Staged Implementer

- staged implementer 不應自行補完以下缺口：
  - 模糊的 stage goal
  - 未定義的 non-goals
  - 未說明的相容性要求
  - 未限制的 scope expansion

### Architect / Reviewer -> Tactical Implementer

- tactical implementer 不應自行升級成：
  - extract class
  - extract interface
  - semantic rename
  - cross-module structural refactor

## Contract 最小化原則

- 沒有跨 skill handoff 時，不強制建立 artifact
- 建立 artifact 時，只要求最小欄位
- 缺欄位時，應先補充必要資訊，而不是讓 skill 自行猜測
- contract 的目的在於交接，不在於增加行政負擔

## 相關文件

- `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`
- `../workflows/README.MD`
- `templates/refactor-plan-template.md`
- `templates/review-report-template.md`
- `templates/refactor-task-template.json`

