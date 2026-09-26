# 採購、供應商與實際收貨實驗

這份操作說明對應 workflow `2026-09-26-procurement-supplier-lab` 與 Issue #17。實驗使用單品採購單、獨立供應商 sandbox、WireMock.Net 與 Microcks，以及既有的 Inventory/Kafka。採購接單與出貨不會增加庫存；登錄實際收貨才會透過 `GoodsReceived` 與 Inventory 入庫。下列命令是重現步驟，成功與否以當次執行及保存的證據為準。

## 啟動與資料庫

在 repository 根目錄使用 PowerShell 7 與 Docker Compose。明確指定原有整合專案、三個既有檔案及新增 overlay：

```powershell
$compose = @(
  '-p', 'mqarchlab-pr5-integration',
  '--profile', 'procurement-lab',
  '--profile', 'verification',
  '-f', 'docker-compose/docker-compose.yml',
  '-f', 'docker-compose/docker-compose.override.yml',
  '-f', 'docker-compose/docker-compose.verification.yml',
  '-f', 'docker-compose/docker-compose.procurement.yml'
)
docker compose @compose config --quiet
./scripts/procurement-lab/Start-Lab.ps1
docker compose @compose ps
```

`Start-Lab.ps1` 只以 `--no-deps` 啟動 Kafka、既有 Inventory PostgreSQL、新的採購與供應商 PostgreSQL，以及本實驗的 API、Consumer、mock 和 Microcks；不啟動其他觀測系統。它等待三個資料庫就緒後，重複套用 `docker-compose/sql-script/migrations/inventory/20260926_0003_add_inventory_goods_receipts.sql` 與 `docker-compose/sql-script/procurement/001-procurement.sql`。新的供應商服務在啟動時套用自己的 `docker-compose/sql-script/supplier/init.sql`。PostgreSQL 的 `docker-entrypoint-initdb.d` 只在新 volume 初始化時執行，因此既有資料庫仍需這一步。腳本也等待服務的 HTTP 健康端點及 Microcks `/api/services`；若商品已在 Inventory 初始化，可傳 `-InventoryProductId $productId` 額外確認其查詢端點回 HTTP 200。腳本不刪除容器、volume 或資料；容器映像已建好時可加 `-NoBuild`。

若要單獨重套 Inventory migration，可把檔案經 stdin 送進本專案的既有資料庫：

```powershell
Get-Content docker-compose/sql-script/migrations/inventory/20260926_0003_add_inventory_goods_receipts.sql -Raw |
  docker compose @compose exec -T postgres-inventory psql -U user -d inventory_db -v ON_ERROR_STOP=1
```

只在此整合專案操作；不要以 `down -v` 清除既有或新增的資料 volume。遇到啟動失敗，先用 `docker compose @compose ps` 與 `docker compose @compose logs --tail 100 <service>` 查看具體服務。

## 入口與連線 profile

| 用途 | 本機入口 | 容器內入口 |
| --- | --- | --- |
| Procurement API 與 `/health` | `http://127.0.0.1:8180/` | `http://procurement-api:8080/` |
| Supplier sandbox、原生檢視頁 | `http://127.0.0.1:8181/` | `http://supplier-sandbox:8080/` |
| WireMock.Net 實驗控制頁 | `http://127.0.0.1:8182/` | `http://supplier-mock:8080/` |
| WireMock.Net 供應商原生端點 | `http://127.0.0.1:8183/` | `http://supplier-mock:9091/` |
| Microcks 原生 UI | `http://127.0.0.1:8184/` | `http://microcks:8080/` |
| Inventory API | `http://127.0.0.1:8185/` | `http://inventory-api:8080/` |

新增的公開 port 全部綁定 `127.0.0.1`。採購設定 `SupplierProfiles__direct` 指向 sandbox、`SupplierProfiles__wiremock` 指向 WireMock 原生 9091、`SupplierProfiles__microcks` 指向 Microcks 的供應商 API URL。Procurement 與 Inventory Consumer 使用 Kafka `kafka:9092`，各自使用自己的 PostgreSQL；Inventory Consumer 的 Wolverine inbox schema 是 `inventory_consumer_messages`，與 Inventory API 分離。

三種供應商 profile 是固定路由，不接受任意上游 URL。`REAL-001` 是 sandbox 真實報價 SKU，單價 TWD 100；`MOCK-001` 用於 mock 範例；`DENY-001` 用於拒絕情境。請以 API 回傳的報價內容建立採購單。供應商訂單提交使用相同 `clientRequestId` 重試；不同 payload 應收到衝突。逾時而結果未知時先用採購單 reconcile 端點查詢原供應商，不要產生新的 clientRequestId 重下單。

## 建立採購單與分批收貨

先準備一個 **Products 中已存在** 的 `ProductId`，再為它初始化 Inventory stock 20。若該商品已有庫存，選另一個測試商品，避免重複初始化；本腳本會在送單前確認庫存是 20。示例：

```powershell
$productId = [Guid]'填入既有 ProductId'
./scripts/procurement-lab/Test-Flow.ps1 -ProductId $productId -SeedInventory `
  -OutputPath 'F:\git-worktree\procurement-lab-evidence\direct-flow.json'
```

已初始化的商品省略 `-SeedInventory`。腳本向 sandbox 查 `REAL-001` 報價，送出數量 10 的 direct 採購單，檢查 `Accepted` 時庫存仍是 20；接著以兩個不同 ReceiptId 收 6、4 件，等待 Kafka/Inventory 處理後依序觀察 26、30。它以第一個 ReceiptId 再送一次，要求 HTTP 200 與 `created=false`，且庫存維持 26；最後確認採購單 `Received`、`receivedQuantity=10`。輸出只含測試識別及觀察結果；腳本未執行前，這些都不是驗證結論。

API 路徑是 `/api/procurement/suppliers/{provider}/catalog/{sku}`、`/api/procurement/purchase-orders`、`/api/procurement/purchase-orders/{id}`、`/api/procurement/purchase-orders/{id}/reconcile` 與 `/api/procurement/purchase-orders/{id}/receipts`。收貨內容 `{receiptId,quantity}`；同 ID 同內容重播回既有結果，變更內容須回衝突。新的採購單與 Supplier sandbox 訂單可分別由兩邊 UI/查詢端點讀回。Inventory 沒有採購總量，超收檢查由 Procurement 採購單負責。

## WireMock.Net 與 Microcks

WireMock 控制頁由本 repository 的 `SupplierMock.WebApi` 提供，不是 WireMock.Net 原生 dashboard。預設 `hybrid`，也可選 `mock` 或 `proxy`；UI 顯示目前模式、固定上游、mapping 與近期 request log。`mock` 應回本機範例且 sandbox request log 不增加；`proxy` 應回 `origin=sandbox` 且 sandbox 記錄上游 request；`hybrid` 對 `MOCK-001` 使用範例、對 `REAL-001` 透傳。固定 `MOCK-001` 訂單範例使用 `clientRequestId=9d4c99da-6517-46b2-baa7-7e81106d3d34`、數量 2、TWD 100；其他 identity 不會冒用此範例。可用下列控制 API 比對實際狀態及重設模式：

```powershell
Invoke-RestMethod http://127.0.0.1:8182/control/state
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8182/control/mode `
  -ContentType application/json -Body '{"mode":"proxy"}'
Invoke-RestMethod http://127.0.0.1:8182/control/mappings
Invoke-RestMethod http://127.0.0.1:8182/control/requests
Invoke-RestMethod -Method Post http://127.0.0.1:8182/control/reset
```

`DELETE /control/requests` 會清除 WireMock 原生 request journal；先保存需要的證據。sandbox `GET /sandbox/requests` 提供最近最多 100 筆安全 request 觀察，`GET /sandbox/orders` 可查供應商單；`GET /sandbox/control` 可讀延遲，`PUT /sandbox/control` 的 `{ "delayAfterCommitMs": 0..10000 }` 可重現提交後逾時。模式與延遲控制是執行時狀態；重啟後由設定檔與環境變數重套起始模式。記錄測試前後的 request ID、origin 與 sandbox request 數，而非只看 HTTP 200。

Microcks 使用自己的 UI。從 `samples/SupplierMock/microcks/` 擇一匯入 `supplier-mock.yaml`、`supplier-proxy.yaml` 或 `supplier-hybrid.yaml`，在 Quick Import 確認 `Supplier API` 版本 `1.0.0`，並讀回 UI 顯示的 mock URL。也可用 PowerShell 7 的匯入腳本；它將所選檔案送到 Microcks 的 artifact upload API，再由 `/api/services` 讀回服務名稱與版本。若 Microcks 啟用驗證，提供具 manager 權限的 bearer token：

```powershell
./scripts/procurement-lab/Set-MicrocksMode.ps1 -Mode hybrid
# 啟用驗證的環境：-BearerToken $managerToken
```

匯入腳本和 HTTP 契約腳本都用固定上傳檔名 `supplier-api.yaml`，讓不同模式覆蓋同一份 Microcks source artifact；手動 Quick Import 時先把所選 YAML 複製成該檔名再上傳，避免以三個來源檔名累積範例。匯入成功與服務身分讀回只證明規格已登錄，切換後仍須以不同 request ID 確認 dispatch 與來源。此版本預期前綴是 `/rest/Supplier+API/1.0.0/`；若 UI 顯示不同路徑，修改 `docker-compose.procurement.yml` 的 `SupplierProfiles__microcks` 再重建 `procurement-api`。每次切換匯入檔後檢查 dispatcher/proxy 設定實際生效；`PROXY_FALLBACK` 只適用已知 operation 的 response matching，不能當作所有未知路徑的轉發。mock/proxy/hybrid 各以唯一 request ID 比對 Microcks response origin 和 sandbox request log，留下原生 UI/請求證據。

## 可重現驗證與故障恢復

隔離的 PostgreSQL 測試使用 `RUN_EXTERNAL_INTEGRATION_TESTS=true` 加上 `INVENTORY_TEST_POSTGRES_CONNECTION_STRING`、`PROCUREMENT_TEST_POSTGRES_CONNECTION_STRING`、`SUPPLIER_TEST_POSTGRES_CONNECTION_STRING`。Compose 的 verification 與 procurement overlay 已為 `regression-tests` 設定容器內連線，避免公開資料庫 port；測試結果輸出到 `artifacts/procurement-lab/test-results/`。需要時可在服務就緒後執行：

```powershell
docker compose @compose run --rm --no-deps regression-tests
```

若要留下採購與兩套原生 mock/proxy 的 HTTP 契約證據，可在這些服務就緒後執行以下標準函式庫腳本。它使用固定本機 port、隨機測試識別與文件化的 `MOCK-001` fixture，並逐情境記錄狀態碼、回應、供應商 request journal 前後值及 cleanup 結果。它會切換 WireMock/Microcks 模式、設定並重設 sandbox 延遲；不操作 Docker 或清除資料。失敗時傳回非零狀態，JSON 仍保存已觀察的結果。首次實際執行前，檢查現場服務是否與本文件設定一致。

```powershell
python ./scripts/procurement-lab/test_contracts.py `
  --output 'artifacts/procurement-lab/http-contracts.json'
```

腳本的 `P02/P03/P04/P07`、`S01` 與每套引擎的 `M01`–`M06` 結果只代表當次實際 HTTP 觀察；Receipt/Kafka 停機恢復、PostgreSQL 查驗與原生 UI 仍須另外驗收。`M06` 記錄 mock-only 未命中與未知路徑的實際狀態/內容，僅要求 sandbox request journal 不增加。

當 Kafka 停止時，新增收貨應保留 Procurement source outbox 記錄；重新啟動 Kafka 後，同一 ReceiptId 最終只增加一次庫存。只停止本專案的 Kafka 服務並記錄停機前後 stock、兩邊 outbox/receipt 表與事件 ID：

```powershell
docker compose @compose stop kafka
# 登錄一筆新的實際收貨並記下 ReceiptId；此時檢查採購庫存仍未增加。
docker compose @compose up -d --no-deps kafka
# 等待庫存增加一次，再重送相同收貨識別並讀回原結果。
```

可用下列 R08 腳本重現此情境，`ProductId` 必須先在 Inventory 初始化且可讀到目前庫存；腳本不清零或重設現有庫存。它先核對 Kafka 容器的 Compose project/service label 與容器 ID，僅停止本專案的 `kafka`，在 `finally` 中啟動同一容器並記錄復原結果。收貨時檢查 Procurement receipt、來源 outbox，以及已交接到 Wolverine 時的 `procurement_wolverine.wolverine_outgoing_envelopes`；`published_at` 只表示持久化交接，不表示 Kafka 已消費。Kafka 恢復後最多等待 120 秒確認庫存增加 3 並重播同一收貨識別，JSON 保留成功或失敗的實際觀察。

```powershell
python ./scripts/procurement-lab/test_broker_recovery.py --product-id $productId `
  --output 'artifacts/procurement-lab/broker-recovery.json'
```

若收貨先於 Inventory 商品初始化，Consumer 應把失敗保留於有限重試／錯誤佇列；初始化 stock 後以同一 ReceiptId 重新投遞才可入庫一次。不能把跳過的 external tests、Compose 語法檢查或一個 mock response 說成實際 PostgreSQL/Kafka 接受證據。驗收需分別保存 HTTP 回應、供應商 origin/request、PostgreSQL receipt/outbox/stock、Kafka 事件與 consumer log；workflow 的最終狀態由 coordinator review 決定。
