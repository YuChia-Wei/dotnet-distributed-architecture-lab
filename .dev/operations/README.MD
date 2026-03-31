# Operations Docs

本目錄存放分散式系統的 runtime truth 與維運文件。

這些文件回答的不是：

- 「系統應該做什麼」 -> 這屬於 `.dev/requirement/` 與 `.dev/specs/`

而是：

- bounded contexts 如何互動
- integration event 由誰擁有、誰消費
- MQ topology 怎麼接
- 發生 duplicate delivery / retry / replay / dead-letter 時怎麼判斷與處理

## 目錄定位

- `.dev/requirement/`
  - 業務能力、NFR、邊界與約束
- `.dev/specs/`
  - domain/use-case/test specs
- `.dev/operations/`
  - distributed runtime truth、integration ownership、runbooks

## Stage 5 文件類型

- `context-map.md`
  - bounded context 關係、責任、上下游
- `event-catalog.md`
  - integration event ownership、schema摘要、producer/consumer 對照
- `mq-topology.md`
  - broker、exchange/topic、queue、routing、retry/DLQ 策略
- `runbooks/`
  - incident trigger、diagnosis、recovery、verification

## 使用原則

- 內容必須是專案特定 truth，所以應放 `.dev/operations/`，不放 `.ai/`
- 每份文件應能回指 `.dev/requirement/`、`.dev/specs/`、`src/` 或 contracts source
- 不把這裡寫成部署手冊，除非確實有營運情境需要

## `.dev/operations/` 與 `.ops/` 的決策規則

目前維持：

- runtime / 維運知識放 `.dev/operations/`

原因：

- 這一階段的 operations 文件仍然是專案知識系統的一部分
- 它和 `.dev/requirement/`、`.dev/specs/`、`.dev/adr/` 的關聯比和獨立 ops 平台更強
- 現在拆成 `.ops/` 只會增加資訊架構成本，還不會帶來明顯治理收益

只有當下列條件成立時，才考慮升級成 repo 根層的 `.ops/`：

- ops 文件數量與治理規則已明顯獨立於 architecture/spec 文件
- 開始有大量 environment-specific runbooks、SLO、alerts、on-call、incident templates
- 需要獨立維護者從 `.ops/` 直接工作，而不是經由 `.dev/` 知識樹
- `.dev/operations/` 的內容成長到足以形成獨立知識域
