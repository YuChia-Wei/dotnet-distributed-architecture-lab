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
  - delegated worker role
- `shared / supporting material`
  - 給 skill / sub-agent 使用，但不應誤當成 runtime entry

## 1. Skill

`skill` 是使用者或 main agent 可直接啟動的高階能力。

特徵：

- 可作為主要入口
- 能夠處理較完整的任務類型
- 可能協調多個 worker roles
- 對人類使用者或主 agent 來說是可辨識的功能單位

例：

- `ddd-ca-hex-architect`
- `code-reviewer`
- `bdd-gwt-test-designer`
- `staged-refactor-implementer`

canonical source：

- `.ai/assets/skills/<skill-id>/`

## 2. Sub-Agent Role

`sub-agent role` 是 workflow 內委派給 bounded worker 的角色定義。

特徵：

- 不應預設當成 top-level skill
- 任務範圍較窄、邊界較穩定
- 輸入輸出清楚
- 服務於生成、測試、review、integration、infrastructure 等局部工作

例：

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`
- `aggregate-sub-agent`
- `usecase-test-sub-agent`
- `code-review-sub-agent`

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

### Review

- `code-reviewer`
  - top-level 正式 review
- `code-review-sub-agent`
  - delegated review worker

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
2. 這是 workflow 中委派出去的 bounded worker 嗎？
   - 是：優先視為 sub-agent role
3. 這只是支援上面兩者的材料嗎？
   - 是：放 shared / supporting material

## 與其他文件的關係

- taxonomy 與 asset 放置策略：
  - `AI-ASSET-LOCATION-STRATEGY.md`
- delegated worker 與 refactor skill 的互動：
  - `.ai/SUB-AGENT-SYSTEM.MD`
  - `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- 模式選擇理由：
  - `../../standards/rationale/skill-sub-agent-boundary-rationale.MD`
