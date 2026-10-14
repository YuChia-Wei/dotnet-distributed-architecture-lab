# Structurizr 小範圍試作

這是現有系統的視覺補充，未改變架構決策或業務實作。模型來源 revision：`4cca0256b96386eae76ea4e73d66cdf7cc2a5847`；核對日期：2026-10-14。既有 [架構文件](../.dev/ARCHITECTURE.md)、[Context Map](../.dev/operations/context-map.md)、[MQ Topology](../.dev/operations/mq-topology.md) 繼續擁有原本的文字說明與決策；此處不複製另一份規格或 ADR。

- [workspace.dsl](workspace.dsl)：單一模型、兩個固定 view key；每個元素有責任，每個 Container 有技術，每個關係有動作與已確認通訊技術。
- [兩張圖預覽](diagrams.md)：從 MCP parse 結果生成的 Mermaid Container 與時序呈現。
- [試作與團隊應用複習筆記](LEARNING-NOTES.zh-TW.md)：本次對話的經驗、Agile 整合建議、工具適用範圍與用量快照；供複習，未自動採用為團隊規則。
- [原生 Mermaid 匯出](exports/)：Structurizr MCP `export_mermaid` 的兩張視圖。
- [MCP 結果與完整 findings](evidence/mcp-results.json)、[解析 workspace](evidence/workspace.json)：此次驗證證據，不能證明產品 runtime 通過。

## 圖能回答什麼

| 圖 | 工程問題 | 實作範圍 |
| --- | --- | --- |
| `CoreContainers` | 前後台如何進 API？哪些程序可分開部署？資料屬於哪個 context？HTTP 與 Kafka 在哪裡交界？Orders 預留庫存經哪個入口？ | Vue ×2、YARP、四 API、三 Consumer、四 PostgreSQL 資料庫、Kafka、外部供應商。Procurement 沒有獨立 Consumer，Relay 在 API 內。 |
| `GoodsReceipt` | 接單為何不加庫存？收貨與事件如何一起提交？哪裡可能重送？誰負責冪等？`published_at` 能否證明入庫？ | direct 供應商接受後，另一個實際收貨操作產生 GoodsReceived；兩個本地交易經非同步訊息串接。 |

## 實作證據對照

| 模型內容／動態步驟 | 直接證據 |
| --- | --- |
| 四個 API、三個 Consumer、四個 context DB、Kafka 的部署單位 | [base Compose](../docker-compose/docker-compose.yml)、[Procurement overlay](../docker-compose/docker-compose.procurement.yml)。只畫程序、資料儲存與外部邊界，不畫 Domain/Application/Infrastructure 專案。 |
| 前後台靜態資產與 YARP 路徑 | [frontend overlay](../docker-compose/docker-compose.frontend.yml)、[Routes](../docker-compose/config/frontend-lab/RoutesSetting.json)、[Clusters](../docker-compose/config/frontend-lab/ClustersSetting.json)、[前台 API client](../src/Frontend/Web/src/api.ts)、[後台 API client](../src/Frontend/Admin/src/lib/api.ts)。SPA 的 HTTP API 呼叫發生於瀏覽器，不是 Nginx 對 API 發出請求。 |
| Orders 預留請求與回覆 | [Orders host](../src/Order/Presentation/SaleOrders.WebApi/Program.cs)、[Inventory API host](../src/Inventory/Presentation/InventoryControl.WebApi/Program.cs)：inventory.requests → Inventory API；orders.outbound.replies → Orders API。不是對 Inventory Consumer 發 HTTP。 |
| Consumer 訂閱及其限制 | [Products Consumer](../src/Product/Presentation/SaleProducts.Consumer/Program.cs)、[Orders Consumer](../src/Order/Presentation/SaleOrders.Consumer/Program.cs)、[Inventory Consumer](../src/Inventory/Presentation/InventoryControl.Consumer/Program.cs)。Products/Inventory 的 orders topic listener 只確認配置，未補上未知業務反應。Products → Orders 的診斷通道保留一條摘要以解釋 Orders Consumer，省略診斷工具細節。 |
| 步驟 1–6：唯一採購身分、外部接受、本地 Accepted | [CreatePurchaseUseCase](../src/Procurement/DomainCore/Procurement.Applications/ProcurementOperations.cs)、[HTTP supplier gateway](../src/Procurement/DomainCore/Procurement.Infrastructure/HttpSupplierGateway.cs)、[PostgresPurchaseStore](../src/Procurement/DomainCore/Procurement.Infrastructure/PostgresPurchaseStore.cs)。ApplyOutcomeAsync 只改供應商狀態，沒有收貨事件／庫存寫入。 |
| 步驟 7–9：另一個收貨 POST 與交易 T1 | [Controller](../src/Procurement/Presentation/Procurement.WebApi/ProcurementController.cs)、[ReceiveGoodsUseCase](../src/Procurement/DomainCore/Procurement.Applications/ProcurementOperations.cs)、[PurchaseOrder.Receive](../src/Procurement/DomainCore/Procurement.Domains/PurchaseOrder.cs)、[CommitAsync](../src/Procurement/DomainCore/Procurement.Infrastructure/PostgresPurchaseStore.cs)：鎖採購單、驗證正數／可收狀態／剩餘量；採購狀態、procurement_receipts、procurement_outbox 同交易。 |
| 步驟 10–12：同程序 Relay 與 durable transport | [Procurement host](../src/Procurement/Presentation/Procurement.WebApi/Program.cs)、[ProcurementOutboxRelay](../src/Procurement/DomainCore/Procurement.Infrastructure/ProcurementOutboxRelay.cs)：租約、SKIP LOCKED、固定 ReceiptId／ProductId N partition key、8 次失敗後 park。await PublishAsync 成功才標記來源 published_at；它代表 Wolverine durable-outbox 交接，並非 Kafka／下游完成。 |
| 步驟 13–14：交易 T2 與冪等 | [GoodsReceivedHandler](../src/Inventory/Presentation/InventoryControl.Consumer/Messaging/GoodsReceivedHandler.cs)、[ApplyGoodsReceiptUseCase](../src/Inventory/DomainCore/InventoryControl.Applications/Receipts/InventoryGoodsReceipt.cs)、[PostgresInventoryGoodsReceiptStore](../src/Inventory/DomainCore/InventoryControl.Infrastructure/Applications/Repositories/PostgresInventoryGoodsReceiptStore.cs)：ReceiptId claim、既有庫存鎖、庫存增加、結果與 StockIncreased source outbox 同交易。相同 ReceiptId/PO/Product/Quantity 重播回傳原結果；內容衝突失敗；缺庫存列不自動初始化。 |
| 已存在的測試與未執行界線 | [ReceiptScenarios](../tests/Procurement.Tests/ReceiptScenarios.cs)、[ReceiptPostgresScenarios](../tests/Procurement.Tests/ReceiptPostgresScenarios.cs)、[Inventory PG tests](../tests/InventoryControl.Tests/PostgresInventoryGoodsReceiptStoreTests.cs)、[跨 context 測試規格](../.dev/specs/tests/cross-domain/procurement-inventory-receipt.test-spec.md)。可對照部分收貨、重播、衝突、並行與 rollback；本試作只讀測試，未執行測試、資料庫或 broker recovery。 |

**供應商接受採購不等於庫存增加。** 接單與收貨是兩次獨立業務操作；只有實際收貨提交後的 GoodsReceived 會驅動 Inventory。T1 與 T2 不是分散式 SQL 交易；傳輸允許重複，不能稱為全域 exactly-once。步驟 11–12 是邏輯階段，transport 非同步送出可能與來源標記交錯，不保證兩個程序事件的總排序。

## 範圍、簡化與疑問

此版選取目前 Compose 的 Kafka profile，加 frontend-lab/procurement-lab overlays，並聚焦 direct supplier。不是執行中環境的觀測結果，也不是部署圖。

- 每個 Vue 方塊合併該應用的瀏覽器 SPA 與 Nginx 資產託管；兩個方向的箭頭分別表示瀏覽器 API 呼叫、YARP 取得靜態資產。未另畫人、瀏覽器程序或網路節點。
- 外部供應商用一個 software system 邊界，direct 實際指向 SupplierSandbox；外部內部資料庫不展開。wiremock、microcks、管理介面與代理鏈依 [供應商實驗指南](../.dev/operations/procurement-supplier-lab.md)，本版省略工具細節，不宣稱三條路徑部署相同。
- 不把 Outbox 表、Relay 類別、契約或 domain project 畫成獨立部署單位。各表與兩階段來源／transport Outbox 在關係及步驟說明。
- 省略 observability、測試工具、health check、schema migration 與詳細錯誤分支。動態圖走接受與首次有效收貨成功路徑，部分收貨／重播／衝突以文字補充；不代表它們未實作。
- Products Consumer 及 Inventory Consumer 的 orders topic listener 有設定，具體業務用途仍待確認；圖不猜測投影或補償行為。未因 Compose depends_on、DI 註冊或 connection string 就畫 Consumer 資料庫寫入。
- Products 的業務整合事件、Kafka + RabbitMQ 雙廣播、RabbitMQ runtime parity 都不列為已實作；現行圖只畫 Kafka，不從未採用提案補出額外連線。
- 未確認的 consumer business intent、broker DLQ 實體命名、consumer group 最終 runtime 配置、實際重送觀測，延續 [Context Map](../.dev/operations/context-map.md) 與 [MQ Topology](../.dev/operations/mq-topology.md) 的疑問。它們需要 handler／runtime 證據，本試作未執行外部實驗。

## 驗證與 findings

Structurizr MCP `validate`：**passed / OK**；`parse`：**passed**；`inspect` 呼叫成功，但**仍有下列 4 個 ERROR findings，非 clean pass**。全文保存在 [mcp-results.json](evidence/mcp-results.json)。

| 最終 inspect finding（原文） | 此次處置 |
| --- | --- |
| The software system "Distributed commerce lab" has containers, but is missing documentation. | 未將既有 Markdown 複製／嵌入 workspace；此 README 連回原權威。DSL 驗證仍成功，此 inspection 要求尚未滿足。 |
| The software system "Distributed commerce lab" has containers, but is missing decisions. | 未新增或搬移 ADR。小範圍 as-is 模型不產生新的產品決策，此 inspection 要求尚未滿足。 |
| The software system "Distributed commerce lab" is disconnected - add a relationship to/from it, or consider removing it from the model. | 關係只連實際 Container；關閉 implied relationships，避免額外摘要邊。系統邊界本身未連線，因此此 finding 保留。 |
| The software system named "Distributed commerce lab" is not included on any views - add it to a view. | 只建立要求的 Container／Dynamic 視圖；系統是 scope／邊界，不是視圖 elements 陣列中的方塊。未為消除 finding 多加第三張圖。 |

初稿另有 workspace scope 未定義的 ERROR，已加 `configuration { scope softwaresystem }` 修正；初稿 5 項與最終 4 項均保留。未關閉 inspection，也未用靜態驗證宣稱架構／業務驗收通過。

數量直接取自 MCP parse 的 view 陣列，系統外框不算一個額外元素：

| View key | elements.length | relationships.length | 不同 relationship ID |
| --- | ---: | ---: | ---: |
| CoreContainers | 16 | 25 | 25 |
| GoodsReceipt | 8 | 14 | 8 |

Dynamic 的 14 是有順序的互動實例；同一模型關係可使用多次，因此不同 ID 只有 8。以下在 repository 根目錄重新計數：

```powershell
$workspace = Get-Content -Raw .\structurizr\evidence\workspace.json | ConvertFrom-Json
@($workspace.views.containerViews) + @($workspace.views.dynamicViews) | ForEach-Object {
    [pscustomobject]@{
        View = $_.key
        Elements = @($_.elements).Count
        Interactions = @($_.relationships).Count
        UniqueRelationships = @($_.relationships.id | Sort-Object -Unique).Count
    }
}
```

重驗方式：將 workspace.dsl 的完整文字傳給 Structurizr MCP 的 validate、inspect、parse，保留每個回應；parse 輸出取代 evidence/workspace.json，重新計數並執行 export_mermaid（viewKey 分別為 CoreContainers、GoodsReceipt），重建預覽。證據與匯出檔都是衍生結果，不能手動改成與 DSL 不同的模型。

codebase-memory MCP 原索引聲稱 HEAD 相符但缺少 Procurement 定義，故本次重建 fast index（persistence=false；專案名稱 C-gitproj-YuChia-dotnet-distributed-architecture-lab），再透過 search_graph、search_code、get_code_snippet、trace_path 探索。新索引排除了 samples/docs 等目錄，且 class call trace 不完整；material claims 均直接回讀 tracked code/config/test。圖不是圖索引自動推斷的事實。採用 ddd-ca-hex-architect 的通用責任／一致性邊界方法；本次 DSL/Markdown 工作未宣稱取得 .NET specialist knowledge 的機械化覆蓋或產品 compliance 結論。

## Windows PowerShell 本機預覽

前提：Docker Desktop 可用。使用官方 [Structurizr local quickstart](https://docs.structurizr.com/local/quickstart) 的目前映像／local 模式；正式採用應另選固定版本。使用者已自行啟動 **127.0.0.1:8081** 與 **structurizr-arch-lab**，課堂的 8080 不動；下面保留相同指令供下次啟動，目前容器仍在執行時不需重跑。

在 repository 根目錄執行；檢視器產生的根層 workspace.json 與 .structurizr/ 已由此資料夾的 .gitignore 排除，保留在磁碟，evidence/workspace.json 則仍是需保留的 MCP 證據：

```powershell
Set-Location 'C:\gitproj\YuChia\dotnet-distributed-architecture-lab'
$modelDirectory = (Resolve-Path .\structurizr).Path
docker run -d --rm --name structurizr-arch-lab `
  -p 127.0.0.1:8081:8080 `
  --mount "type=bind,source=$modelDirectory,target=/usr/local/structurizr" `
  structurizr/structurizr:latest local
```

瀏覽器開啟 http://127.0.0.1:8081/workspace/1/diagrams ，選 CoreContainers 或 GoodsReceipt。結束時執行 `docker stop structurizr-arch-lab`。模型更新後重新整理。舊教學的 [Lite quickstart](https://docs.structurizr.com/lite/quickstart) 使用另一個映像；此處指令依目前 local 文件，未修改現有 Compose。

使用者啟動後的唯讀檢查：容器 running、HTTP 根頁與 diagrams 頁均為 200，檢視器載入的兩張圖數量與 MCP 一致；日誌顯示 Local v2026.09.19，image ID 為 sha256:c59b18bd7bae0cfd976a29119217eb50ab402cbc120149d399fcc001de32e6a5。這是服務可達證據，不代表已完成瀏覽器互動／完整排版驗收，也不是產品系統的部署或 E2E 驗證。

本機檢查紀錄見 [final-checks.json](evidence/final-checks.json)。

## 換電腦快速 Demo

只展示架構圖時，不需要 .NET SDK、Node.js、Codebase Memory MCP、Structurizr MCP，也不需要啟動本專案 API、Kafka 或資料庫。準備 Docker Desktop（Windows 使用 Linux containers），以及本資料夾的 `workspace.dsl` 即可；建議連同 README.md、diagrams.md 一起帶走。MCP 是建立／驗證模型時使用，檢視既有模型不需要 AI，也不消耗 AI tokens。

目前這些檔案尚未 commit；在其他電腦只 clone 遠端 repository 不會取得本次試作，請先手動複製 `structurizr/` 資料夾。`.structurizr/` 與根層 `workspace.json` 是本機檢視器狀態，第一次 demo 可不複製；`evidence/workspace.json` 是另一份 MCP 證據，與啟動無關。

### 有網路：複製資料夾後啟動

1. 啟動 Docker Desktop，在 PowerShell 執行 `docker version`，確認 Server 可連線。
2. 切換至包含 `workspace.dsl` 的資料夾；下面路徑改成新電腦的實際位置。
3. 貼上啟動指令。第一次 pull 需要網路，後續可使用已下載的映像。

```powershell
Set-Location 'D:\demo\structurizr'
if (-not (Test-Path -LiteralPath .\workspace.dsl)) { throw '此資料夾找不到 workspace.dsl' }
$modelDirectory = (Get-Location).Path
docker pull structurizr/structurizr:latest
docker run -d --rm --name structurizr-arch-lab `
  -p 127.0.0.1:8081:8080 `
  --mount "type=bind,source=$modelDirectory,target=/usr/local/structurizr" `
  structurizr/structurizr:latest local
```

開啟以下網址；啟動需要數秒，若尚未就緒可稍後重新整理：

- [核心 Container 圖](http://127.0.0.1:8081/workspace/1/diagrams#CoreContainers)
- [採購收貨入庫動態圖](http://127.0.0.1:8081/workspace/1/diagrams#GoodsReceipt)

Demo 順序建議：先用 Container 圖說明四個 context 與資料所有權，再看 GoodsReceipt，指出「供應商接受不等於庫存增加」、T1/T2 與 Outbox／冪等邊界。這是架構模型展示，沒有執行真實採購或入庫。

### 停止、重開與排除問題

```powershell
# 查看狀態與啟動訊息
docker ps --filter name=structurizr-arch-lab
docker logs --tail 50 structurizr-arch-lab

# Demo 結束
docker stop structurizr-arch-lab
```

`--rm` 會在停止後移除容器，但掛載資料夾與 Docker image 仍保留。下次重新執行 `docker run` 區塊即可，不使用 `docker start`；沒有要更新映像時可略過 `docker pull`。

- 名稱衝突：先用 `docker ps -a --filter name=structurizr-arch-lab` 查看；若就是已啟動的 demo，直接開網址。若要重開，確認後停止自己的 demo，再執行 run。
- 埠 8081 被占用：改成 `-p 127.0.0.1:8082:8080`，網址同步改為 8082；課堂檢視器的 8080 不動。
- 掛載錯誤：確認 `$modelDirectory` 是新電腦上包含 workspace.dsl 的絕對路徑，並允許 Docker Desktop 存取該資料夾。
- 頁面錯誤：先查 logs；圖頁路徑是 `/workspace/1/diagrams`。
- 模型內容更新：編輯掛載資料夾中的 workspace.dsl，再重新整理圖頁。

### 沒網路：事先攜帶 Docker image

在有網路的電腦，先切換到自行選定的 demo 傳輸資料夾，匯出映像；把產生的 tar 與模型資料夾一起帶到目標電腦：

```powershell
docker pull structurizr/structurizr:latest
docker image save --output .\structurizr-demo-image.tar structurizr/structurizr:latest
```

目標電腦先安裝並啟動 Docker Desktop，再從 tar 所在位置匯入：

```powershell
docker image load --input .\structurizr-demo-image.tar
```

接著切換到包含 workspace.dsl 的資料夾，執行前面的變數設定與 `docker run` 區塊，略過 pull。傳輸兩台電腦需有相容的 image／CPU 平台；上述離線步驟未在此次試作實測。匯出 tar 可保留同一份映像，避免 demo 當天 `latest` 更新而改變行為；請勿把大型 image tar 放進 Git。

## 試用判斷與維護

本次證明同一份 DSL 能共用元素、產生拓撲與互動視圖，並經 MCP 檢查／解析／匯出，適合先拿來做 onboarding、呼叫邊界討論和收貨一致性審查。25 條邊的全圖密度較高，深究單一流程時應看 Dynamic 圖。使用者已啟動本機 image，HTTP 可達；原生檢視器的完整視覺排版、團隊協作、權限、發布與 CI 整合尚未驗收；不把這次語法成功當成全面導入評估。

未來遇到下列變更應同步更新 DSL、對照證據、兩張匯出與 parse/count/inspection 結果：

- API/Consumer 拆分、Relay 移至獨立 worker、資料庫所有權或部署 overlay 改變。
- 前端資產託管／API 路徑／YARP cluster、supplier profile 或供應商通訊契約改變。
- Kafka topic、request/reply 路由、broker、多目的地交付、partition key／穩定訊息識別改變。
- 接單與收貨語意、ReceiptId 冪等鍵、交易原子範圍、庫存初始化前提、Outbox handoff／完成標記改變。
- 未知 listener 的業務反應被正式實作，或新的 runtime 證據推翻本次配置／來源觀察。

本次只新增 structurizr/ 文件與證據；分支 docs/structurizr-pilot（base main）。未 commit、push、部署、修改業務程式碼、資料庫、Compose 或 AI 規則。
