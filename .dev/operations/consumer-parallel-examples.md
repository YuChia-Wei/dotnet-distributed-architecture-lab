# 單一 Consumer 接收外部事件後並行處理

本範例由 Product API 發佈外部 Kafka 事件，Orders Consumer 的單一 `products.integration.events` listener 接收。兩項工作分別為稽核紀錄與統計紀錄，各自有獨立的 Application use case 與 outbound port。

| 模型 | 外部事件 | 執行方式 | 單一工作失敗時 |
| --- | --- | --- | --- |
| Task.WhenAll | `WhenAllWorkRequested` | `WhenAllWorkHandler` 建立兩個獨立 DI scope，等待兩項 use case 完成 | 整個外部事件重試，成功分支也可能再次執行 |
| 兩個獨立 handler | `IndependentWorkRequested` | 同一 Consumer 內，由 Wolverine 分派原始事件至 `IndependentAuditHandler` 與 `IndependentStatisticsHandler` | 各處理佇列獨立重試，成功 handler 不因另一分支失敗而重跑 |

## Task.WhenAll

入口位於 `src/Order/Presentation/SaleOrders.Consumer/Diagnostics/WhenAllWorkHandler.cs`：

```csharp
public static Task Handle(WhenAllWorkRequested message,
    IServiceScopeFactory scopes, CancellationToken cancellationToken)
    => Task.WhenAll(
        WriteAuditAsync(message.ProbeId, scopes, cancellationToken),
        RecordStatisticsAsync(message.ProbeId, scopes, cancellationToken));
```

每個 async helper 各自 `CreateAsyncScope()`、解析 use case、等待執行，再非同步釋放 scope。這避免把同一個非執行緒安全的 scoped repository／DbContext 分享給兩條分支。helper 的 async 邊界也確保某個分支同步拋錯時，另一分支仍會被等待。

`Task.WhenAll` 會等待所有工作結束，但不會因為其中一個失敗就自動取消其他工作。本例把相同的取消 token 傳入兩個獨立作業。這是使用者要求的教學協調入口；一般業務 handler 仍維持單一 use case。

## 原始外部事件與兩個 handler

組態位於 `ParallelWorkConfiguration.cs`：

```csharp
options.MultipleHandlerBehavior = MultipleHandlerBehavior.Separated;
options.LocalQueue("parallel-work-audit")
    .AddStickyHandler(typeof(IndependentAuditHandler));
options.LocalQueue("parallel-work-statistics")
    .AddStickyHandler(typeof(IndependentStatisticsHandler));
```

兩個 handler 的第一個參數都是 `IndependentWorkRequested`，各自只呼叫一項 use case：

```text
Product API → Kafka: products.integration.events → Orders Consumer
    → IndependentAuditHandler(IndependentWorkRequested) → WriteParallelAuditUseCase
    → IndependentStatisticsHandler(IndependentWorkRequested) → RecordParallelStatisticsUseCase
```

Wolverine 6.36.0 的入站 fan-out 會把原始訊息交给兩條內部處理佇列。應用程式沒有另建轉發 handler，也沒有把它轉成另一種記憶體事件；Kafka listener 與 consumer group 仍只有一組。內部佇列讓 handler 有各自的 scope、完成狀態與重試流程。參考 [Wolverine 的 external fan-out 實作](https://github.com/JasperFx/wolverine/blob/V6.36.0/src/Wolverine/Runtime/Handlers/FanoutMessageHandler.cs) 與 [Separated handler 路由](https://github.com/JasperFx/wolverine/blob/V6.36.0/src/Wolverine/Runtime/Handlers/HandlerGraph.cs)。

此範例沿用目前 host 的持久化設定，兩條新增 local queue 使用預設模式，未新增持久化訊息儲存。分派完成不等於兩項業務工作完成，也不保證程序中斷後 local queue 的未完成工作可恢复。若需要重啟後可靠續作，應另行配置持久化佇列／inbox 與 durable storage，並驗證入站確認到落盤的交接。

## 以既有 Docker Compose 執行

在 repository 根目錄執行 PowerShell。既有 `docker-compose.override.yml` 保留本機隔離的 port 設定；不需建立另一個 Kafka。

```powershell
$compose = @('-p', 'mqarchlab-pr5-integration',
    '-f', 'docker-compose/docker-compose.yml',
    '-f', 'docker-compose/docker-compose.override.yml',
    '-f', 'docker-compose/docker-compose.verification.yml')
docker compose @compose --profile verification build --pull product-api product-consumer orders-api orders-consumer inventory-api inventory-consumer regression-tests
docker compose @compose up -d --no-build
docker compose @compose --profile verification run --rm --no-deps regression-tests
pwsh -File docker-compose/scripts/Test-ParallelWork.ps1
pwsh -File docker-compose/scripts/Test-CommerceFlow.ps1
```

Verification override 僅在 Product API 啟用 `Diagnostics__ParallelWork__Enabled=true`。一般設定未啟用時，診斷 endpoint 回傳 404。HTTP 202 只代表發佈已接受，E2E 另從 Consumer 執行紀錄確認兩項工作都完成。

手動觸發：

```powershell
Invoke-RestMethod -Method Post http://localhost:8888/api/products/diagnostics/parallel-work/WhenAll
Invoke-RestMethod -Method Post http://localhost:8888/api/products/diagnostics/parallel-work/IndependentHandlers
```

回應中的 `probeId` 可透過 `?probeId=<同一識別碼>` 重送，觀察 `applied=False`。每筆請求的兩個 `started in scope` 紀錄應具有不同 scope ID，且均早於第一個 `completed` 紀錄。

範例儲存使用程序內 `ConcurrentDictionary.TryAdd` 模擬去重副作用，資料僅保留至 Consumer 結束。兩種模式應使用不同 probe ID。它不是資料庫、郵件或遠端 API 的 exactly-once 範本；實際業務需要以持久化唯一鍵或下游 idempotency key 保護副作用。500/700 ms 延遲只用來觀察重疊，不代表效能基準。

## 驗證範圍

- `WhenAllWorkHandlerTests`：以可控同步閘驗證重疊、獨立 scope、同步失敗後仍等待另一分支、取消與部分成功重試。
- `KafkaParallelWorkTests`：Compose 中連接真實 Kafka，使用每次執行獨立的 topic/group；驗證原始外部事件到兩個 handler、各分支 scope、獨立重試與重送去重。測試替換 outbound writer 以控制失敗，仍使用正式 handler、use case 與 Wolverine 路由。
- `Test-ParallelWork.ps1`：經 gateway → Product API → Kafka → 正式 Orders Consumer，驗證兩種模式的重疊、scope 與重送結果。
- `Test-CommerceFlow.ps1`：驗證既有產品、庫存、下單、Kafka 庫存預留、出貨／交付、取消及庫存不足流程。每次新增獨立 UUID 測試資料，保留資料庫與 broker volumes。

測試結果存於 `artifacts/nuget-consumer/`。未啟用外部測試時，Kafka/PostgreSQL 測試會明確標示 skipped，不能算成通過。

## NuGet 遷移注意事項

Wolverine 與四個相關 transport／runtime 套件統一為 `6.36.0`；六個 host 明確參考 `WolverineFx.RuntimeCompilation`，以支援既有動態 handler 產生。Inventory 預留流程的既有 scoped factory 另以 `AlwaysUseServiceLocationFor<IInventoryReservationOutbox>()` 在 PostgreSQL 組態中明確允許解析；其他型別維持 Wolverine 6 預設的 `ServiceLocationPolicy.NotAllowed`。這項修正由真實 Kafka 庫存預留 E2E 的失敗定位，參考 [官方逐型別 allow-list 說明](https://wolverinefx.net/guide/codegen#allow-list-for-service-location)。

Microsoft 套件更新至 `10.0.12`，`Microsoft.OpenApi` 保留相容的 `2.12.2`，因為 ASP.NET Core 10 的相依範圍小於 3.0。

五個測試專案改用 xUnit v3 `4.0.0` 的 `xunit.v3.mtp-off` 與 VSTest adapter，避免切換 .NET 10 既有 test runner。OTel Process 使用目前的 `1.18.0-rc.1`；RabbitMQ.Client.OpenTelemetry 保留 `1.0.0-rc.2`，兩者尚無可採用的 stable 版本。完整升級矩陣與驗證摘要位於本次 workflow 的 `evidence/`。

間接相依性維持其直接套件所解析的版本，未額外增加強制版本參照。`--outdated --include-transitive` 在目前 CLI 對預發行來源回傳 `Sequence contains no matching element`；納入 `--include-prerelease` 後可完成盤點。該報告含預發行候選，不能據此宣稱所有間接相依性均為最新 stable。
