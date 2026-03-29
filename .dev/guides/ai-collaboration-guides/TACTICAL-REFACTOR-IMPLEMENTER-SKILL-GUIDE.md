# Tactical Refactor Implementer Skill Guide

本文件說明如何從使用者角度呼叫 `tactical-refactor-implementer` skill。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 以單一類別、物件或主要目標型別為中心做局部重構
- 抽方法
- 局部變更名稱
- 只在必要範圍內調整直接依賴物件與呼叫點

## 這個 Skill 不應該做什麼

不應該拿來做：

- bounded context 重畫
- aggregate boundary 重畫
- command/query/reactor 的 stage 級切片設計
- 抽類別
- 抽介面
- 跨多模組的大規模 rename
- 大範圍 architecture-level refactor

## 它和其他 Skill 的關係

- `ddd-ca-hex-architect` 決定較大的架構方向
- `code-reviewer` 找出具體問題並標記 architecture-level / code-level
- `staged-refactor-implementer` 處理 stage 級、模組級的安全重構
- `tactical-refactor-implementer` 處理局部、物件中心、結構整理型重構

## 典型適用情境

- 某段邏輯太長，要抽方法提升可讀性
- 某個名稱誤導語意，要在局部範圍內安全 rename
- 某個物件周圍有少量直接依賴，也需要跟著整理

## 最大允許粒度

預設情況下，一次只應處理：

- 單一主要目標類別或物件
- 以及其直接依賴與必要呼叫點

允許的操作組合通常是：

- 抽方法 + 小範圍 rename
- rename 方法 / 欄位 / 局部符號 + 更新直接使用位置

不應處理：

- 多個主要類別同時大改
- 一次跨多個模組重整命名
- 牽涉架構邊界重畫的改動
- 抽類別或抽介面這種新型別引入

## 什麼情況要先讓 Architect 覆核

下列情況先交給 `ddd-ca-hex-architect`：

- 你懷疑需要抽類別
- 你懷疑需要抽介面
- rename 可能影響商業詞彙、domain language、DTO、API、event 命名

architect 覆核後，再決定交給：

- `staged-refactor-implementer`
或
- `tactical-refactor-implementer`

## 怎麼下 Prompt

好的 prompt 至少應包含：

1. 主要目標類別或物件
2. 目前問題
3. 想做的局部重構操作
4. 可接受的相依範圍
5. 不要碰的範圍

## 範本 1：抽方法

```text
Use $tactical-refactor-implementer to refactor [class or object] by extracting methods from the current long implementation.

Context:
- Target class: [class]
- Problem: [problem]
- Allowed scope: target class and direct call sites only
- Keep behavior unchanged

Focus on:
- extract methods
- improve readability
- keep naming consistent
- avoid unrelated cleanup

Return:
1. refactor slice
2. files affected
3. behavior compatibility notes
4. validation needed
```

## 範本 2：局部 rename

```text
Use $tactical-refactor-implementer to rename [symbol] safely within a bounded local scope.

Context:
- Current name: [name]
- New name: [new name]
- Scope limit: [scope]
- Do not expand into unrelated modules

Focus on:
- rename symbol
- update direct usages
- avoid behavior changes

Return:
1. rename scope
2. files affected
3. risk notes
4. anything intentionally left unchanged
```
