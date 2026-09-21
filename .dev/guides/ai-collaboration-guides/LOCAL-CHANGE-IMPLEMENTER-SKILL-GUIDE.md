# Local Change Implementer Skill Guide

本文件說明如何使用 `local-change-implementer` 執行局部技術變更。

`local-change-implementer` 是 lower-level local execution skill。它可以被 `slice-implementer` 呼叫，也可以由人類直接用在單一 class、object、method、symbol、SQL/ORM 或 direct call sites 的小改動。

## 這個 Skill 可以做什麼

適合用在：

- 單一 class/object/method/symbol 的小改動
- 抽方法
- 局部 rename
- 小型 bug fix
- 局部 SQL / ORM 寫法調整
- 直接呼叫點更新
- 行為不變的局部 cleanup

## 這個 Skill 不應該做什麼

不應該拿來做：

- 改變公開合約、責任、dependency/lifetime/transaction 的 class
- 抽 interface
- 改 dependency direction
- 改 bounded context / aggregate boundary
- 改 domain language、DTO、API、event 命名語意
- 跨 module 或跨 aggregate 的變更
- 規劃一個完整 slice

## 多檔案與交接判斷

判斷依據是單一技術目標、操作與允許的依賴範圍，不是檔案數。
同一模組內的 private symbol 與三個直接呼叫點仍可由 local-change 處理。
private implementation helper type 可維持在 local change，但前提是仍在已接受的
target 與 dependency radius 內，且不改變 behavior、責任、dependency direction、
lifetime 或 transaction boundary。公開合約、domain、責任、dependency/lifetime/
transaction 會受影響的 class/interface 交給 bounded slice；如果缺少或改變了決策，
才需要重新做 architecture decision。

## 必須停止並升級的情況

如果執行中發現需要：

- 公開合約、domain、責任、dependency/lifetime/transaction 會受影響的 class 或 interface
- 新 abstraction boundary
- dependency direction 調整
- domain language 變更
- 多模組行為修正

就停止，不要硬做。回到：

- `slice-implementer` 重新切 slice
- 或 `ddd-ca-hex-architect` 做 architecture decision

## Prompt 範本

```text
Use $local-change-implementer for this local technical change.

Target:
- <class/object/method/symbol/sql/orm target>

Intent:
- <small fix | extract method | local rename | local cleanup>

Allowed scope:
- target and direct call sites only

Constraints:
- a private implementation helper type may stay local only when target, radius, behavior, responsibility, dependency direction, lifetime, and transaction boundary stay unchanged
- do not change architecture boundaries
- stop and hand off if the change expands beyond local scope

Return:
1. local change summary
2. files affected
3. behavior compatibility notes
4. validation needed
5. escalation if local scope is no longer safe
```

## 預期輸出

- local change result
- dependency radius touched
- behavior compatibility notes
- validation notes
- escalation reason if needed
