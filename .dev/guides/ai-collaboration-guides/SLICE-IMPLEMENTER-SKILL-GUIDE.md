# Slice Implementer Skill Guide

本文件說明如何使用 `slice-implementer` 執行一個 bounded implementation slice。

`slice-implementer` 是 scope-first implementer。它不再把 command、query、reactor 分成三個 top-level implementer skill，而是用 execution mode / reference 保留這些架構角色的規則，再依 intent 疊加必要的 overlay。

## 這個 Skill 可以做什麼

適合用在：

- 實作一個 feature slice
- 修正一個 bug fix slice
- 落地一個 review remediation slice
- 執行一個 behavior-preserving refactor slice
- 實作 command / query / reactor mode 的 bounded slice
- 協調 slice 內需要的 local technical changes

## 這個 Skill 不應該做什麼

不應該拿來做：

- 重新定義 architecture direction
- 模糊 bounded context 或 aggregate boundary 時硬做
- 把多個不相關 slice 混成一輪
- 取代 code review
- 取代 BDD / GWT test design
- 取代 local-change-implementer 做很細的 class/object/symbol 調整

## Execution Mode 怎麼選

| Mode | 適用情境 |
| --- | --- |
| `command` | 會改變 aggregate 狀態的 command-side use case |
| `query` | 不修改 domain state 的 read-side use case |
| `reactor` | 事件反應處理器、projection 更新、integration reaction |
| `generic` | 不屬於 command/query/reactor 的 bounded slice |

每個 slice 只選一個 execution mode。`refactor` 是 intent，不是 mode；它可以在任何
符合實際結構的 mode 下執行。`remediation` 是 overlay：review finding 或 validation
failure 的修正仍須保留其 command、query、reactor 或 generic mode 規則。

## Remediation Overlay

使用 remediation overlay 時，來源要分層：

- authorization source：使用者要求或 workflow task，負責授權範圍、acceptance criteria、non-goals 與 validation；
- normative truth：requirement、spec、standard、ADR，負責定義正確行為與架構；
- finding evidence：assessment、code review 或 validation finding，負責記錄觀察到的問題與證據。

Finding 應使用穩定 reference，例如 `<assessment-id>#<finding-id>`。Workflow task
不能取代 normative truth，finding recommendation 也不能自行形成新的架構決策。

## 和 Local Change 的關係

`slice-implementer` 可以把 slice 內的局部技術變更交給 `local-change-implementer`。

例子：

- slice 目標是修正某個 import flow；
- 其中一個步驟只是整理 `CsvParser.ParseRows`；
- 這個局部步驟可以交給 `local-change-implementer`。

若局部變更需要抽 class、抽 interface、改 dependency direction 或 domain language，應停止並回到 architecture review 或 slice planning。

## Prompt 範本

```text
Use $slice-implementer to implement this bounded slice.

Intent:
- <feature | bug-fix | review-remediation | validation-failure-remediation | behavior-correction | refactor | cleanup>

Execution mode:
- <command | query | reactor | generic>

Overlays:
- <none | remediation>

Authorization source:
- <user request or workflow task>

Normative truth:
- <requirement/spec/standard/ADR>

Finding evidence:
- <stable finding references, or none>

Slice boundary:
- In scope: <files/modules/behavior>
- Out of scope: <non-goals>

Constraints:
- do not redefine architecture direction
- preserve existing behavior unless the intent requires behavior change
- use local-change-implementer for local technical edits when useful

Return:
1. selected intent, execution mode, overlays, and references
2. implementation summary and finding dispositions when applicable
3. touched files
4. validation notes
5. handoff or deferred items
```

## 預期輸出

- selected intent, execution mode, overlays, and references
- bounded implementation result
- finding dispositions and evidence when remediation applies
- touched files
- validation notes
- local-change handoff notes, if used
- deferred items
