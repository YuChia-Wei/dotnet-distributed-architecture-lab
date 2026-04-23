# Use Case, Command, Query, and Handler Relationship

本文件定義本 repo 在 DDD + Clean Architecture + Hexagonal Architecture 下，`use case`、`command`、`query`、`handler`、`application service`、`repository`、`controller`、`message bus` 等詞彙的關係與責任邊界。

## 目的

- 統一詞彙
- 避免把 `use case`、`command`、`handler` 混成同義詞
- 定義 controller、message bus、use case、handler、application service 的依賴方向

## 核心結論

- `Use Case` 是 application inbound port，也是一次明確 business operation 的主名稱。
- `Use Case` 在本 repo 中應顯式反映在程式碼中，預設以 `I<Verb><Noun>UseCase` / `<Verb><Noun>UseCase` 命名。
- `Input` / `Output` / `Result` / `PageResult` 是 use case boundary model，不使用 `InputDto` / `OutputDto` / `ResultDto` 作為預設命名。
- `Command` / `Query` 不是 use case 的同義詞，而是 message-oriented request model。
- HTTP controller 的主要入口應直接依賴 `Use Case`，不以 `message bus -> command handler` 作為預設入口。
- `Command Handler` / `Query Handler` 是 message-oriented application executor，主要服務於 bus、consumer、reactor、workflow 等入口。
- `Application Service` 是 use case 內部可選的 application-layer collaborator，不是每個 use case 都必備，也不是 inbound port。
- `Controller` 是 adapter，只負責轉譯 protocol input/output，不直接碰 repository 或 domain model。
- `message bus` 是 delivery / dispatch mechanism，不應被誤當成 use case 本身。

## 詞彙定義

### Use Case

一次明確的 application-level business operation，且在本 repo 中是顯式的 inbound port。

例：

- `CreateProduct`
- `PlaceOrder`
- `DecreaseStock`

對應程式碼命名例：

- `IPlaceOrderUseCase`
- `PlaceOrderUseCase`
- `PlaceOrderInput`
- `PlaceOrderOutput`

`Use Case` 回答的是：

- 系統這次要完成什麼業務操作
- 需要哪些 application input
- 改變哪個 aggregate 或 read model
- 成功後輸出什麼結果

`Use Case` 不是 transport 技術詞彙，而是 application boundary。本 repo 要求它在程式碼中顯式存在，而不是只留在文件概念層。

### Input / Output / Result / PageResult

`Input` / `Output` / `Result` / `PageResult` 是 use case boundary model。

- `Input`
  - use case 的 application-level input model
  - 不直接等同於 HTTP request，也不直接等同於 message bus command
- `Output`
  - use case 的 application-level output model
  - 不直接等同於 HTTP response，也不直接等同於 query-side DTO
- `Result`
  - result pattern 的 application-level output wrapper
  - 用於表達 success / failure / error / optional value
- `PageResult`
  - 分頁查詢的 application-level output wrapper
  - 用於表達 items、total count、page index、page size 等分頁資訊

命名規則：

- `PlaceOrderInput`
- `PlaceOrderOutput`
- `Result<Guid>`
- `Result<OrderDetailsOutput>`
- `PageResult<ProductDto>`

避免使用：

- `PlaceOrderInputDto`
- `PlaceOrderOutputDto`
- `DecreaseStockResultDto`

`Dto` 應保留給 projection、跨 BC 傳輸、或 adapter / read model 導向的資料承載模型。

補充規則：

- 若 use case 回傳的是單純成功資料，優先使用具語意的 `*Output`
- 若 use case 明確採用 result pattern，回傳 `Result` / `Result<T>`
- 若 use case 明確回傳分頁資料，回傳 `PageResult<T>`
- `Result` / `PageResult` 屬於 use case boundary model 的特例，不視為 DTO

### Command

表達「要做一件會改變系統狀態的事」的 message-oriented request model。

`Command` 本身不負責執行業務，只承載：

- input data
- caller intent
- 必要的 metadata

例：

- `CreateProductCommand`
- `ShipOrderCommand`

在本 repo 中，`Command` 的主要適用情境是：

- message bus dispatch
- MQ consumer
- reactor / workflow 內部訊息
- 非 HTTP 的 message-oriented 入口

因此：

- `Command` 不是 HTTP use case port 的預設輸入模型
- `Command` 不是 `Use Case` 的同義詞

### Query

表達「要讀取資料或組裝 view/read model」的 request model。

`Query` 不應改變 domain state。

`Query` 可視情況作為：

- 顯式 use case port 的 input model
- query handler 的 message model

但無論哪種形式，都應維持 read-only 語意。

### Handler

接收 `Command` 或 `Query` 並執行對應 application flow 的 message-oriented application-layer object。

`Handler` 的責任通常包括：

- 驗證 application-level input
- 載入 aggregate 或 read-side data
- 呼叫 aggregate behavior / domain service
- 呼叫 repository 或 query service
- 組裝 result
- 必要時發布 integration message

在本 repo 中：

- `Handler` 不是 `Use Case` 的同義詞
- `Handler` 可以在內部轉呼叫 `Use Case`
- `Handler` 也可以在某些純訊息流場景中直接承擔 application execution
- 但 HTTP controller 不以 `Handler` 作為預設依賴目標

### Application Service

`Application Service` 是 use case 內部可選的 application-layer collaborator，用來承接不適合直接留在單一 use case 類別中的 orchestration / policy coordination。

它不是每個 use case 都必備的物件，也不是 inbound port。

建議抽出的情況：

- 同一段 orchestration 需要被多個 use case / handler / reactor 重用
- 流程協調跨多個 repository / gateway / publisher / policy collaborator
- 流程中有明確的 permission / compensation / retry / sequencing policy
- use case 類別中的流程控制已壓過 use case 主語意

不建議抽出的情況：

- 只是把 use case 的內容平移到同名 service
- 沒有重用需求，也沒有獨立 policy/orchestration 語意
- 只是 repository pass-through
- 單純為了讓 class 變薄而多包一層

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
- 轉成 use case input
- 透過 `[FromServices]` 取得 use case port
- 呼叫 application boundary
- 將 result 轉成 HTTP response

Controller 不應：

- 透過 `IMessageBus` 作為 HTTP use case 的預設入口
- 直接依賴 repository
- 直接操作 aggregate
- 承擔 domain orchestration

Controller DI 規則：

- `Use Case` 介面只能透過 action parameter 的 `[FromServices]` 注入
- 其他輔助介面如 `ILogger`、`IMapper`、`IMessageBus` 可使用 constructor injection
- 不直接注入 repository 或 aggregate

## 推薦關係鏈

### HTTP Command-Side Flow

```text
HTTP Request
  -> Controller
  -> Use Case Input
  -> Use Case
  -> Application Service (optional)
  -> Aggregate / Domain Service / Repository / Gateway
  -> Use Case Output / Result / PageResult
  -> HTTP Response
```

### HTTP Query-Side Flow

```text
HTTP Request
  -> Controller
  -> Use Case Input or Query
  -> Use Case
  -> Query Repository / Query Service
  -> Use Case Output / Result / PageResult / Response Model
  -> HTTP Response
```

### Message-Oriented Flow

```text
Consumer / Reactor / Workflow
  -> Command / Query
  -> Handler
  -> Use Case (optional but recommended when the same business operation also exists as a named inbound port)
  -> Application Service (optional)
  -> Aggregate / Query Repository / Gateway
```

### Cross-BC Flow

```text
BC A Application
  -> Integration Event / Request Message
  -> MQ / Message Bus
  -> BC B Consumer / Handler
  -> BC B Use Case / Reactor
```

## Controller 是否一定要透過 Message Bus

否。

應區分兩件事：

- `application boundary`
- `delivery mechanism`

在同一個 BC / process 內：

- HTTP controller 應直接依賴 `Use Case` 進入 application boundary
- `message bus` 可保留給 internal workflow 或 message-oriented dispatch

在跨 BC / 跨 process 情境：

- 必須透過 MQ / message bus

因此：

- `controller -> use case` 是本 repo 的預設規則
- `bus -> command/query handler` 是 message-oriented 補充機制
- 不要把 `bus` 視為 use case 本身

## Handler 是否必須再呼叫 Use Case

不一定，但要看入口類型。

正確原則是：

- HTTP 入口一定要有顯式 `use case boundary`
- message-oriented 入口可以由 handler 直接執行，或轉呼叫 use case
- 若同一 business operation 同時存在 HTTP 與 message-oriented 入口，應優先讓共用邏輯收斂到 use case / application service，而不是各自複製

## 推薦實作規則

### Rule 1

HTTP controller 預設直接依賴顯式 `Use Case` port，不透過 `IMessageBus` dispatch command 進入 application boundary。

### Rule 2

`Use Case` 預設以 `I<Verb><Noun>UseCase` / `<Verb><Noun>UseCase` 命名，搭配 `<Verb><Noun>Input` 與 `*Output` / `Result` / `PageResult`。

### Rule 3

`Command` / `Query` 保留給 message-oriented request model，不作為 HTTP use case port 的預設命名。

### Rule 4

只有在複雜度真的上升時，才抽 `Application Service`，不要為了名詞完整性硬多包一層。

### Rule 5

`Application Service` 不是 inbound port，不直接被 controller 作為主依賴目標。

### Rule 6

`Command Handler` / `Query Handler` 應聚焦在 message-oriented execution，不應退化成與同名 use case 的無意義轉呼叫。

### Rule 7

Query side 應優先使用 query repository / query service，不要把 query flow 拉回 aggregate。

### Rule 8

跨 BC communication 只能用 MQ；同 BC 內 `bus` 是 dispatch choice，不是 HTTP application boundary。

## 命名建議

- HTTP models:
  - `PlaceOrderRequest`
  - `PlaceOrderResponse`
- use case:
  - `IPlaceOrderUseCase`
  - `PlaceOrderUseCase`
  - `PlaceOrderInput`
  - `PlaceOrderOutput`
  - `Result<Guid>`
  - `PageResult<ProductDto>`
- message-oriented models:
  - `ReserveInventoryCommand`
  - `ReserveInventoryCommandHandler`
  - `GetOrderDetailsQuery`
  - `GetOrderDetailsQueryHandler`
- optional application service:
  - `OrderPlacementApplicationService`
  - `InventoryReservationApplicationService`

## 與 Spec 的關係

在 `.dev/specs/` 中：

- `use case` 是 production behavior 的主名稱
- `input` / `output` / `result` / `page result` 是該 use case 的 boundary model
- `command` / `query` / `handler` 是程式碼中的 message-oriented implementation vocabulary，不必額外成為 spec 主詞

因此 spec 應先寫：

- `CreateProduct`

再由程式碼決定以：

- `ICreateProductUseCase + CreateProductUseCase + CreateProductInput + CreateProductOutput`
- 或在 result pattern 下使用 `IIncreaseStockUseCase + IncreaseStockInput + Result<IncreaseStockOutput>`
- 並在需要 message-oriented dispatch 時補上 `CreateProductCommand + CreateProductCommandHandler`

## References

- Microsoft, CQRS pattern:
  - [https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- Martin Fowler, CQRS:
  - [https://martinfowler.com/bliki/CQRS.html](https://martinfowler.com/bliki/CQRS.html)
- Alistair Cockburn, Hexagonal Architecture:
  - [https://alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture)
- Microsoft, DDD-oriented microservice:
  - [https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice)
