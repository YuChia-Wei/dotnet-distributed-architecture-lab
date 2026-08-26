# Skill And Sub-Agent Taxonomy Guide

本文件定義 AI 協作知識庫中的三種主要資產類型：

- skill
- sub-agent role
- shared / supporting material

它的目的不是記錄某個專案當時做了什麼決策，而是提供可攜式的 taxonomy，讓新專案也能沿用同一套整理方式。

## 核心結論

- `skill`
  - top-level capability
- `sub-agent role`
  - owning skill 所有的 bounded worker contract；可由 owning skill direct inline，或在有 genuine execution evidence 時 delegated
- `shared / supporting material`
  - 給 skill / sub-agent 使用，但不應誤當成 runtime entry

taxonomy 只分類資產，不等於某次執行的 disposition。

## 1. Skill

`skill` 是使用者或 main agent 可直接啟動的高階能力。

特徵：

- 可作為主要入口
- 能夠處理較完整的任務類型
- 可能協調多個 worker roles
- 對人類使用者或主 agent 來說是可辨識的功能單位

例：

- `ai-context-governance`
- `ddd-ca-hex-architect`
- `code-reviewer`
- `bdd-gwt-test-designer`
- `slice-implementer`
- `local-change-implementer`

canonical source：

- `.ai/assets/skills/<skill-id>/`

## 2. Sub-Agent Role

`sub-agent role` 是 owning skill 所有的 bounded worker contract。它可由
owning skill 直接 inline 套用，或在條件成立且保有 genuine execution
evidence 時委派給 worker；它不是預設必定 delegated 的 runtime 宣告。

特徵：

- 不應預設當成 top-level skill
- 任務範圍較窄、邊界較穩定
- 輸入輸出清楚
- 服務於生成、測試、review、integration、infrastructure 等局部工作

適用的 role 必須明確記錄 `direct`、`delegated`、`unavailable` 或
`not-applicable`。只有 genuine child invocation 才能記錄為 `delegated`；
完整的 disposition、execution evidence、retry 與 fallback 規則見
[Provider-Neutral Role Execution Contract](../../../.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md)。

例：

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`
- `aggregate-sub-agent`
- `usecase-test-sub-agent`
- `code-review-sub-agent`
- `context-translator`

canonical source：

- `.ai/assets/sub-agent-role-prompts/<sub-agent-id>/`

## 3. Shared / Supporting Material

某些材料不是 skill，也不是完整的 sub-agent role。

例如：

- checklist
- prompt snippet
- validation command reference
- report template
- shared rules
- 未成熟到足以成為獨立 role 的專用說明

這類材料應視為 supporting material，而不是新的 runtime entry。

## Test 與 Review 的典型分工

### Test

- `bdd-gwt-test-designer`
  - 設計 scenario 與 assertion plan
- `usecase-test-sub-agent` / `aggregate-test-sub-agent` / `reactor-test-sub-agent`
  - 實作具體測試

### AI Context / Documentation Governance

- `ai-context-governance`
  - 整理 `.ai/`、`.dev/`、`.agents/`、`.claude/` 的 AI context 邊界、語言政策、skill routing、wrapper sync 與 context migration
- `context-translator`
  - 英文 canonical context 定稿後，處理有明確 source/output 的 bounded 繁中衍生翻譯 role；可 inline 或有證據 delegated，不是 top-level skill
- 不要把純 AI 文件整理、prompt 邊界整理、README 語言策略、或 wrapper/index sync 交給 `bdd-gwt-test-designer`
- `bdd-gwt-test-designer` 只在主要工作是測試意圖、Given-When-Then scenario、assertion plan 時使用

### Review

- `code-reviewer`
  - top-level 正式 review
- `code-review-sub-agent`
  - bounded review role；可 inline 或有證據 delegated

## 不建議的錯誤分類

### 錯誤 1：因為某份 prompt 可執行，就升格成 skill

這會造成 top-level capability 和 worker role 混淆。

### 錯誤 2：把所有 test / review 相關材料都做成 skill

這會讓入口過多，而且難以維持清楚的分工。

### 錯誤 3：把 shared rules 當成 sub-agent role

shared rules 沒有獨立輸入輸出 contract，不應假裝成 worker role。

## 實務判斷規則

問自己三個問題：

1. 這是人或 main agent 直接啟動的能力嗎？
   - 是：優先視為 skill
2. 這是 owning skill 可直接 inline 或委派的 bounded worker contract 嗎？
   - 是：優先視為 sub-agent role
3. 這只是支援上面兩者的材料嗎？
   - 是：放 shared / supporting material

## 與其他文件的關係

- taxonomy 與 asset 放置策略：
  - `AI-ASSET-LOCATION-STRATEGY.md`
- role execution 與 implementer skill 的互動：
  - [Provider-Neutral Role Execution Contract](../../../.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md)
  - `.ai/SUB-AGENT-SYSTEM.MD`（derived binding / routing view）
  - `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- sub-agent role manifests 的 `human_guide` 應指向本文件，作為 human-facing taxonomy 參考。
- 模式選擇理由：
  - `../../standards/rationale/skill-sub-agent-boundary-rationale.MD`
