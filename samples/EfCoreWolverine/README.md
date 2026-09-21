# EF Core + Wolverine inbox／outbox 範例

這份獨立範例示範：Kafka consumer 呼叫 Use Case 修改 `InventoryItem`，由 Wolverine 將 aggregate 變更、outbox 訊息與 inbox 完成狀態放進同一個 PostgreSQL 交易。採用 .NET 10、EF Core 10.0.12、Npgsql EF provider 10.0.3、Wolverine 6.36.0；Compose 提供 PostgreSQL 與 Kafka。

## 先看這些程式碼

1. [DecreaseStockUseCase](EfCoreWolverine.Application/DecreaseStockUseCase.cs)：載入 aggregate → domain behavior → repository Save → publisher port；Application 沒有 EF Core／Wolverine 相依。
2. [EfInventoryRepository](EfCoreWolverine.Infrastructure/EfInventoryRepository.cs)：使用追蹤中的 aggregate；`SaveAsync()` 登記變更，**不呼叫 `SaveChanges`，也不 commit**。
3. [WolverineStockEventPublisher](EfCoreWolverine.Infrastructure/WolverineStockEventPublisher.cs)：將 Application port 接到目前處理中的 `IMessageContext`，登記 outgoing event。
4. [SampleHost](EfCoreWolverine.Host/SampleHost.cs)：共用 scoped DbContext、Eager transaction middleware、durable inbox／outbox 與 Kafka routing 的組裝位置。
5. [DecreaseStockHandler](EfCoreWolverine.Host/DecreaseStockHandler.cs)：薄 inbound adapter，只轉換輸入、呼叫 Use Case 與處理業務拒絕結果。
6. [InventoryDbContext](EfCoreWolverine.Infrastructure/InventoryDbContext.cs) 與 [測試](../../tests/EfCoreWolverine.Tests/)：EF mapping、並行控制與驗證案例。

`Application`、`Infrastructure`、`Host` 三個專案重用現有 `InventoryControl.Domains`、`IAggregateRepository<InventoryItem, Guid>` 與跨 BC integration event，正式 Inventory 已採用 EF Core；此獨立 sample 保留自己的 schemas/topics，用來對照原生 Wolverine 交易 pipeline 與正式 Inventory 的 capability-specific source outbox。Products／Orders 保留 Dapper，參見 [Inventory EF Core 指南](../../.dev/operations/inventory-efcore.md)。

## 交易由誰管理

```text
Kafka → Wolverine durable inbox
  → Eager middleware 開啟交易
    → Handler → Use Case
      → Repository.FindByIdAsync → InventoryItem.DecreaseStock
      → Repository.SaveAsync → IStockEventPublisher.PublishAsync
    → Wolverine 保存 DbContext、保存 outbox、標記 inbox 完成、commit
  → Wolverine 投遞 outgoing event → Kafka → 範例 observer
```

`SampleHost` 透過 `AddDbContextWithWolverineIntegration<InventoryDbContext>()`、`UseEntityFrameworkCoreTransactions(TransactionMiddlewareMode.Eager)` 與 `AutoApplyTransactions()` 掛接交易。Repository 使用同一個 scoped context；publisher 使用目前的 message context。**相同 connection string 本身不保證共用交易**，改動 DI 後仍須驗證實際 middleware 與交易整合。

本路徑不需要自行實作 `InboxStore.MarkProcessed()`、另一套 outbox relay 或額外 `IUnitOfWork.Commit()`。Wolverine 是唯一交易提交者；Use Case／Repository／publisher 不各自建立交易。原生 durable inbox／outbox 負責持久化、重送與投遞。

`InventoryItem.DomainEvents` 不映射成 EF entity，也不在 Save 時清除；本範例保留到 message processing scope 釋放，避免 commit 前提前確認事件。Integration event 沿用本次 domain event 的資料與發生時間。

`xmin` shadow property 是 PostgreSQL 樂觀並行控制 token；兩筆不同訊息同時修改相同庫存時，過期更新會拋出 `DbUpdateConcurrencyException`，由 Wolverine 冷卻後重試。這與 inbox 訊息防重是不同責任。庫存不足／找不到資料為業務拒絕，完成 incoming request 且不產生 stock event；持久化或 outgoing staging 例外會向外傳遞以回滾交易。

## 從儲存庫根目錄執行

需要 .NET 10 SDK、Docker Compose，以及可啟動 Linux containers 的 Docker engine。每個 PowerShell 終端都須設定相同環境變數；密碼由你選擇，不存入版本控制。

```powershell
$env:SAMPLE_POSTGRES_PASSWORD = Read-Host '請輸入本機範例 PostgreSQL 密碼' -MaskInput
$connection = [System.Data.Common.DbConnectionStringBuilder]::new()
$connection.ConnectionString = 'Host=localhost;Port=55435;Database=ef_inventory_sample;Username=sample'
$connection['Password'] = $env:SAMPLE_POSTGRES_PASSWORD
$env:ConnectionStrings__Sample = $connection.ConnectionString
$env:Kafka__BootstrapServers = '127.0.0.1:39092'
$sampleHost = 'samples/EfCoreWolverine/EfCoreWolverine.Host'

docker compose -f samples/EfCoreWolverine/compose.yaml up -d --wait
dotnet run --project $sampleHost -- --mode seed --stock 10
```

`seed` 輸出 JSON；保留其中 `Id`。這是建立示範資料的獨立操作，不會發送 stock event。另開終端，設定上述環境變數後啟動 consumer：

```powershell
dotnet run --project $sampleHost -- --mode consume
```

回到原終端，將 placeholder 換成剛才的 `Id`：

```powershell
$inventoryId = '<seed 輸出的 Id>'
dotnet run --project $sampleHost -- --mode send --id $inventoryId --quantity 2
dotnet run --project $sampleHost -- --mode inspect --id $inventoryId
```

處理是非同步的；`send` 完成表示 Kafka 接受 request，`inspect` 可能要稍後再執行。成功時庫存由 10 變為 8，consumer log 可看到經 Kafka 回送的 `StockDecreased`。預設 request／event topics 為 `ef-inventory-sample.requests`、`ef-inventory-sample.events`。

每次 `send` 都會建立**新的 envelope ID**，因此執行兩次代表兩次扣庫。Wolverine inbox 對同一 envelope 的重送防重，不等於永久的業務 `OperationId` 防重；這份範例未實作後者。`KeepAfterMessageHandling = 1 小時` 是範例選擇，需依重送／重播需求調整。Kafka offset 確認與 SQL commit 不是同一個分散式交易，不宣稱 end-to-end exactly-once。

## Schema 部署

業務 schema `ef_inventory_sample` 由 [EF migration](EfCoreWolverine.Infrastructure/Migrations/InitialInventory.cs) 管理；`seed` 明確呼叫 `MigrateAsync()`。Wolverine message schema `ef_inventory_messages` 由 `AutoBuildMessageStorageOnStartup` 在 consumer 啟動時建立／更新，與業務 migration 分開。

工作環境應先部署兩類 schema，再啟動 consumer，並依環境權限調整自動建表設定。範例也啟用 Kafka `AutoProvision()`；既有環境的 topic 建立、權限與部署流程應由你的團隊決定。

## 驗證方式與目前證據

```powershell
dotnet test tests/EfCoreWolverine.Tests/EfCoreWolverine.Tests.csproj
```

預設執行 Use Case／mapping 測試，外部整合測試跳過。先啟動專用 PostgreSQL／Kafka，再明確啟用外部測試：

```powershell
$env:RUN_EXTERNAL_INTEGRATION_TESTS = 'true'
$env:EF_SAMPLE_POSTGRES = $env:ConnectionStrings__Sample
$env:EF_SAMPLE_KAFKA = $env:Kafka__BootstrapServers
dotnet test tests/EfCoreWolverine.Tests/EfCoreWolverine.Tests.csproj
```

2026-09-17 已在 .NET SDK `10.0.401`、Docker engine `29.7.2` 與本範例 Compose 上驗證：

- 16 個測試全部通過，0 失敗、0 略過：8 個 Use Case、3 個 EF mapping／Repository、1 個 generated transaction pipeline，以及 4 個真 PostgreSQL／Kafka 測試。
- 真實整合涵蓋成功扣庫與 outgoing event、SQL flush 後故障回滾且事件未逸出 Kafka、同一 envelope 的並行／完成後重送，以及 `xmin` 過期更新衝突。
- `seed --stock 10 → send --quantity 2 → inspect` 的 CLI 流程確認庫存為 8。
- `dotnet build MQArchLab.slnx --no-restore --disable-build-servers -m:1` 成功；17 個既有專案警告，0 錯誤。

驗證專用容器在完成後清理，Docker engine 保持開啟。重跑請依上述指令設定自己的本機密碼並啟動 Compose。程序強制終止／重啟、broker 長時間中斷與超過 retention 的重播，仍應依工作環境需求另外驗收。

本次為單一實作驗證範例，依使用者 2026-09-17 明確授權豁免 Issue binding，以 direct mode 執行。此範例尚未同步成 AI Collaboration Framework 的正式規範。

## 官方參考

- [Wolverine EF Core transaction middleware](https://wolverinefx.net/guide/durability/efcore/transactional-middleware)
- [Wolverine EF Core inbox／outbox](https://wolverinefx.net/guide/durability/efcore/outbox-and-inbox)
- [Wolverine idempotency 與 retention](https://wolverinefx.net/guide/durability/idempotency)
- [Npgsql PostgreSQL xmin concurrency token](https://www.npgsql.org/efcore/modeling/concurrency.html)
