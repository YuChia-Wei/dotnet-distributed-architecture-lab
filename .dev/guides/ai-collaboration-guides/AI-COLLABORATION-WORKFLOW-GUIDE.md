# AI Collaboration Workflow Guide

本文件說明這個 repo 目前建議的 AI 協作作業流程。

它不是單一 skill 的使用說明，而是整理：

- 什麼類型的工作應先從哪份文件開始
- 應該先用哪個 skill 或 prompt
- 何時需要 workflow mode
- 何時適合引入 subagent

若任務本身是「規劃並驅動多階段 software/product development」，使用 `dev-workflow`。它負責 development direct/workflow mode、開發 skill routing、validation 與 commit checkpoint。其他多階段作業由其 domain owner skill 建立並管理 workflow；例如 AI context lifecycle 使用 `ai-context-governance`，不再經由 `dev-workflow` 統籌。

## 核心原則

- 先建立對人與 AI 都可讀的文件，再進入生成或重構
- 小任務優先 direct mode
- 多 skill handoff 才進 workflow mode
- skill 負責專業角色，subagent 負責在既定邊界內協作

補充：

- `workflow mode` 不只適用於程式碼重構，也適用於文件補全、文件重構與 source-of-truth 校準；但 template 與 orchestration owner 必須依 workflow kind 選擇
- 若程式碼問題本質上來自文件缺口，應先進 document workflow，再決定是否展開 code workflow
- AI context、prompt 邊界、skill routing、wrapper sync、README language policy 這類文件治理工作，使用 `ai-context-governance`
- `bdd-gwt-test-designer` 只負責測試意圖、Given-When-Then scenario 與 assertion plan，不負責 AI context cleanup 或 test code generation

## 主要文件入口

### 需求與規格

- `.dev/requirement/`
  - functional / non-functional requirement docs
- `.dev/specs/`
  - use case / adapter / entity / aggregate specs

### 測試設計

- `bdd-gwt-test-designer`
  - 將 requirement / spec 拆成 Given-When-Then scenarios

### 重構交接

- `.dev/workflows/`
  - `<workflow-id>/workflow.yaml`：固定 locator
  - 由 locator 指向 owning skill 定義的 artifact root 與 entrypoint
  - development workflow 通常包含 `workflow-plan.md`、`tasks/<task-id>.json` 與選用的 `review-report.md`

## 流程 1：需求驅動開發

適用於：

- 新功能
- 新 use case
- 新 API / reactor / aggregate 行為
- 需求先於程式碼存在

建議流程：

```text
1. requirement
2. spec
3. architecture clarification if needed
4. BDD GWT test design
5. test generation / implementation
6. code review
```

### Step 1: requirement

若需求仍然模糊，先整理到：

- `.dev/requirement/`

參考：

- `.dev/requirement/requirement-guide.md`
- `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY.md`

### Step 2: spec

當 requirement 已明確後，展開到：

- `.dev/specs/`

參考：

- `.dev/specs/SPEC-GUIDE.md`
- `.dev/specs/SPEC-ORGANIZATION-GUIDE.md`

### Step 3: architecture clarification

若 requirement / spec 過程中出現：

- aggregate 邊界不清
- MQ / API / domain role 不清
- 命名語意衝突

先交給：

- `ddd-ca-hex-architect`

### Step 4: BDD GWT test design

用：

- `bdd-gwt-test-designer`

產出：

- Given-When-Then scenarios
- assertion points
- test level recommendation

### Step 5: test generation / implementation

依情境交給：

- `slice-implementer`
  - command use case mode
  - query use case mode
  - reactor mode
  - generic slice mode
- `local-change-implementer` when the task is only a local class, object, method, symbol, SQL/ORM, or direct-call-site change
- 或既有 test generation prompt / subagent

### Step 6: code review

最後交給：

- `code-reviewer`

確認：

- 規範符合
- coverage 與 assertions 合理
- implementation 沒有偏離 requirement / spec

## 流程 2：重構驅動開發

適用於：

- legacy cleanup
- architecture correction
- staged refactoring
- test-first 補強後再重構
- 文件系統補全或 source-of-truth 重整

建議流程：

```text
1. architecture diagnosis
2. review findings
3. slice or local execution
4. review again
5. iterate if needed
```

### Step 1: architecture diagnosis

用：

- `ddd-ca-hex-architect`

決定：

- 問題在哪裡
- 目標方向
- 是否要切 stage

### Step 2: review findings

用：

- `code-reviewer`

產出：

- architecture-level findings
- code-level findings 或 doc-level findings
- score
- next-skill recommendation

### Step 3: execution

依範圍交給：

- `slice-implementer`
  - bounded feature, fix, review remediation, refactor, or documentation slice
- `local-change-implementer`
  - one local class, object, method, symbol, SQL/ORM, or direct-call-site technical change

若是 document workflow，execution 應優先使用下列切法：

- 以文件邊界切 stage，例如 requirement、spec、runbook、AI asset alignment
- 以 source-of-truth 問題切 stage，例如 terminology normalization、ownership clarification、gap map
- 避免把「文件補全 + code cleanup + prompt cleanup」混成同一輪

### Task Artifact 執行原則

若工作明確提供 `task-*.json`、workflow task artifact 或 stage task JSON：

- 必須先讀 task
- 先確認 required steps / postChecks / expected outputs
- 完成後更新對應 status 與 results

不要因看到關鍵字就直接執行而跳過 artifact 內容。

### Step 4: review again

再回到：

- `code-reviewer`

確認這一輪有沒有真的收斂。

## Direct Mode vs Workflow Mode

### Direct Mode

適合：

- 單一 skill 任務
- 小範圍局部修改
- 不需要保存跨輪上下文

例子：

- 單次 code review
- 單次 extract method
- 直接從 spec 拆 GWT scenarios

### Workflow Mode

適合：

- 多 skill handoff
- 多輪 stage
- 需要保存 architecture / review / task 狀態
- 需要保存文件真相與補全決策

明確觸發條件：

- 工作預期會分成兩個以上 stage
- 工作同時涉及 architect / reviewer / implementer 類型 handoff
- 需要在多輪作業間保留 decision trail
- 需要追蹤 `plan`、`review`、`task status` 或 stage results
- 問題本質是文件系統重整、source-of-truth 校準、ADR 整理、spec 補全、operations 補全
- 預期會更新多個知識邊界，而不是單一小檔案

若符合上述任一條件中的強訊號，應建立完整日期 workflow locator：

- `.dev/workflows/<YYYY-MM-DD-topic[-NN]>/workflow.yaml`

建立 locator 前，先從預定 base branch 建立獨立 workflow branch；Codex 預設為 `codex/<workflow-id>`。Locator 必須記錄 `branch`、`base_branch`。Workflow merge 預設使用 `--no-ff`。

Locator 固定記錄 owner skill、status、artifact root、entrypoint、`created_at` 與 `updated_at`。真正 artifact layout 與 template 由建立該類 workflow 的 skill 管理：

- software/product development lifecycle → `dev-workflow`
- AI context 自檢 → `ai-context-auditor`
- AI context 文件治理、整改與複檢結案 → `ai-context-governance`
- framework 複製後的 repo 初始化 → `repo-structure-sync`

artifact 預設放在 locator 同目錄；owner skill 也可宣告其他 repository-relative `artifact_root`。不要假設所有 workflow 都具有下列同名檔案。Development workflow 通常使用：

- `workflow-plan.md`
- `tasks/<task-id>.json`
- `review-report.md`（需要正式 development review 時）

對 document workflow 來說，先依 source-of-truth 判斷 owner skill，再由其 artifact 回答：

- 哪一類文件是 source of truth
- 這一輪補的是哪個知識缺口
- 完成後可以支撐哪一種維護情境
- 哪些內容刻意延到下一 stage

若使用者在 workflow 未完成時要求 merge/push，將它記為 checkpoint handoff，不得直接標記 completed。Push-only 時從已推送的 workflow branch 接續；checkpoint merge 後才從更新後的 target 建立新的 continuation branch，再更新 locator 後繼續。

### Practical Trigger Rule

可用以下判斷快速決定是否進 workflow mode：

- 如果這件事只是一次分析或一次小修，留在 direct mode
- 如果這件事需要「盤點 -> 分類 -> 補標準 -> 清理遺留」，就應進 workflow mode
- 如果你已經開始問「這件事要不要分 stage」，通常答案就是要進 workflow mode

## Subagent 介入原則

subagent 適合：

- 在既定邊界內平行處理 generation / test / review 工作
- 消費既有 requirement / spec / workflow artifact

subagent 不應：

- 自行發明 architecture direction
- 自行改寫 requirement 的商業意圖
- 自行把局部整理擴張成結構重構

若 subagent 遇到：

- 邊界不清
- semantic rename
- extract class / extract interface
- 多模組重構擴張

應回到：

- `ddd-ca-hex-architect`
或
- `code-reviewer`

## 推薦心智模型

把整套流程理解成三層：

### 上游設計層

- requirement
- spec
- architect
- BDD GWT test design

### 中游執行層

- test generation
- bounded slice implementation
- local technical change
- 一般 generation subagents

### 下游驗證層

- code review
- spec compliance
- test validation

## 相關文件

- `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY.md`
- `DEV-WORKFLOW-SKILL-GUIDE.md`
- `BDD-GWT-TEST-DESIGNER-SKILL-GUIDE.md`
- `BDD-GWT-TEST-DESIGNER-PAIR-GUIDE.md`
- `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`
- `../workflows/README.MD`

