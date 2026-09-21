# Inventory 的 EF Core 練習路徑

Inventory 正式 runtime 使用 EF Core；Products 與 Orders 保留 Dapper。三個 context 仍各自擁有資料庫與 domain，透過訊息契約協作，適合對照 ORM 實作與共同的 DDD／Clean Architecture 邊界。

## 建議閱讀順序

1. `src/Inventory/DomainCore/InventoryControl.Domains/InventoryItem.cs`：庫存業務規則，沒有 EF Core 相依。
2. `src/Inventory/DomainCore/InventoryControl.Applications/`：Use Case、query 與 capability-specific outbox ports。
3. `src/Inventory/DomainCore/InventoryControl.Infrastructure/Persistence/`：DbContext 與既有 PostgreSQL schema 的 mapping。
4. 同一 Infrastructure 的 `Applications/Repositories/`：aggregate/query repository、庫存與預留交易、outbox staging。
5. `BuildingBlocks/InventoryIntegrationOutboxRelay.cs`：獨立 scope 中讀取已提交事件並送往 Wolverine／Kafka。
6. `tests/InventoryControl.Tests/`：mapping、DI、查詢、並行、重送與回滾案例。

對照 Dapper 可閱讀 Products 的 `ProductDomainRepository`，以及 Orders 的 `OrderEventSourcingRepository`。Orders 保留 event sourcing，是額外的 domain 能力，不代表使用 Dapper 就必須採用 event sourcing。

## 交易與 context lifetime

一般查詢使用 EF Core LINQ；PostgreSQL row lock、operation claim 與 outbox lease 等並行語意使用參數化 EF SQL。更換 ORM 不改 API、事件內容或現有資料表名稱。

庫存更新與 outgoing intent 由 `IInventoryStockOutbox` 的 adapter 在同一個 local transaction 完成。預留 adapter 僅在新 operation 首次成功時呼叫 event factory，將 OperationId、業務結果、庫存變更及 outbox 一起提交；相同 OperationId 和 payload 重送只回傳原結果，不再 staging，payload 不同則拒絕。即使已發布 outbox row 被 retention 清除或 legacy operation 缺少 row，也不由一般重送補建；缺失資料須依 [MQ topology 的恢復邊界](mq-topology.md) 另行明確處理。

Request scope 內參與操作的 adapters 使用同一個 DbContext。背景 relay 另外建立 scope；同一個 DbContext 不跨平行作業使用。Relay 只發送已提交記錄，保持穩定 message ID、partition key、重試、park 與 retention 行為。SQL commit 與 broker acknowledgement 不屬於同一個分散式交易，消費端仍須處理 at-least-once delivery。

[samples/EfCoreWolverine](../../samples/EfCoreWolverine/README.md) 留作另一種交易組裝方式的比較：它使用 Wolverine 原生 Eager middleware 與 EF inbox／outbox enrollment。正式 Inventory 延續既有 source-outbox contract，沒有額外疊一層 Wolverine EF transaction completion owner。

## 現有資料與 schema

`inventoryitems`、`inventoryreservationoperations`、`inventoryintegrationoutbox` 延續既有 lowercase PostgreSQL 名稱。Schema 由 [初始化 SQL](../../docker-compose/sql-script/create_inventoryitems_table.sql) 與 [既有 migrations](../../docker-compose/sql-script/migrations/inventory/) 管理。Runtime 不呼叫 `EnsureCreated` 或自動 EF migration；既有 volumes 可繼續使用。

## 執行與驗證

一般測試：

```powershell
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj
```

PostgreSQL 測試依 [tests/README.md](../../tests/README.md) 設定 opt-in 與連線資訊。每次建立 UUID 專用 schema，套用正式初始化 SQL，結束後只刪除該次 schema；不清除既有 public tables。未啟用外部測試時會明確標示 skipped。

現有 Compose 環境：

```powershell
$compose = @('-p', 'mqarchlab-pr5-integration',
    '-f', 'docker-compose/docker-compose.yml',
    '-f', 'docker-compose/docker-compose.override.yml',
    '-f', 'docker-compose/docker-compose.verification.yml')
docker compose @compose --profile verification build inventory-api regression-tests
docker compose @compose up -d --no-build
docker compose @compose --profile verification run --rm --no-deps regression-tests
pwsh -File docker-compose/scripts/Test-CommerceFlow.ps1
```

此回歸流程涵蓋 Dapper 商品與訂單、EF Core 庫存及真 Kafka 預留。獨立 Wolverine sample 的外部測試另需它的 `EF_SAMPLE_POSTGRES`／`EF_SAMPLE_KAFKA` 設定，預設不會由上面的 Compose 指令啟用。完整本次驗證結果以 [workflow](../workflows/2026-09-21-inventory-efcore-integration/workflow-plan.md) 為準。
