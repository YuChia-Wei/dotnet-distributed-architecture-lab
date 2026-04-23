# Use Case Implementer Skill Guide

本文件說明如何從使用者角度使用下列三個 bounded implementation skills：

- `command-use-case-implementer`
- `query-use-case-implementer`
- `reactor-implementer`

這三個 skill 的定位是「直接落地一個已經大致明確的 use case / reactor」，不是重新規劃整體架構。

## 適用情境

適合用在：

- requirement / spec 已經存在，只差 bounded implementation
- 已有 `ddd-ca-hex-architect` 的方向，接下來要落地 command、query、reactor
- 已有 review findings，現在要把某個 use case 或 reactor 修到位
- 想讓 main agent 直接進入 command/query/reactor implementation，而不是先手動指定 delegated sub-agent role

## 不適用情境

不適合直接用在：

- aggregate 邊界還不清楚
- command / query / reactor 的責任邊界還在爭議中
- 任務其實是 stage 級重構，而不是單一 bounded implementation
- 你只想做單一類別內的 extract method 或 local rename

對應建議：

- 邊界不清：先用 `ddd-ca-hex-architect`
- stage 級重構：改用 `staged-refactor-implementer`
- 局部小整理：改用 `tactical-refactor-implementer`
- 測試情境尚未拆清楚：先用 `bdd-gwt-test-designer`

## 三個 Skill 怎麼選

### `command-use-case-implementer`

適用於：

- Create / Update / Delete 類行為
- 會改變 aggregate 狀態
- 會產生 domain events
- 需要 command handler、write-side persistence、validation notes

Canonical spec:

- `.ai/assets/skills/command-use-case-implementer/skill.yaml`

### `query-use-case-implementer`

適用於：

- Get / List / Search 類查詢
- 需要 projection、DTO、read model
- 不應修改 domain state

Canonical spec:

- `.ai/assets/skills/query-use-case-implementer/skill.yaml`

### `reactor-implementer`

適用於：

- 事件驅動的一致性處理
- projection 更新
- MQ-driven integration reaction
- 跨 aggregate 事件回應

Canonical spec:

- `.ai/assets/skills/reactor-implementer/skill.yaml`

## 與 Sub-Agent Role 的關係

這三個 skill 是 top-level implementation entry。  
對應的 delegated worker-role canonical assets 仍然是：

- `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`

也就是說：

- 人或 main agent 直接啟動時，優先用 implementer skills
- 需要再切成 bounded worker delegation 時，才用 sub-agent role prompts

## Prompt 撰寫方式

一個好用的 prompt 至少應包含：

1. 目標 use case / reactor
2. requirement / spec / review finding 來源
3. bounded context 或 aggregate 範圍
4. 明確輸出期待
5. 限制條件或不得擴張的邊界

## Prompt 範本

### 範本 1：實作 command use case

```text
Use $command-use-case-implementer to implement the [command name] use case in this repository.

Source of truth:
- Requirement/spec: [path or summary]
- Bounded context / aggregate: [target]

Constraints:
- keep the existing architecture direction
- do not redesign aggregate boundaries
- follow current repository and handler rules

Return:
1. touched files
2. implementation summary
3. validation notes
4. follow-up handoff if tests or review are still needed
```

### 範本 2：實作 query use case

```text
Use $query-use-case-implementer to implement the [query name] use case in this repository.

Source of truth:
- Requirement/spec: [path or summary]
- DTO / projection target: [target]

Constraints:
- query must not modify domain state
- keep DTO naming aligned with current terminology

Return:
1. touched files
2. read-model / DTO summary
3. validation notes
4. follow-up handoff if tests or review are still needed
```

### 範本 3：實作 reactor

```text
Use $reactor-implementer to implement the [reactor name] flow in this repository.

Source of truth:
- Triggering event: [event]
- Goal: [consistency update / integration reaction / projection update]

Constraints:
- keep existing architecture direction
- do not redesign event ownership
- use the established MQ and handler rules

Return:
1. touched files
2. event-processing summary
3. validation notes
4. follow-up handoff if tests or review are still needed
```

### 範本 4：由 review findings 落地修正

```text
Use $command-use-case-implementer to apply these review findings to the [use case name] implementation.

Inputs:
- review findings: [paste or path]
- target scope: [handler / mapper / repository interaction]

Constraints:
- stay within bounded command-side implementation
- do not expand into architecture redesign

Return:
1. touched files
2. which findings were addressed
3. remaining findings or required handoff
```

## 預期輸出

這三個 skill 的輸出應偏向：

- bounded implementation result
- touched files 或預計輸出位置
- validation notes
- 需要時，明確指出下一個 skill 或 delegated role

它們不應直接假裝完成：

- 架構決策
- 正式 code review
- 完整測試策略設計

## 建議閱讀順序

1. 先看本文件，決定要用 command、query 還是 reactor implementer
2. 再看 `.ai/assets/skills/README.MD` 找 skill registry
3. 再看對應 `skill.yaml`
4. 需要 runtime entry 時，再看 `.agents/skills/<skill>/SKILL.md` 或 `.claude/skills/<skill>/SKILL.md`
5. 若要進一步 delegated execution，再看 `.ai/assets/sub-agent-role-prompts/<role>/sub-agent.yaml`
