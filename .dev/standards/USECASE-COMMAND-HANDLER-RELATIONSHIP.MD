# Use Case, Command, Query, and Handler Relationship

本文件定義本 repo 在 DDD + Clean Architecture + Hexagonal Architecture 下，`use case`、`command`、`query`、`handler`、`application service`、`repository`、`controller` 等詞彙的關係與責任邊界。

## 目的

- 統一詞彙
- 避免把 `use case`、`command`、`handler` 混成同義詞
- 定義 controller、message bus、handler、application service 的依賴方向

## 核心結論

- `Use Case` 是 application boundary，不是特定 class 名稱。
- `Command` / `Query` 是進入 use case 的 request model。
- `Handler` 是 command / query 的 application-layer executor。
- 多數情況下，handler 本身就可以是 use case implementation。
- 只有當 orchestration 明顯變複雜、需要重用、或需要把 handler 保持極薄時，才另外抽 `Application Service`。
- `Controller` 是 adapter，只負責轉譯 protocol input/output，不直接碰 repository 或 domain model。
- `message bus` 是 delivery / dispatch mechanism，不應被誤當成 use case 本身。

## 詞彙定義

### Use Case

一次明確的 application-level business operation。

例：

- `CreateProduct`
- `PlaceOrder`
- `DecreaseStock`

`Use Case` 回答的是：

- 系統這次要完成什麼業務操作
- 需要哪些 input
- 改變哪個 aggregate 或 read model
- 成功後輸出什麼結果

`Use Case` 是責任與邊界，不要求一定有一個名為 `*UseCase` 的獨立 class。

### Command

表達「要做一件會改變系統狀態的事」的 request model。

`Command` 本身不負責執行業務，只承載：

- input data
- caller intent
- 必要的 metadata

例：

- `CreateProductCommand`
- `ShipOrderCommand`

### Query

表達「要讀取資料或組裝 view/read model」的 request model。

`Query` 不應改變 domain state。

### Handler

接收 `Command` 或 `Query` 並執行對應 use case 的 application-layer object。

`Handler` 的責任通常包括：

- 驗證 application-level input
- 載入 aggregate 或 read-side data
- 呼叫 aggregate behavior / domain service
- 呼叫 repository 或 query service
- 組裝 output DTO / result
- 必要時發布 integration message

### Application Service

當 handler 的 orchestration 過長、跨多個 collaborator、需要重用，或你想把 handler 保持為極薄 dispatch shell 時，才抽出的 application-layer service。

它不是每個 use case 都必備的物件。

### Domain Service

無法自然歸屬於單一 aggregate method、但仍屬於 domain rule 的物件。

不要把純 application orchestration 誤放進 domain service。

### Repository

負責 aggregate persistence 或 query-side data access 的 port / implementation。

- command side: repository 載入與保存 aggregate
- query side: query repository / query service 組裝 read model

### Controller

HTTP adapter。只負責：

- 接收 HTTP request
- 轉成 command / query
- 呼叫 application boundary
- 將 result 轉成 HTTP response

Controller 不應：

- 直接依賴 repository
- 直接操作 aggregate
- 承擔 domain orchestration

## 推薦關係鏈

### Command Flow

```text
HTTP Request
  -> Controller
  -> Command
  -> Command Handler
  -> Aggregate / Domain Service / Repository
  -> Result DTO
  -> HTTP Response
```

### Query Flow

```text
HTTP Request
  -> Controller
  -> Query
  -> Query Handler
  -> Query Repository / Query Service
  -> Result DTO
  -> HTTP Response
```

### Cross-BC Flow

```text
BC A Application
  -> Integration Event / Request Message
  -> MQ / Message Bus
  -> BC B Consumer / Handler
  -> BC B Use Case
```

## Controller 是否一定要透過 Message Bus

不一定。

應區分兩件事：

- `application boundary`
- `delivery mechanism`

在同一個 BC / process 內：

- controller 可以透過 in-process dispatcher、mediator、Wolverine handler invocation、或直接依賴 application port 進入 use case

在跨 BC / 跨 process 情境：

- 必須透過 MQ / message bus

因此：

- `controller -> command/query dispatch` 是合理的
- 但不要把 `bus` 視為唯一合法入口

## Handler 是否必須再呼叫 Use Case Class

不必。

正確原則是：

- 一定要有 `use case boundary`
- 不一定要多包一層 `UseCaseService`

以下情況，handler 本身就可以是 use case implementation：

- 單一 aggregate 為主
- orchestration 短而清楚
- 沒有可重用的 application workflow 需求
- handler 內容仍可讀、可測、可維護

以下情況，建議抽 `Application Service`：

- handler 需要協調多個 repository / service
- 流程長且有多段 policy / permission / compensation logic
- 同一 orchestration 需要被多個 adapter 或 consumer 重用
- 你需要讓 handler 保持為 very thin transport shell

## 推薦實作規則

### Rule 1

預設把 handler 視為 use case implementation。

### Rule 2

只有在複雜度真的上升時，才抽 `Application Service`，不要為了名詞完整性硬多包一層。

### Rule 3

Command handler 應聚焦在狀態變更與 domain collaboration，不應退化成只轉呼叫另一個同名 service。

### Rule 4

Query handler 應優先使用 query repository / query service，不要把 query flow 拉回 aggregate。

### Rule 5

Controller 只碰 adapter concern，不直接碰 repository 或 aggregate。

### Rule 6

跨 BC communication 只能用 MQ；同 BC 內是否使用 bus，屬於 dispatch choice，不是 architecture law。

## 命名建議

- request model:
  - `CreateProductCommand`
  - `GetOrderDetailsQuery`
- handler:
  - `CreateProductHandler`
  - `GetOrderDetailsHandler`
- optional application service:
  - `OrderPlacementApplicationService`
  - `InventoryReservationApplicationService`

若已使用 handler-based dispatch，避免再建立完全同名且只有單行轉呼叫的 `CreateProductUseCaseService`。

## 與 Spec 的關係

在 `.dev/specs/` 中：

- `use case` 是 production behavior 的主名稱
- `command` / `query` 是進入該 use case 的 request model
- `handler` 是程式碼實作形態，不必額外成為 spec 主詞

因此 spec 應先寫：

- `CreateProduct`

再由程式碼決定以：

- `CreateProductCommand + CreateProductHandler`
- 或其他等價 application dispatch 形式

來實作這個 use case。
