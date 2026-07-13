# .NET 分散式訊息架構實驗室

[English](README.en.md)

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

- .NET SDK `10.0.0`、主要 target framework `net10.0`
- ASP.NET Core Web API、Scalar OpenAPI UI
- WolverineFx `5.32.1`
- Kafka（目前 Docker Compose 啟用的 broker）
- RabbitMQ（保留 packages 與部分 conditional configuration；Compose service 預設註解，Inventory request listener 尚未完整配置）
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
tools/                 Roslyn analyzers 與 runtime validators
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
docker compose -f ./docker-compose/docker-compose.yml up -d --build
```

目前 Compose 會啟動三組 API/Consumer、三個 PostgreSQL databases、Kafka/Kafdrop，以及 OpenTelemetry/Grafana observability stack。

API 預設入口：

- Orders API: `http://localhost:8080`
- Products API: `http://localhost:8090`
- Inventory API: `http://localhost:8100`

執行 solution tests：

```powershell
dotnet test MQArchLab.slnx
```

Analyzer 與 validator tests 位於 `tools/`，目前不屬於 `MQArchLab.slnx`，需要個別執行其 test projects。

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
