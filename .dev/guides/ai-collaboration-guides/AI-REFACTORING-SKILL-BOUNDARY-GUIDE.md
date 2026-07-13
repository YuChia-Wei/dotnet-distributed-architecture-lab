# AI Implementation Skill Boundary Guide

本文件定義 architecture / review / implementer skill 的責任邊界。

雖然檔名仍保留 refactoring 字樣，原因是維持既有 guide link；現行 taxonomy 已改為 scope-first implementer，不再以 refactor 作為 implementer 命名主軸。

## 短結論

- `ddd-ca-hex-architect`: 決定架構方向、邊界、切片策略。
- `code-reviewer`: 找出問題、評分、分類 findings。
- `slice-implementer`: 落地一個 bounded slice，包含 feature、fix、review remediation、refactor、documentation slice。
- `local-change-implementer`: 落地一個 local class、object、method、symbol、SQL/ORM、或 direct-call-site 技術變更。

`slice-implementer` 是一般實作入口；command、query、reactor 不是獨立 skill，而是 `slice-implementer` 的 modes / references。

## 核心分工

| Skill | 主要任務 | 主要輸入 | 主要輸出 | 不該做的事 |
| :--- | :--- | :--- | :--- | :--- |
| `ddd-ca-hex-architect` | 架構診斷、目標設計、切分策略 | 現況描述、模組結構、ADR、需求、混亂點 | 目標架構、切片順序、風險、非目標 | 直接代替 implementer 大量修改 code |
| `code-reviewer` | 程式碼規則審查、違規點盤點、評分 | 具體檔案、模組、測試、實作片段 | 評分、findings、architecture-level / code-level 標記 | 代替架構規劃、代替實作 |
| `slice-implementer` | 依既定方向完成一個 bounded slice | requirement、spec、workflow task、review findings、slice goal、mode | bounded code 或 document 變更、驗證結果、handoff notes | 自行重定義架構方向或靜默擴張 scope |
| `local-change-implementer` | 完成一個局部技術變更 | 單一主要目標、局部操作、可接受依賴半徑 | 局部變更、直接依賴更新、窄範圍驗證 | 抽 class/interface、改 domain language、改 API/event/module boundary |

## `slice-implementer` Modes

`slice-implementer` 依 task intent 載入對應 mode reference：

- command use case mode
- query use case mode
- reactor mode
- generic slice mode

當 command / query / reactor 的語意明確時，使用對應 mode 保留原本限制；當任務不是這三種架構角色時，使用 generic slice mode。

## 何時用哪個 Skill

### 用 `ddd-ca-hex-architect`

當問題是「應該改成什麼樣子」：

- bounded context / aggregate boundary 不清楚
- dependency direction 或 layer placement 不清楚
- domain language、DTO、API、event 命名語意不清楚
- 需要切分多個 implementation slices

### 用 `code-reviewer`

當問題是「現在這段 code 或文件哪裡不符合規範」：

- 需要正式 findings、severity、score
- 需要區分 architecture-level 與 code-level 問題
- 需要驗證一輪實作後是否收斂

### 用 `slice-implementer`

當問題是「依照既定方向，把這個 bounded slice 做出來」：

- 一個新功能或 bug fix
- 一個 command / query / reactor flow
- 一批 review remediation
- 一段文件或 AI context 的 source-of-truth slice
- 一個 bounded refactor slice

### 用 `local-change-implementer`

當問題是「只在一個局部目標周圍做技術變更」：

- extract method
- local rename
- 單一類別內部寫法調整
- 局部 SQL / ORM 寫法調整
- 直接呼叫點更新

若執行中發現需要新增 class/interface、調整架構邊界、改 domain language、改 DTO/API/event 名稱，必須停止並交回 `slice-implementer` 或 `ddd-ca-hex-architect`。

## 推薦工作流

```text
1. ddd-ca-hex-architect
   需要時做診斷與切片策略

2. code-reviewer
   需要時產生具體 findings

3. slice-implementer
   落地一個 bounded slice

4. local-change-implementer
   只在 slice 內處理局部技術調整

5. code-reviewer
   驗證這一輪是否收斂
```

## Rename Decision Rule

- local rename:
  - 只改善單一類別、方法、欄位、局部符號可讀性
  - 不改變 bounded context、DTO、API、event、domain language
  - 可交給 `local-change-implementer`
- semantic rename:
  - 影響 ubiquitous language、DTO、API、event、boundary naming
  - 可能反映商業詞彙改版或領域語意變更
  - 先交給 `ddd-ca-hex-architect` 覆核，再由 `slice-implementer` 落地

## 不建議的混用方式

- 讓 `code-reviewer` 直接當 implementer。
- 讓 `slice-implementer` 自己決定最終架構。
- 讓 `local-change-implementer` 擴張成多模組或跨邊界變更。
- 讓 command / query / reactor mode 重新升格成 top-level skill。

## 相關文件

- `DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`
- `SLICE-IMPLEMENTER-SKILL-GUIDE.md`
- `LOCAL-CHANGE-IMPLEMENTER-SKILL-GUIDE.md`
- `AI-REFACTORING-SKILL-CONTRACTS.md`
- `AI-SKILL-GUIDE-STANDARDS.md`
