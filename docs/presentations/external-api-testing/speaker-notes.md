# 外部 API 測試實驗：講者與示範筆記

對應 17 張投影片，總長約 20 分鐘。投影片中的示範值是操作手冊所列情境；現場結果須以當次服務、資料與 request log 讀回為準。請在開場前取得一個 Products 中已存在且可供 Inventory 初始化的 ProductId。現場使用既有整合專案與資料卷，不要清除 volume。

| 頁 | 時間 | 講述重點 |
| --- | ---: | --- |
| 1 | 0.5 分 | 說明本次只涵蓋既有 localhost 採購與供應商實驗。 |
| 2 | 0.5 分 | 預告入口、模式、逾時協調與真正入庫四個問題。 |
| 3 | 1 分 | 分清測試引擎與 Procurement 的 `ISupplierGateway`。前者處理 HTTP 範例與代理，後者核對供應商回應並保護採購身分。 |
| 4 | 1 分 | 沿瀏覽器、YARP、Procurement API 與管理控制 API 讀圖。前端 Vue 在瀏覽器呼叫同源 API；Nginx 提供前端檔案。這張只呈現供應商實驗路徑，不代替 Orders 與 Inventory 的其他整合路徑。 |
| 5 | 1 分 | `/web/` 是內部業務與倉管作業台，`/admin/` 是商品主檔與整合工具。Microcks 保有自己的原生 UI。說明目前只有 localhost 入口，未新增登入。 |
| 6 | 1 分 | WireMock.Net 由專用 .NET host 執行。控制頁是 repository 自建，底下使用原生 mapping、proxy 與 Admin API。hybrid 的窄範例 priority 1 優先於 priority 10 透傳；POST 需符合完整頂層身分才命中固定範例。 |
| 7 | 1 分 | Microcks 以匯入的 OpenAPI operation 與 dispatcher 工作。`PROXY_FALLBACK` 是已知 operation 的 response matching 回退，不能推論未知路徑都會轉送。 |
| 8 | 1 分 | 此頁用 GET 報價的 origin、SKU 與 Sandbox request log 對照三種模式。GET 報價不帶 clientRequestId；隔離操作和查前後 request 數可辨來源。HTTP 200 單獨不足以證明 proxy。 |
| 9 | 1 分 | 固定 POST 範例要比對頂層完整身分；`100` 與 `100.00` 等值，變更 payload 不可冒用固定範例。 |
| 10 | 1 分 | 沿箭頭讀一次供應商請求：操作者選 provider，Procurement 呼叫 mock 引擎，需透傳時再到 Sandbox；回應沿反方向返回。request journal 另從控制 API 讀取，不能當作業務回應的一部分。Microcks hybrid 的回退限已匯入 operation。 |
| 11 | 1.5 分 | 提交後逾時會保留未知結果。用原 `clientRequestId` 查原 provider，再決定是否用同 key 明確重試。不要讓傳輸逾時把已接受訂單降級。 |
| 12 | 1.5 分 | 接受採購單不入庫。登錄 ReceiptId 後，Procurement 收貨與 source outbox 持久化；relay 交 Kafka，Inventory 以 ReceiptId 去重並更新庫存。`published_at` 若出現在證據中，只代表持久化交接到 Wolverine，不等於 Kafka 已消費。 |
| 13 | 2 分 | 現場示範一：進 `/admin/` 整合工具；記下 WireMock request journal 與 Sandbox request 數。切到 mock 查 MOCK-001，再切 proxy 查 REAL-001，最後切 hybrid 各查一次。每次確認 effective mode、origin 與 Sandbox 請求變化。 |
| 14 | 2 分 | 現場示範二：以 Sandbox `delayAfterCommitMs` 重現提交後逾時。採購單可能為 `SubmissionUnknown`；讀 Sandbox 單，再執行採購單 `reconcile`。示範後把延遲重設為 0。若現場沒有可用 ProductId，改用操作手冊與既有實際證據解說，不宣稱當次驗收通過。 |
| 15 | 2 分 | 現場示範三：先核對可用商品與起始 stock。操作手冊的情境是 20 起始、分批收 6 與 4，依序觀察 26 與 30；重播第一筆 ReceiptId 不再增加。實際數值須按現場狀態調整，避免重複初始化既有商品。 |
| 16 | 1 分 | mock-only 適合固定契約的可重現檢查；proxy/hybrid 要另留來源證據。外部整合測試是 opt-in，跳過並非通過。 |
| 17 | 1 分 | 以模式、來源、身分、庫存四個讀回點收束，保留提問時間。 |

## 現場準備與替代路徑

1. 從持久 repository 路徑執行 `./scripts/frontend-lab/Start-Lab.ps1`，依操作手冊核對 `http://127.0.0.1:8888/web/`、`/admin/` 與 Microcks `http://127.0.0.1:8184/`。F: RAM disk worktree 不宜作需要 bind mount 的執行期部署來源。
2. 透過 YARP，WireMock 讀回路徑為 `/api/admin/supplier-mock/control/state`、`/api/admin/supplier-mock/control/mappings`、`/api/admin/supplier-mock/control/requests`。Microcks 控制狀態使用 `/api/admin/supplier-mock/control/microcks/state`；詳細 operation 與 dispatcher 可進原生 UI。
3. 透過 YARP，Sandbox 用 `/api/admin/supplier-sandbox/sandbox/requests` 查最近請求，用 `/api/admin/supplier-sandbox/sandbox/control` 讀寫提交後延遲。延遲與模式都是執行時狀態，重啟可能重套初始 preset。
4. API 合約批次檢查參考 `python ./scripts/procurement-lab/test_contracts.py --output artifacts/procurement-lab/http-contracts.json`。真正入庫示範參考 `./scripts/procurement-lab/Test-Flow.ps1 -ProductId $productId -SeedInventory`；僅新商品可使用 `-SeedInventory`。
5. 若現場服務不可用，展示已保存且標註日期的證據或本簡報的流程圖。不要把歷史驗收說成當次測試結果。

## 來源

- [採購、供應商與實際收貨實驗](../../../.dev/operations/procurement-supplier-lab.md)
- [商務作業前台與管理後台實驗](../../../.dev/operations/commerce-frontend.md)
- [採購架構](../../../.dev/workflows/2026-09-26-procurement-supplier-lab/architecture.md)
- [採購規格](../../../.dev/workflows/2026-09-26-procurement-supplier-lab/specifications.md)
- [WireMock.Net proxying](https://wiremock.org/dotnet/proxying/)
- [WireMock.Net Admin API](https://wiremock.org/dotnet/admin-api-reference/)
- [Microcks dispatching](https://microcks.io/documentation/explanations/dispatching/)
- [Microcks proxy feature explanation](https://microcks.io/blog/new-proxy-features-1.9.1/)
