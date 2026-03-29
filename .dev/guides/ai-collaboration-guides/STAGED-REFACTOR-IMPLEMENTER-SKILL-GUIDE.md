# Staged Refactor Implementer Skill Guide

本文件說明如何從使用者角度呼叫 `staged-refactor-implementer` skill。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 依據既定架構計畫執行單一 stage 的重構
- 把 review findings 轉成小步驟 code changes
- 在不一次大改的前提下逐步拆解 legacy code
- 補齊必要測試與驗證步驟
- 控制變更範圍，維持行為相容

## 這個 Skill 不應該做什麼

不應該拿來做：

- 全域架構方向決策
- 第一輪問題診斷
- 完整 code review
- 沒有計畫就直接大規模重寫
- 在輸入不足時自行擴大 scope

## 它和其他 Skill 的關係

- `ddd-ca-hex-architect` 先決定重構方向、切片、目標結構
- `code-reviewer` 先盤點具體違規點與 code-level 風險
- `staged-refactor-implementer` 再把其中一個 safe slice 落地

## 沒先跑其他 Skill 時能不能用

可以，但只限於非常保守的情況。

若沒有先跑 `ddd-ca-hex-architect` 或 `code-reviewer`，那至少必須由使用者自己提供：

- 明確的 stage goal
- 很小的 scope
- 必須維持不變的行為
- 清楚的限制與驗證要求

若這些資訊不足，這個 skill 應該停止擴張 scope，並要求先回到：

- `ddd-ca-hex-architect` 做架構診斷
或
- `code-reviewer` 做具體問題盤點

## 最大允許粒度

預設情況下，這個 skill 一次只應處理下列其中一種：

- 單一 aggregate 邊界整理
- 單一 use case flow 或單一 handler 的 refactor
- 單一 adapter extraction
- 單一 outbound port isolation
- 單一 module 內的一個 repository misuse cleanup
- 單一 hot path 的測試保護補強

超過這個粒度時，不應直接硬做，應該：

1. 先切成多個 stage
2. 或回到 `ddd-ca-hex-architect` 重新切片

## 怎麼下 Prompt

好的 prompt 至少應包含：

1. 目前要執行的 stage 或 slice
2. 目標模組 / 檔案範圍
3. 來自 architect 或 reviewer 的輸入
4. 相容性與驗證要求
5. 明確限制不要順手做太多事

## 範本 1：依架構計畫執行第一階段重構

```text
Use $staged-refactor-implementer to execute stage 1 of this refactoring plan.

Context:
- Target area: [module]
- Refactoring goal: [goal]
- Architectural target: [summary]
- Constraints: preserve behavior, keep changes incremental

Focus on:
- smallest safe code changes first
- clear file-by-file impact
- test updates only where required
- no unrelated cleanup

Return:
1. implementation steps
2. files to change
3. risks
4. validation/tests for this stage
```

## 範本 2：依 review findings 落地一個 safe slice

```text
Use $staged-refactor-implementer to implement one safe refactoring slice based on these review findings.

Context:
- Target area: [module / aggregate / handler]
- Review findings: [paste findings]
- Desired boundary after this stage: [target]

Focus on:
- convert findings into minimal code changes
- avoid changing public behavior unless required
- keep follow-up work out of this stage
- identify deferred items explicitly

Return:
1. chosen slice
2. implementation plan
3. affected files
4. deferred items
5. validation plan
```

## 範本 3：先列出重構執行任務，再動手

```text
Use $staged-refactor-implementer to break this refactoring stage into executable tasks before editing code.

Context:
- Stage goal: [goal]
- Target files/modules: [scope]
- Required invariants: [invariants]

Return:
1. ordered tasks
2. dependency notes
3. test impact
4. rollback concerns
```

## 範本 4：實作後自我檢查

```text
Use $staged-refactor-implementer to verify whether this refactoring stage is complete and ready for code-reviewer.

Context:
- Stage goal: [goal]
- Changes made: [summary]
- Expected outcome: [outcome]

Check:
- scope stayed bounded
- architecture direction was followed
- tests/validation were updated where needed
- no obvious unrelated edits were mixed in

Return:
1. completion check
2. remaining gaps
3. what code-reviewer should inspect next
```

## 典型輸出

你通常應該期待它回傳：

- 這一輪要處理的最小 slice
- 會修改哪些檔案
- 哪些變更要先做、哪些不要混在一起
- 哪些測試或驗證要一起補
- 哪些項目要留到下一輪

如果輸入不足，你應該期待它回傳：

- 為什麼目前不能安全執行大範圍重構
- 需要補哪些最小輸入
- 應該先去用哪個 skill

## 建議使用順序

1. 先看 `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
2. 再看 `DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`
3. 若你已經有計畫與 findings，再使用本 skill
