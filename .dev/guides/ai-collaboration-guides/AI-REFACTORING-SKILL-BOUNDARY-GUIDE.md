# AI Refactoring Skill Boundary Guide

本文件定義四個重構相關 skill 的責任邊界：

- `ddd-ca-hex-architect`
- `code-reviewer`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`

## 短結論

把這四個 skill 想成四種不同角色：

- `ddd-ca-hex-architect`: 決定應該怎麼重構
- `code-reviewer`: 指出現在哪裡有問題
- `staged-refactor-implementer`: 依據既定方向，分階段把重構做出來
- `tactical-refactor-implementer`: 在單一主要目標周圍做局部結構整理

它們不是互相取代，而是組成一條完整工作流。

## 核心分工

| Skill | 主要任務 | 主要輸入 | 主要輸出 | 不該做的事 |
| :--- | :--- | :--- | :--- | :--- |
| `ddd-ca-hex-architect` | 架構診斷、目標設計、切分策略 | 現況描述、模組結構、ADR、需求、混亂點 | 目標架構、重構切片、優先順序、風險 | 直接大規模修改 code |
| `code-reviewer` | 程式碼規則審查、違規點盤點、評分 | 具體檔案、模組、測試、實作片段 | 評分、CRITICAL / MUST FIX / SHOULD FIX findings、architecture-level / code-level 標記 | 代替架構規劃、代替實作、代替 refactor planning |
| `staged-refactor-implementer` | 依計畫逐步重構與落地 | 架構計畫、review findings、目標 slice、驗證要求 | 小步驟實作、檔案變更、測試更新、後續待辦 | 自行發明全新架構方向或跳過驗證一次大改 |
| `tactical-refactor-implementer` | 物件中心、局部結構重整 | 單一主要目標、局部問題、可接受依賴半徑 | 局部重構變更、直接依賴更新、局部 rename/extract 結果 | 代替 stage planning 或 architecture redesign |

## 何時該用哪個 Skill

### 用 `ddd-ca-hex-architect`

當你要回答的是：

- 這個 legacy 專案應該從哪裡開始重構
- 哪些 module boundary / aggregate boundary 錯了
- 應該怎麼切 bounded context、ports、adapters
- 哪些改動應該分成多個 stage

### 用 `code-reviewer`

當你要回答的是：

- 這個檔案現在有什麼問題
- 哪些違規是局部實作問題，哪些是架構層級問題
- 這次重構後是否仍違反規範

它的輸出應停留在：

- 找問題
- 分類問題
- 評分
- 標記問題嚴重度

它不應該負責：

- 決定目標架構
- 切 staged refactoring plan
- 排實作順序

### 用 `staged-refactor-implementer`

當你已經有：

- 一個明確的重構目標
- 一份架構方向或 staged plan
- 一批 review findings

並且你要：

- 逐步修改 code
- 保持行為相容
- 控制變更範圍
- 每個 stage 都可驗證、可 review

### 用 `tactical-refactor-implementer`

當你要回答的是：

- 這個 class 是否該抽方法
- 這個名稱是否該在局部範圍內 rename
- 這個物件周圍是否能做一次小範圍整理

它應該只碰：

- 一個主要目標
- 直接依賴
- 必要呼叫點

它不應該自行決定：

- 抽類別
- 抽介面
- 影響 ubiquitous language 或邊界語意的 rename

## 推薦工作流

```text
1. ddd-ca-hex-architect
   做全域診斷與切片策略

2. code-reviewer
   對第一批目標區塊做具體審查與評分

3. staged-refactor-implementer
   依據計畫與 findings 實作第一個 safe slice

4. tactical-refactor-implementer
   在某個 slice 內處理局部 extract-method / local-rename 整理

5. code-reviewer
   檢查這一輪實作後是否真的收斂

6. ddd-ca-hex-architect
   視需要調整後續 stage 的設計
```

## 標準重構流程

把這份文件當成架構層級的標準流程即可：

1. 用 `ddd-ca-hex-architect` 做全域診斷，先定義問題、目標結構與切片順序
2. 用 `code-reviewer` 盤點第一批目標區塊的具體 code-level 問題
3. 用 `staged-refactor-implementer` 只落地一個 safe slice
4. 再用 `code-reviewer` 驗證這一輪是否真的收斂，而不是只是換一種混亂
5. 視結果回到 `ddd-ca-hex-architect` 調整下一輪 stage

如果要把這套流程帶去既有專案，優先帶走的應該是這個流程本身，而不是直接照搬所有 repo-specific prompt。

## Optional Workflow Mode

這四個 skill 預設都可以直接使用，不必每次都走流程文件。

但如果任務會跨 skill 接力，建議啟用「可選的最小 workflow 模式」：

- `workflow-plan.md`
- `review-report.md`
- `tasks/<task-id>.json`

用途不是增加流程，而是讓 skill 間 handoff 更穩定。
詳細規則與模板見：

- `AI-REFACTORING-SKILL-CONTRACTS.md`
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`
- `templates/workflow-plan-template.md`
- `templates/review-report-template.md`
- `templates/workflow-task-template.json`

## Sub-agent Collaboration

當任務由 sub-agent 協作完成時，仍應遵守這四個 refactor skill 的責任邊界。

- generation 類 sub-agent:
  - 可作為 stage 內的執行幫手
  - 不應自行宣告新的 architecture direction
- review 類 sub-agent:
  - 可提供審查觀點
  - 若需要正式 score / findings / next-skill recommendation，應對齊 `code-reviewer`
- 一般 sub-agent:
  - 預設只讀 workflow artifact
  - 只有在任務明確要求更新 task 狀態或結果時，才可寫入既有 `tasks/<task-id>.json`

若 sub-agent 在執行途中發現：

- 需要 extract class / extract interface
- 需要 semantic rename
- 需要重切 module / aggregate / bounded context

則應停止擴張，交回 `ddd-ca-hex-architect`。

## Decision Tree

### 問題是「應該改成什麼樣子」嗎？

用 `ddd-ca-hex-architect`

### 問題是「現在這段 code 到底錯在哪裡」嗎？

用 `code-reviewer`

### 問題是「依照既定設計，把這一小段重構做出來」嗎？

用 `staged-refactor-implementer`

### 問題是「以單一物件或類別為中心，做抽方法 / 局部 rename」嗎？

用 `tactical-refactor-implementer`

### 問題涉及抽類別、抽介面，或語意型 rename 嗎？

先用 `ddd-ca-hex-architect` 覆核，再視規模交給 `staged-refactor-implementer` 或 `tactical-refactor-implementer`

## 不建議的混用方式

### 讓 `code-reviewer` 直接當重構執行者

這會讓 review 與 implementation 混在一起，容易失去檢查獨立性。

### 讓 `code-reviewer` 直接當 refactor planner

這會讓 review skill 越權，從「指出問題」變成「決定怎麼改」，使 architecture planning 與 review 判斷混在一起。

## Architecture-Level vs Code-Level

在這套流程裡，`code-reviewer` 可以標記 architecture-level 問題，但不負責解它。

- architecture-level:
  - boundary leakage
  - command/query mixing
  - wrong layer placement
  - dependency direction violations
  - repository role misuse

- code-level:
  - missing guards
  - mapper defects
  - test gaps
  - local implementation bugs
  - naming and organization issues

當 `code-reviewer` 發現 architecture-level 問題時，下一步應交回 `ddd-ca-hex-architect`。
當問題已經有明確方向，只差落地時，下一步應交給 `staged-refactor-implementer`。

## Rename Decision Rule

不是所有 rename 都要先經過 architect，但要先分辨兩種：

- local rename:
  - 只改善單一類別、方法、欄位、局部符號可讀性
  - 不改變 bounded context、DTO、API、event、domain language
  - 可交給 `tactical-refactor-implementer`

- semantic rename:
  - 影響 ubiquitous language
  - 影響 DTO / API / event / boundary naming
  - 可能反映商業詞彙改版或領域語意變更
  - 先交給 `ddd-ca-hex-architect` 覆核

### 讓 `ddd-ca-hex-architect` 直接處理所有 code edits

這會讓架構規劃與落地執行混在一起，通常會造成切片不夠小、風險過高。

### 讓 `staged-refactor-implementer` 自己決定最終架構

這會讓實作 skill 越權，變成邊做邊改方向，最後失去可控性。

### 讓 `tactical-refactor-implementer` 擴張成多模組重構

這會讓局部重構 skill 越權，從 tactical cleanup 滑向 stage-level 或 architecture-level refactor。

## 適合帶去既有專案的東西

最適合跨專案移植的是：

- 四 skill 的邊界分工
- staged refactoring workflow
- 先 architect / 再 review / 再 implement / 再 validate 的節奏

較不適合直接照搬的是：

- 綁這個 repo 的 ADR 路徑
- 綁 WolverineFx / Outbox / project-config 的實作細節
- 綁特定資料夾命名的 code generation 規則

## 相關文件

- `DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`
- `STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
- `TACTICAL-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
- `AI-SKILL-GUIDE-STANDARDS.md`


