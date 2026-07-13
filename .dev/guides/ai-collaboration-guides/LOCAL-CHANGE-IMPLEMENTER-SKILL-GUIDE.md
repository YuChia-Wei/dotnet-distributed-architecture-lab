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

- 抽 class
- 抽 interface
- 改 dependency direction
- 改 bounded context / aggregate boundary
- 改 domain language、DTO、API、event 命名語意
- 跨 module 或跨 aggregate 的變更
- 規劃一個完整 slice

## 必須停止並升級的情況

如果執行中發現需要：

- 新 class 或 interface
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
- do not introduce new class or interface
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
