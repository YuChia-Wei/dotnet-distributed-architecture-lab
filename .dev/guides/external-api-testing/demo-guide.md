# 團隊展示指南

這是本機環境的可觀察展示腳本，不是驗收已通過的聲明。先確認現在的服務、商品與庫存，再操作會寫入採購、供應商或庫存的步驟。所有模式切換、sandbox 延遲與 WireMock request journal 都是共享執行期狀態；在共用實驗環境與同事約定展示時段，保留要比較的紀錄後才切換。不要為展示執行 `down -v`、清 volume 或重置既有商品／訂單。

## 0. 準備與入口

從**持久的 repository 路徑**執行，使用 PowerShell 7 和既有 Compose project。先看 [前台手冊](../../operations/commerce-frontend.md) 與 [採購手冊](../../operations/procurement-supplier-lab.md) 的初始化條件。前台啟動腳本會調用採購 bootstrap 並只啟動所需服務；它不清資料。先跑 Compose 合成檢查再讀回服務，而不是把命令本身當成成功證據。

```powershell
./scripts/frontend-lab/Start-Lab.ps1
$compose = @(
  '-p', 'mqarchlab-pr5-integration',
  '--profile', 'procurement-lab', '--profile', 'verification', '--profile', 'frontend-lab',
  '-f', 'docker-compose/docker-compose.yml',
  '-f', 'docker-compose/docker-compose.override.yml',
  '-f', 'docker-compose/docker-compose.verification.yml',
  '-f', 'docker-compose/docker-compose.procurement.yml',
  '-f', 'docker-compose/docker-compose.frontend.yml'
)
docker compose @compose config --quiet
docker compose @compose ps
```

打開 `http://127.0.0.1:8888/web/` 的「採購與收貨」與 `http://127.0.0.1:8888/admin/` 的「整合工具」。若用直接端點排錯：Procurement 8180、Sandbox 8181、SupplierMock 自製控制頁 8182、WireMock 原生端點 8183、Microcks 原生 UI 8184、Inventory 8185；都綁 `127.0.0.1`。管理後台沒有一般授權保護，僅適合 localhost。若服務未就緒，先查 `docker compose @compose ps` 與 `docker compose @compose logs --tail 100 <service>`；不要用刪除 volume 處理啟動問題。

## 1. 先用報價展示兩種 hybrid

在管理後台「整合工具」分別選 WireMock.Net 與 Microcks 的 `hybrid`。WireMock 切換會清除 mapping 與 request journal 後重建；先保存既有紀錄。Microcks 首次可能是 `unconfigured`，按「套用混合模式」會匯入固定契約。等待控制頁再次顯示 WireMock `ready/hybrid`，以及 Microcks 原生操作完整讀回 `ready/hybrid`；`custom`、`failed`、`unavailable` 都不能說已套用。Microcks 原生 UI 另在 8184，可核對 `Supplier API` 1.0.0 的三個 operation。

在「採購與收貨」把供應商路徑選 `wiremock`、SKU 設 `MOCK-001`，按「查詢報價」：預期 `origin=wiremock`，sandbox「近期請求」不增加。接著查 `REAL-001`：預期 `origin=sandbox`，sandbox 增加相應 GET。改選 `microcks`，重複兩次：固定範例應顯示 `origin=microcks`，`REAL-001` 應由已知 catalog operation 的 fallback 到 sandbox。每次至少記下請求時間、provider、SKU、回應 `origin`、sandbox journal 前後筆數；共用環境有其他流量時需用唯一識別或原始紀錄比對，單靠筆數不足以歸因。

可從同源 API 再讀回控制設定：

```powershell
Invoke-RestMethod http://127.0.0.1:8888/api/admin/supplier-mock/control/state
Invoke-RestMethod http://127.0.0.1:8888/api/admin/supplier-mock/control/mappings
Invoke-RestMethod http://127.0.0.1:8888/api/admin/supplier-mock/control/microcks/state
Invoke-RestMethod http://127.0.0.1:8888/api/admin/supplier-sandbox/sandbox/requests
```

要展示純 mock，分別切到 `mock`，重查 `MOCK-001`，確認範例回應與 sandbox journal 不變。要展示純 proxy，切到 `proxy`，查 `REAL-001`，確認 sandbox 收到請求。Microcks 的 proxy／hybrid 只涵蓋匯入的三個已知 operation；不要用未知路徑推論與 WireMock 相同的 catch-all 行為。切換後一定讀回；按鈕完成只是控制面的回應。

## 2. 建立採購、處理未知結果、實際收貨

選一個 Products 已存在、Inventory 已初始化且適合測試的 `ProductId`，先讀目前 stock 並記錄。前台「採購與收貨」選 `direct`、`REAL-001`，先查報價，再用回傳的 TWD 單價與欲採購數量建立採購單。前台會顯示本次 `clientRequestId`；送出後保留採購單 ID。供應商 `Accepted` 時再次讀 Inventory stock，應仍是原值；採購單的 `receivedQuantity` 仍是 0。這個動作會在 Procurement 與 Supplier Sandbox 建立持久資料，請使用測試商品和新識別，不要重用他人的身分。

逾時演示先在管理後台的 Supplier Sandbox 將「提交後延遲」設為 3000 毫秒並讀回，再以一筆**新的** `direct` 採購示範。目前 Procurement 的 `SupplierHttp:TimeoutSeconds` 預設為 2；若現場設定已覆寫，先讀設定並選擇比期限長、且在 0–10000 毫秒範圍內的延遲。若此次沒有逾時，記錄實際 `Accepted`，不要把它寫成未知結果。若前台得到 `SubmissionUnknown` 或傳輸結果不明，保留畫面中的原 `clientRequestId` 與採購單 ID，開採購單明細按「協調供應商結果」。協調會用原 provider／key 查單；不要建立新草稿或新 key 重下單。讀回採購狀態與 sandbox 訂單，演示後把延遲設回 0 並再次讀回。若供應商查無單或仍無法連線，狀態可能仍未知，不強行宣稱失敗。

只對已接受、確實到貨的採購在「採購單明細」登錄實際收貨。先記下 stock，輸入不超過未收數量的正整數，保留 `ReceiptId`，等待採購單出現 receipt，再觀察 Inventory stock 增加一次。若前台報結果未知，先按「讀回收貨紀錄」；如未見紀錄，僅以**同一 ReceiptId 和數量**重送。新 ID 代表另一筆收貨，不能用於確認原請求。Procurement 的收貨回應與 Inventory 入庫之間有 Kafka 非同步延遲；前者成功不等於後者已完成。要做 Kafka 停機恢復、DB/outbox 核對與實際長時間等待，使用採購手冊的專門步驟與證據，勿在一般短展示中任意停共享 broker。

## 3. 銷售保留是另一條路

在 `/web/` 從商品頁建立一筆銷售訂單。Orders 先向 Inventory 保留可用量，成功才提交訂單；不足則回失敗。記錄商品 ID、保留前後可用量、訂單 ID 或失敗回應。這條路不經 `ISupplierGateway`，也不會替採購單登錄收貨。不要以銷售訂單建立成功推論供應商測試引擎正確。

## 4. 可重現證據與收尾

需要機器可讀的 HTTP 契約結果時，可在服務就緒後執行現有 `scripts/procurement-lab/test_contracts.py`，輸出到 `artifacts/procurement-lab/http-contracts.json`；腳本會改變兩套模式與 sandbox 延遲，先確認沒有同事正在使用同一實驗室。`test_supplemental_contracts.py` 還需要已初始化的 `ProductId`，且會建立額外供應商／採購資料。兩者保留每次 HTTP 觀察，不能替代這次瀏覽器畫面或 PostgreSQL/Kafka 驗收。若只演示 UI，保存模式讀回、兩套引擎原生規則／operation、回應及 sandbox request journal 即可。

結束前把 sandbox 延遲設回 0、兩套引擎設回約定模式並**讀回**。WireMock 重設或切換會清除 request journal，所以先匯出需要的紀錄。Microcks 的契約匯入與模式不應跨重啟假定仍存在。歷史腳本或 workflow 的通過記錄只能說明當時環境；本次結果須依本次的時間、識別與讀回報告。
