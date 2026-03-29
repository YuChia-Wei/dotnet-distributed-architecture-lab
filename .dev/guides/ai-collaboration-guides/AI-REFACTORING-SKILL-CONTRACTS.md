# AI Refactoring Skill Contracts

本文件定義四個重構 skill 在 direct mode 與 optional workflow mode 下的最小 input / output contract。

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

- 使用 `refactor-plan.md`
- 使用 `review-report.md`
- 使用 `refactor-task.json`
- 預設存放於 `.dev/refactor-workflows/<workflow-id>/`
- artifact 欄位應至少滿足本文件的最小 contract

## Artifact 與 Skill 對應

| Artifact | Owner Skill | 主要用途 |
| :--- | :--- | :--- |
| `refactor-plan.md` | `ddd-ca-hex-architect` | 保存診斷、目標方向、stages、非目標、風險 |
| `review-report.md` | `code-reviewer` | 保存評分、architecture/code findings、建議下一步 |
| `refactor-task.json` | `staged-refactor-implementer` / `tactical-refactor-implementer` | 保存執行 scope、限制、驗證、結果 |

## Artifact 存放位置

Workflow artifact 的正式存放根目錄為：

- `.dev/refactor-workflows/`

每個 workflow 應使用獨立資料夾：

- `.dev/refactor-workflows/<workflow-id>/refactor-plan.md`
- `.dev/refactor-workflows/<workflow-id>/review-report.md`
- `.dev/refactor-workflows/<workflow-id>/tasks/<task-id>.json`

若 task 不只一個，應放在同一個 `tasks/` 子目錄下，而不是散落在其他路徑。

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

### 若進入 Workflow Mode，至少應寫入 `refactor-plan.md`

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
- code-level findings
- recommended next skill

### 若進入 Workflow Mode，至少應寫入 `review-report.md`

- `report_id`
- `owner_skill`
- `Reviewed target`
- `Review reason`
- `Architecture Compliance`
- `Code Quality`
- `Test Adequacy`
- 至少一筆 architecture-level 或 code-level finding
- `Recommended Next Skill`

## `staged-refactor-implementer`

### 最低必要輸入

- stage goal
- target scope
- constraints

### 建議補充輸入

- `refactor-plan.md`
- `review-report.md`
- 驗證要求
- 明確 non-goals

### 最低必要輸出

- 本輪要處理的 safe slice
- 執行限制
- 驗證方式
- deferred items

### 若進入 Workflow Mode，至少應寫入 `refactor-task.json`

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

### 若進入 Workflow Mode，至少應寫入 `refactor-task.json`

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
  - 哪些問題是 code-level
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
- `../refactor-workflows/README.MD`
- `templates/refactor-plan-template.md`
- `templates/review-report-template.md`
- `templates/refactor-task-template.json`
