# .NET 分散式訊息架構實驗室

[English](README.en.md)

英文翻譯文件為 `README.en.md`。

`dotnet-mq-arch-lab` 是以 .NET 10 建立的分散式商務範例專案，用來實作與驗證 DDD、Clean Architecture、CQRS、事件驅動整合、Outbox、Event Sourcing，以及以訊息佇列進行 bounded-context 協作的做法。

Repository 同時維護一套可重用的 AI collaboration context；產品真相以 `src/`、`tests/`、`docker-compose/` 與 `.dev/` 中經驗證的專案文件為準，可攜式 AI 規則則以 `.ai/assets/` 為準。

## Bounded Contexts

| Context | Responsibility | Runtime hosts |
| --- | --- | --- |
| Products | 商品建立、查詢、更新與刪除 | `SaleProducts.WebApi`, `SaleProducts.Consumer` |
| Orders | 訂單建立與 shipped/delivered/cancelled lifecycle | `SaleOrders.WebApi`, `SaleOrders.Consumer` |
| Inventory | 商品庫存初始化、增加、扣減與補貨 | `InventoryControl.WebApi`, `InventoryControl.Consumer` |

跨 context contracts 位於 `src/BC-Contracts/`。Orders 與 Inventory 的庫存預留流程透過 Wolverine request/reply 與 MQ channels 協作；integration events 透過各 context 擁有的 topic/queue 發布。

## 技術棧

- .NET SDK `10.0.302`（`global.json` 允許 `latestMajor` roll-forward）、主要 target framework `net10.0`
- ASP.NET Core Web API、Scalar OpenAPI UI
- WolverineFx `5.32.1`
- Kafka（canonical broker；目前 Docker Compose 啟用，並以 producer-selected partition key 驗證同一業務實體的順序消費）
- RabbitMQ（deferred compatibility profile；Compose service 預設註解，目前共享 queue 不是廣播拓撲，是否轉換或同步部署需另行評估）
- PostgreSQL 16、Dapper `2.1.72`、Npgsql `10.0.2`
- xUnit `2.9.3`、Moq、Shouldly
- OpenTelemetry、Prometheus、Tempo、Loki、Grafana

精確版本與證據路徑見 [.dev/project-config.yaml](.dev/project-config.yaml) 與 [.dev/requirement/TECH-STACK-REQUIREMENTS.MD](.dev/requirement/TECH-STACK-REQUIREMENTS.MD)。

## 專案結構

```text
src/
  BC-Contracts/       跨 bounded-context contracts
  BuildingBlocks/     無業務語意的共用抽象
  Shared/             尚未填入 domain concepts 的 Shared Kernel placeholder
  Product/            Products bounded context
  Order/              Orders bounded context
  Inventory/          Inventory bounded context
tests/                 產品與 domain tests
docker-compose/        本機服務與 observability topology
sql-script/            PostgreSQL 初始化腳本
.dev/                  專案知識、requirements、specs、operations 與 workflows
.ai/                   Canonical reusable AI context
.agents/, .claude/     Runtime-specific skill wrappers
```

Solution 入口為 `MQArchLab.slnx`。產品 project 採 `DomainCore` 與 `Presentation` 分層；每個 bounded context 各自擁有 Application、Domain、Infrastructure、Web API 與 Consumer projects。

## 啟動本機環境

必要條件：

- .NET 10 SDK
- Docker 與 Docker Compose

啟動完整環境：

```powershell
docker compose `
  -f ./docker-compose/docker-compose.yml `
  -f ./docker-compose/docker-compose.override.yml `
  up -d --build
```

目前 Compose 會啟動三組 API/Consumer、無身分認證的 YARP Gateway、三個 PostgreSQL databases、Kafka/Kafdrop，以及 OpenTelemetry/Grafana observability stack。

預設 host 入口：

- YARP Gateway（無身分認證）：`http://localhost:8888`（`/api/orders`、`/api/products`、`/api/inventory`）
- Grafana：`http://localhost:3001`

`docker-compose.override.yml` 只讓 YARP Gateway 與 Grafana 發布 host ports；APIs、Consumers、Kafka、Kafdrop、PostgreSQL、OpenTelemetry Collector、Tempo、Loki 與 Prometheus 僅透過 Compose 內部 network 通訊。基礎 `docker-compose.yml` 保持原始 standalone bindings，不受此部署 profile 影響。

### 查詢錯誤與例外

開啟 Grafana 的 [System Errors & Exceptions](http://localhost:3001/d/system-errors-exceptions/system-errors-exceptions) dashboard，即可依 service 與文字快速篩選 `Error`、`Critical`、`Fatal` logs，以及任何帶有 exception metadata 的 log。展開具有 `trace_id` 的 log 後，按下 `View trace` 會直接開啟對應的 Tempo trace；背景工作若沒有 active trace context，則只會顯示 log，不會建立無法對應的連結。

Orders 與 Inventory APIs 目前將 `wolverine_node_assignments` health-check traces 取樣為每 10 分鐘最多保留一次，避免預設約每 10 秒的背景檢查淹沒 Tempo，又保留少量診斷資料：

```csharp
options.Durability.NodeAssignmentHealthCheckTraceSamplingPeriod = TimeSpan.FromMinutes(10);
```

程式碼旁也保留以下「完全不輸出」範例，但以註解停用，因此目前不會套用：

```csharp
// options.Durability.NodeAssignmentHealthCheckTracingEnabled = false;
```

這兩個設定 API 自 WolverineFx `5.9.0` 起提供，適用於本專案的 `5.32.1`，並仍存在於 Wolverine `6.x`。若使用 `DurabilityMode.Solo`，Wolverine `5.39.5` 與 `6.19.0` 曾有取樣週期無法抑制 recurring trace 的已知問題；本 Compose 使用預設的 Balanced mode，不受該 Solo-mode 問題影響。

### 驗證 Wolverine Consumer 例外處理

Compose 會明確啟用僅供實驗使用的 exception-policy probe；直接以其他設定啟動 Product API 時，此功能預設關閉並回傳 HTTP 404。Probe 不會修改產品、庫存或訂單資料。

透過無身分認證的 YARP Gateway 觸發 timeout policy：

```powershell
$probe = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8888/api/products/diagnostics/consumer-exception-policy/timeout
$probe
```

或觸發未分類例外的 fallback policy：

```powershell
$probe = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8888/api/products/diagnostics/consumer-exception-policy/unhandled
$probe
```

兩個端點都會回傳 HTTP 202，以及可用來追蹤整段處理流程的 `probeId`。不支援的 failure kind 會回傳 HTTP 400。

使用回傳的 `probeId` 查看 Orders Consumer 的 handler 執行紀錄：

```powershell
$handlerPattern = "Consumer exception policy probe $($probe.probeId) is throwing"
docker logs orders-consumer 2>&1 | Select-String -SimpleMatch $handlerPattern
```

預期 `timeout` 共執行 4 次（初次執行加 3 次 scheduled retries），`unhandled` 共執行 2 次（初次執行加 1 次 retry）。所有嘗試耗盡後，訊息會進入 Kafka native dead-letter topic `wolverine-dead-letter-queue`。

從 DLQ 找出這次 probe 的 exception type、`attempts` header 與 payload：

```powershell
docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh `
  --bootstrap-server localhost:9092 `
  --topic wolverine-dead-letter-queue `
  --from-beginning `
  --timeout-ms 10000 `
  --property print.headers=true 2>&1 |
  Select-String $probe.probeId
```

`timeout` 的 terminal record 應包含 `System.TimeoutException` 與 `attempts:4`；`unhandled` 應包含 `System.InvalidOperationException` 與 `attempts:2`。Topic 會保留先前的實驗訊息，因此請以本次回傳的 `probeId` 篩選。

執行 solution tests：

```powershell
dotnet test MQArchLab.slnx
```

本 repository 目前沒有 active target-owned analyzer 或 runtime-validator projects。它們已在受治理的 v0.9 AI context 升級中退役，v0.13 framework 也已移除先前的 bundled mechanical-validation provider。現在僅保留 `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/` 下的 reference-only recipes；它們未被選用、未加入 `MQArchLab.slnx`、未接入 build，也未啟用。

## 專案知識入口

- [.dev/ARCHITECTURE.md](.dev/ARCHITECTURE.md)：目前產品架構與依賴邊界
- [.dev/requirement/distributed-commerce-bounded-context-overview.md](.dev/requirement/distributed-commerce-bounded-context-overview.md)：bounded-context requirement baseline
- [.dev/specs/INDEX.MD](.dev/specs/INDEX.MD)：domain 與 test specs
- [.dev/operations/context-map.md](.dev/operations/context-map.md)：context relationships
- [.dev/operations/event-catalog.md](.dev/operations/event-catalog.md)：events 與 request/reply contracts
- [.dev/operations/mq-topology.md](.dev/operations/mq-topology.md)：Kafka/RabbitMQ topology

## AI 協作入口

- `AGENTS.md`：canonical agent collaboration guide
- `.ai/INDEX.MD`：canonical AI asset index
- `.ai/assets/skills/README.MD`：canonical skill registry
- `.agents/skills/README.md`、`.claude/skills/README.md`：runtime wrappers
- `.dev/guides/ai-collaboration-guides/README.MD`：human-facing 使用指南

AI context 更新後若專案真相被來源 framework 覆蓋，使用 `repo-structure-sync` 依 repository evidence 重建，不得直接沿用來源 repo 的產品名稱、credentials、ports、domains 或 workflow records。
