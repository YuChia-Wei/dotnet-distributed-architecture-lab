# 可重建分散式商務系統需求基線

## Metadata

- Version: `1.1-draft`
- Date: `2026-08-27`
- Owner: repository owner
- Authoring workflow: `2026-08-26-reconstructable-system-specification`
- Work item: GitHub Issue `#2`
- Scope in: 產品需求、架構、領域行為、應用流程、HTTP/MQ 契約、資料持久化、執行環境、可觀測性、測試與重建驗收。
- Scope out: 刪除現有 source code、改動產品執行行為、push、PR、merge、Issue closure、release。
- Approval status: 本文件已獲授權起草；內容核准仍與作者完成狀態分開。

## Context & Goals

本專案必須保有一套不依賴 `src/`、`tests/` 或隱藏對話脈絡的耐久規格，使未來即使移除所有產品 source code，具備 LUNA 等級能力的低成本 AI 仍可依文件重建出：

1. 與目前系統相容的公開行為與資料契約；
2. 不低於目前的 DDD、Clean Architecture、CQRS、Hexagonal Architecture 與 MQ-first 邊界品質；
3. 已改善目前明確可見的驗證、組態一致性、測試覆蓋與可靠性缺口；
4. 可由機械化驗證判斷是否完成，而不是以「看起來差不多」作為完成標準。

成功不是逐檔複製目前程式。成功是重建後的系統滿足相同或更強的需求、相容契約、架構限制與驗證 oracle。

## Personas

- Repository owner：決定哪些行為為正式產品需求、哪些相容性負擔可移除，並核准剩餘決策。
- Reconstructing AI：只能讀取本需求、`.dev/ARCHITECTURE.md`、ADR、`.dev/specs/`、`.dev/problem-frames/`、`.dev/operations/` 與 build/deployment metadata，不得假設可讀取原 source。
- Maintainer：能從文件定位每個 bounded context、use case、port、adapter、schema、channel、設定與驗證命令。
- API/MQ consumer：在重建後仍得到相容的 HTTP status/payload 與 message schema/delivery semantics。
- Operator：能配置六個 runtime host、三個 PostgreSQL database、broker 與 observability stack，並診斷 reservation/outbox failure。

## Evidence And Normative Status

每項重建敘述必須使用下列其中一種狀態；優先順序由上而下：

| Status | Meaning | Reconstruction rule |
| --- | --- | --- |
| `required` | 本需求、Accepted ADR 或 owner 決策明定 | 必須實作；不得被目前程式中的差異覆寫 |
| `compatibility` | 目前公開 API、message、database 或 runtime contract | 預設保持相容，除非 owner 另行核准 breaking change |
| `preserve` | 有測試、ADR 與實作共同證明的意圖行為 | 必須保持語意，實作形式可改善 |
| `quality-uplift` | 為達到「相同或更高品質」而新增的明確要求 | 新重建系統必須滿足；若與相容性衝突需先取得 owner 決策 |
| `observed` | 只由目前實作證明、未被需求或 ADR 採納 | 僅作反向工程證據，不自動成為需求 |
| `gap` | 現況缺少、矛盾或未驗證 | 不得宣稱完成；依本文規則修補或保持顯式未決 |
| `deferred` | 需要 owner 決策 | 不得自行猜測；採 fail-closed 或明載的 compatibility fallback |

## Functional Requirements

### SYS — System reconstruction

- `SYS-001` `required`: 重建輸入必須能從 `.dev/specs/reconstruction/README.MD` 單一路徑開始，並依明載順序完成 solution、shared contracts、bounded contexts、hosts、infrastructure 與 tests。
- `SYS-002` `required`: 每個 normative requirement 必須可追溯到 spec/ADR；每個 production spec 必須反向連結 requirement 與 repository evidence。
- `SYS-003` `required`: 重建完成不得依賴原始 `src/`、`tests/`、未提交檔案、程式知識圖 cache 或本次對話。
- `SYS-004` `required`: 重建允許使用不同但等價的內部實作；公開契約、領域不變條件、交易邊界、delivery semantics 與驗收 oracle 必須保持。
- `SYS-005` `quality-uplift`: 所有輸入驗證、錯誤語意、idempotency、concurrency 與 cancellation 行為必須明確，禁止依 framework 預設或偶然 exception 決定產品語意。

### PRD — Products bounded context

- `PRD-001` `required`: Products 擁有 `Product` aggregate 與產品目錄語言，不得把 Orders 或 Inventory 內部模型當作其 domain model。
- `PRD-002` `preserve`: 建立產品時產生 UUID v7 ID，驗證 `Name`、`Description` 非空白且 `Price >= 0`，並產生 `ProductCreated` domain event。
- `PRD-003` `preserve`: 更新產品沿用相同驗證，成功後更新欄位並產生 `ProductUpdated`。
- `PRD-004` `preserve`: 刪除是 soft delete；已刪除產品不得由 write-side load 或 query-side read 回傳，且使用 optimistic version check。
- `PRD-005` `compatibility`: 提供 create、update、delete、get-all、get-by-id HTTP/use-case 行為，契約詳見 `http-api-contracts.json` 與 domain use-case specs。
- `PRD-006` `gap`: `products.integration.events` 目前只有 route，沒有由正式 Product use case 證實的 producer。重建不得自行發明 product integration event。

### ORD — Orders bounded context

- `ORD-001` `required`: Orders 擁有 event-sourced `Order` aggregate、order lifecycle 與 order integration events。
- `ORD-002` `preserve`: 新訂單以 UUID v7 ID 建立並進入 `Placed`；事件歷史依版本順序 replay，replay 不產生 pending events。
- `ORD-003` `required`: `Ship`、`Deliver`、`Cancel` 需非空白 `reason`。任何目前狀態可轉至不同目標狀態；對相同狀態的重複要求是 no-op，不得寫入 event/outbox 或發佈 integration event。
- `ORD-004` `required`: PlaceOrder 先透過 MQ request/reply 保留庫存；reservation 失敗時不得 commit order event、read model 或 outgoing event。
- `ORD-005` `required`: order domain events、Orders read model 與 integration outbox 必須在同一 PostgreSQL transaction 寫入；成功後才標記 aggregate pending events committed。
- `ORD-006` `preserve`: event stream 以 `(StreamId, Version)` 唯一，commit 前檢查 aggregate version 對應 database version；衝突必須 fail closed。
- `ORD-007` `compatibility`: `GetOrderDetails` 回傳 order ID 與目前單一 line item 的 product ID/quantity；找不到回傳 HTTP 404。

### INV — Inventory bounded context

- `INV-001` `required`: Inventory 擁有 `InventoryItem` aggregate、stock adjustment、reservation outcome 與 stock integration events。
- `INV-002` `compatibility`: 每個 `ProductId` 最多一筆 `InventoryItem`；初始化重複 product 回傳 `InventoryItemAlreadyExists`。
- `INV-003` `quality-uplift`: 初始化 stock 必須 `>= 0`；increase、decrease、restock 與 reserve quantity 必須 `> 0`；任何成功操作後 stock 不得為負。這補強目前 aggregate 對 increase/restock/init 驗證不足的現況。
- `INV-004` `preserve`: 一般 decrease/increase/restock 先載入 aggregate、執行 domain behavior、持久化，再發佈相對應 integration event；失敗不得持久化或發佈。
- `INV-005` `required`: reservation 以 caller 提供的 `OperationId` 作 idempotency key。同 key 同 payload 必須重播原 outcome 且不得再次扣庫；同 key 不同 payload 必須回傳 terminal `OperationIdentityConflict`。
- `INV-006` `required`: reservation claim、row lock、stock decrement、terminal outcome 與成功事件的 `InventoryIntegrationOutbox` row 必須在單一 PostgreSQL transaction 完成；任一 write/stage/commit 失敗時全部 rollback，且暫時性 store failure 必須可被 retry policy 辨識。
- `INV-007` `required`: 成功 reservation 由 use case 建立 producer-owned stock-decreased integration event；source-outbox relay 以 `OperationId` 作 stable delivery/deduplication ID，以 `ProductId.ToString("N")` 作 Kafka partition key。相同 operation replay 不得建立第二個 outbox row。
- `INV-008` `compatibility`: inventory HTTP API 提供 initialize、get available quantity、increase、decrease、restock 行為。

### INT — Cross-context integration

- `INT-001` `required`: 跨 bounded context communication 只能透過 MQ contract，不得以 direct HTTP 或 domain project reference 協作。
- `INT-002` `required`: Published Language 位於 `BC-Contracts`；Domain projects 不得參考它。
- `INT-003` `compatibility`: `ReserveInventoryRequestContract` 包含 `OperationId`, `ProductId`, `Quantity`；response 包含 `OperationId`, `Result`, `FailureReason`。
- `INT-004` `required`: delivery 按 at-least-once 設計。Publisher 提供 stable message identity；consumer 對重複訊息的處理策略必須可驗證。
- `INT-005` `required`: Kafka 是目前 canonical runtime 與事件驅動驗證路徑；logical names 維持 `orders.integration.events`, `inventory.requests`, `orders.outbound.replies`, `inventory.integration.events`, `products.integration.events`。相同 entity/aggregate 的順序需求必須使用穩定 partition key，不得宣稱跨 partition 全域順序。
- `INT-006` `preserve`: Orders native source outbox relay 使用 outbox row ID 作 Wolverine deduplication/header identity、aggregate ID 作 partition key；失敗採 bounded backoff，五次後 park。
- `INT-007` `quality-uplift`: 所有六個 host 使用同一個 `Messaging` configuration contract；移除 Product hosts 的 legacy `QUEUE_SERVICE`/`BrokerConnectionString` 分岔，且 InMemory/Kafka/RabbitMq profile 都必須 fail-fast 驗證。
- `INT-008` `required`: integration event 的 business meaning、名稱、schema、相容性與版本決策由 producer bounded context 擁有；consumer 只擁有 reaction、projection、idempotency、retry 與 dead-letter policy，不得以自身模型改寫 event 語意。
- `INT-009` `deferred`: RabbitMQ 保留為可選 compatibility profile，但目前不是 canonical verification path。未來若有廣播需求，必須先比較 Kafka 多 consumer-group 與 RabbitMQ exchange + per-consumer queue；目前共享 queue 不能被描述成廣播，broker 轉換或同步部署需另行 owner 決策。

### API — HTTP boundary

- `API-001` `required`: Controller 只負責 transport mapping、use-case invocation 與 HTTP result mapping，不得直接使用 aggregate、write repository 或 message bus。
- `API-002` `required`: Request/response DTO 與 application Input/Output 分離；所有 async request 路徑傳遞 non-optional `CancellationToken`。
- `API-003` `quality-uplift`: success/error status、validation problem 與 not-found mapping 必須由 adapter spec 明定。重建不得依未處理 exception 偶然產生 500 作為已知 business outcome。

## Non-Functional Requirements

- `NFR-001` Build: 以 `global.json` 選擇 .NET SDK `10.0.302` 並允許 `latestMajor` roll-forward；所有 active product/test project 以 `net10.0` 為目標。
- `NFR-002` Architecture: Domain 無 Infrastructure/Presentation dependency；Application 擁有 inbound/outbound ports；Infrastructure 實作 adapters；Presentation 為 composition/inbound boundary。
- `NFR-003` Persistence: 所有 SQL parameterized；command transaction 保持 aggregate consistency；query port 回傳 DTO/read model，不回傳 mutable aggregate。
- `NFR-004` Reliability: Orders commit/outbox atomicity、Inventory reservation outcome/outbox atomicity、reservation idempotency、optimistic concurrency 與 at-least-once duplicate tolerance 是 hard gates。
- `NFR-005` Security/privacy: connection strings 只存在 runtime configuration；transition reason 可能含人員文字，不得預設可安全完整記錄於 logs/telemetry。
- `NFR-006` Observability: 六個 host 提供 OpenTelemetry logs/traces/metrics OTLP export；API hosts 加 ASP.NET Core instrumentation，message hosts 加 Wolverine/broker instrumentation。
- `NFR-007` Containers: 每個 host 提供 Linux multi-stage Dockerfile；restore 前顯式 copy 其遞迴 project references，以保持 restore cache。
- `NFR-008` Testing: 使用 xUnit 與 Given-When-Then semantics；遵循各 test project 已選擇的 Moq 或 NSubstitute；不得使用共享 mutable base test class。
- `NFR-009` Coverage: Products、Orders 與 Inventory 現有 oracles 必須重建；每個 bounded context 使用自己擁有的 test project/surface。
- `NFR-010` Reproducibility: solution、project graph、API/message/schema/config contract 皆有 machine-readable JSON；所有 JSON 必須可 parse，所有相對連結必須解析。
- `NFR-011` Test profiles: 一般 `dotnet test` 必須只依賴 process-local doubles/in-memory transports；需要 PostgreSQL、Kafka、RabbitMQ 或其他外部服務的測試必須明確分類並在缺少 opt-in 與連線設定時 skipped。Skipped 不得被視為該外部行為的 passing evidence。

## Constraints & Assumptions

- Dapper + Npgsql + PostgreSQL、WolverineFx、Kafka、OpenTelemetry 為目前 canonical target selections；RabbitMQ 是 deferred compatibility profile。更換或同步部署 broker 需另行 owner 決策，且不得弱化 producer ownership、ordering key、outbox atomicity 或 at-least-once 語意。
- Orders event sourcing 是 context-specific，不得套用到 Products/Inventory。
- Products soft delete 與 Orders event sourcing/outbox 是重建必要能力。
- `SharedKernel` 目前為空 placeholder；不得從 BuildingBlocks 或任一 bounded context 猜測共享 domain concepts。
- Consumer runtime 目前訂閱 channel，但缺少清楚 business handler ownership；重建需保留 host/topology compatibility，同時將無 handler 的訂閱列為 `gap`，不得宣稱已有業務效果。
- Owner 已於 2026-08-27 核准 breaking correction：`ProductStockIncreasedIntegrationEvent.IncreasedQuantity` 與 `ProductStockReturnedIntegrationEvent.ReturnedQuantity` 是 normative names；舊的錯誤 `DecreasedQuantity` 名稱不保留為相容 alias。

## Domain / Business Rules

1. Product name/description 不得空白，price 不得小於零。
2. 已 soft-deleted product 不可由正常 load/query 取得。
3. Order lifecycle transition 需要 reason；same-state transition 是無副作用 no-op。
4. Order placement 只有在 inventory reservation 成功後才能成為 durable fact。
5. Inventory stock 不得因任何成功操作成為負數。
6. Reservation operation identity 與 payload 一起定義一次性 logical operation。
7. Cross-context contract 由 producer/owning bounded context 定義，consumer 不得重定義其語意。
8. Domain events 只表示 bounded-context 內已發生的 domain decision；integration events 只在 durable transaction boundary 後對外送出。

## Acceptance Criteria

| ID | Acceptance |
| --- | --- |
| `AC-001` | 從 `.dev/specs/reconstruction/README.MD` 開始，不讀原 source，能建立與 manifest 相符的 solution、27 個 active project（22 product + 5 tests）與六個 host。 |
| `AC-002` | 重建後所有 project dependency direction 符合 blueprint，且 Domain projects 無 broker/database/Web dependency。 |
| `AC-003` | HTTP contract tests覆蓋所有 15 個列出的 endpoints、success/error/not-found mapping。 |
| `AC-004` | Domain/use-case oracles覆蓋三個 aggregates、16 個列出的 use cases 與同狀態/no-side-effect、validation、not-found paths。 |
| `AC-005` | Orders event-store + read-model + source-outbox 原子性、optimistic concurrency、stable relay identity 與 park policy 均通過 tests。 |
| `AC-006` | Inventory reservation replay/conflict/terminal-failure/cancellation、reservation + outbox rollback、stable relay identity 與 park policy scenarios 全部通過；real PostgreSQL atomicity check 不得以 skipped 代替。 |
| `AC-007` | Kafka 與 InMemory profile 的必要 configuration、logical routes、Kafka partition ordering 與 actual broker smoke test 均通過；RabbitMQ 僅驗證已宣告的 compatibility surface，除非未來升格為 canonical profile。Blocked environment 不算 passed。 |
| `AC-008` | 三個 database schema 能由 checked-in SQL/migrations 重建，schema constraints 與 persistence specs 一致。 |
| `AC-009` | JSON specs/manifest 全部 parse；problem-frame selected scope 達成 100% spec compliance；所有未決項保持 `gap`/`deferred`。 |
| `AC-010` | 兩次互相獨立的 LUNA-class clean-room reconstruction，在無 `src/`、`tests/`、`.git/`、`bin/`、`obj/`、code graph cache 與聊天歷史的 disposable copies 中完成；兩次皆需通過相同 gates，且不得讀取彼此輸出。 |
| `AC-011` | 重建後 HTTP/message/schema/runtime 外部契約逐項相符；內部程式碼允許不同或更佳設計。source deletion 仍需另外明確授權，不因本 gate 通過而自動執行。 |

## Decisions And Deferred Choices

- `DEC-001`: Products 是否要正式生產 product integration events；目前只保留 route compatibility。
- `DEC-002`: 無明確 business handler 的三個 Consumer hosts 應保留為 topology lab、補 handler，或退役。
- `DEC-003` `resolved 2026-08-27`: 以 breaking correction 修正 Inventory increase/return quantity property；producer-owned normative names 分別為 `IncreasedQuantity` 與 `ReturnedQuantity`。
- `DEC-004` `deferred`: RabbitMQ exchange/binding、每 consumer queue、broker-specific DLQ physical names，以及轉換或同步部署策略。
- `DEC-005` `resolved provisionally 2026-08-27`: Kafka 為 canonical broker；RabbitMQ 不因「廣播」一詞自動成為較佳選擇，需以實際 consumer-group/exchange topology 再評估。
- `DEC-006` `resolved provisionally 2026-08-27`: ReserveInventory 採 explicit application transaction port + PostgreSQL source outbox；owner 將依實際程式碼架構觀察後決定是否調整或擴大到其他 Inventory commands。

## References

- `.dev/ARCHITECTURE.md`
- `.dev/adr/ADR-001-reasoned-order-state-transitions.md`
- `.dev/adr/ADR-002-pluggable-durable-messaging.md`
- `.dev/requirement/distributed-commerce-bounded-context-overview.md`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- `.dev/specs/reconstruction/README.MD`
- `.dev/specs/reconstruction/system-blueprint.md`
- `.dev/specs/reconstruction/coverage-matrix.md`
- `.dev/operations/context-map.md`
- `.dev/operations/event-catalog.md`
- `.dev/operations/mq-topology.md`

## Recommended Next Handoff

本需求核准後，由 `ddd-ca-hex-architect` 維護 architecture blueprint，`spec-author` 維護 production/adapter contracts，`problem-frame-author` 維護 selected validator-ready behavior frames。
