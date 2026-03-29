# DDD + CA + HEX Architect Skill Guide

本文件說明如何從使用者角度呼叫 `ddd-ca-hex-architect` skill。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 設計新的 bounded context
- 定義或重構 aggregate 邊界
- 設計 command / query / reactor 流程
- 設計 bounded context 之間的 MQ 整合
- 盤點 inbound port / outbound port / adapter
- 調整 project/module 結構，使其符合 DDD + CA + HEX
- 把散落的 AI prompts 整理成可重用的架構 workflow
- 找出應更新的 ADR、docs、prompts

## 什麼是 HEX

在這個 repo 中，`HEX` 指的是 Hexagonal Architecture 的視角，也就是：

- 哪些是 inbound ports
- 哪些是 outbound ports
- 哪些是 adapters
- 如何讓 domain / application 維持乾淨，不被基礎設施反向污染

它不是取代 DDD 或 Clean Architecture，而是用 port-and-adapter 的方式補強既有的 DDD + CA 設計。

## 怎麼下 Prompt

一個好用的 prompt 通常會有這五段：

1. 目標：你要設計或重構什麼
2. 範圍：bounded context、aggregate、module、prompt set
3. 關注點：你最在意哪些架構問題
4. 輸出：你希望它回傳什麼形式的結果
5. 限制：repo 規則、ADR、既有設計不能破壞的地方

## 範本 1：新 Bounded Context 設計

```text
Use $ddd-ca-hex-architect to design a new bounded context for [business capability] in this repository.

Context:
- Existing bounded contexts involved: [contexts]
- Business goal: [goal]
- Expected integrations: [RabbitMQ/Kafka events or none]

Focus on:
- bounded context boundary
- ubiquitous language
- key aggregates
- inbound ports and outbound ports
- adapters and folder placement
- BC contracts and integration events

Return:
1. assumptions
2. architecture decisions
3. context/module structure
4. events/contracts to add
5. ADRs or docs to update
6. risks and tradeoffs
```

## 範本 2：Aggregate 設計或重構

```text
Use $ddd-ca-hex-architect to design or refactor the aggregate for [aggregate name] in this repository.

Target:
- Bounded context: [context]
- Current problem: [problem]
- Desired behavior: [behavior]

Focus on:
- aggregate boundary
- invariants
- entities and value objects
- domain events and metadata
- whether event sourcing or outbox affects the design

Return:
1. aggregate responsibility
2. proposed model structure
3. behavior methods and events
4. persistence and adapter implications
5. tests/review gates to enforce
```

## 範本 3：Command / Query / Reactor 流程設計

```text
Use $ddd-ca-hex-architect to design the [command/query/reactor] flow for [use case name].

Context:
- Bounded context: [context]
- Trigger: [HTTP request, MQ event, scheduler, internal workflow]
- Current constraints: [constraints]

Focus on:
- application port shape
- DTO/result contract
- domain interaction
- outbound ports
- adapter placement
- separation between command, query, and reactor concerns

Return:
1. flow summary
2. handler responsibilities
3. ports and adapters
4. persistence/messaging impact
5. files and prompts likely to change
```

## 範本 4：MQ 整合設計

```text
Use $ddd-ca-hex-architect to design the MQ-based integration between [producer BC] and [consumer BC].

Context:
- Triggering business event: [event]
- Broker choice: [RabbitMQ/Kafka]
- Delivery constraints: [at-least-once, idempotency, ordering, retry]

Focus on:
- event contract
- producer responsibilities
- consumer/reactor responsibilities
- outbox needs
- failure handling and replay safety

Return:
1. event choreography
2. contract payload
3. producer and consumer boundaries
4. outbox/transaction notes
5. implementation risks
```

## 範本 5：整理既有 Prompt 或 Skill

```text
Use $ddd-ca-hex-architect to reorganize the existing AI prompts in this repository into a reusable architecture skill/workflow.

Scope:
- Source prompt set: [.ai/assets/...]
- Desired target: [skill, references, prompt families, templates]
- Main pain points: [duplication, inconsistency, hard to discover, too task-specific]

Focus on:
- stable shared rules
- prompt family boundaries
- what should stay task-specific
- user-facing invocation templates
- migration path from old prompts

Return:
1. current prompt map
2. proposed information architecture
3. files to create or merge
4. migration steps
5. risks and open questions
```

## 範本 6：實作前先做架構審查

```text
Use $ddd-ca-hex-architect to review this design direction before implementation.

Proposal:
- [paste the proposed design or summarize it]

Check it against:
- DDD boundaries
- Clean Architecture dependency direction
- HEX ports/adapters placement
- MQ-only cross-BC rule
- repository/DI/testing constraints in this repo

Return:
1. confirmed decisions
2. design flaws or rule conflicts
3. recommended corrections
4. ADR/prompt/doc impact
```

## 短版範例

```text
Use $ddd-ca-hex-architect to design a new inventory bounded context that integrates with SaleOrders through Kafka events.
```

```text
Use $ddd-ca-hex-architect to refactor the Product aggregate boundary and identify the correct ports and adapters.
```

```text
Use $ddd-ca-hex-architect to reorganize canonical AI assets under `.ai/assets/` into reusable architect guidance for this repo.
```

## 建議的閱讀順序

如果你是第一次使用這個 skill，建議順序如下：

1. 先看本文件，了解它能做什麼
2. 再看 [`.claude/skills/ddd-ca-hex-architect/SKILL.md`](C:/Github/YuChia/dotnet-mq-arch-lab/.claude/skills/ddd-ca-hex-architect/SKILL.md)，理解 skill 本體規則
3. 若要深挖設計依據，再看 skill 內的 `references/`

## 與其他目錄的關係

- 這份文件是給人看的，所以放在 `.dev/guides/ai-collaboration-guides/`
- skill 本體仍然在 `.claude/skills/ddd-ca-hex-architect/`
- 給 agent 重用的 prompt building blocks 仍然放在 `.ai/`

