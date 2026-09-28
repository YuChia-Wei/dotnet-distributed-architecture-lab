# WireMock.Net 與 Microcks：本實驗室如何選用

兩套工具都扮演 Procurement 的外部供應商 HTTP 端點。選擇的是某次測試需要的控制範圍，並非替換採購業務埠。`ISupplierGateway` 仍由 Procurement 定義，`HttpSupplierGateway` 依已命名的 `direct`、`wiremock`、`microcks` profile 呼叫供應商；供應商替身只位於該埠的外側。三條 profile 的位址由 Compose 設定，前台不接受臨時任意 URL。

| 判準 | WireMock.Net（此專案） | Microcks（此專案） |
| --- | --- | --- |
| 管理介面 | `SupplierMock.WebApi` 自製繁中控制頁和 `/control/*`；內嵌 WireMock.Net 的原生管理 API 位於 9091，控制頁不是原廠 dashboard | 原生 Microcks UI 與 `/api/services`；自製管理後台經 `MicrocksPresetController` 套用固定契約並讀回原生 operation |
| 契約來源 | 程式將 `presets/*.json` 解讀為三組固定原生 mapping；不是通用 mapping 編輯器 | `supplier-{mock,proxy,hybrid}.yaml` OpenAPI 契約以固定來源檔名 `supplier-api.yaml` 匯入，辨識 `Supplier API` `1.0.0` 的三個 operation |
| 此處 mock 命中 | GET `MOCK-001` 報價、GET 固定 clientRequestId 查單；POST 須完整符合固定 key、SKU、數量、單價、幣別的 JMESPath 條件 | OpenAPI 範例：catalog/query 用 URI 部分，POST 用 JS dispatcher 對固定本文做欄位比對 |
| 此處 hybrid 未命中 | 優先序 1 範例；優先序 10 的 `/*` 代理 mapping 送往固定 Supplier Sandbox，涵蓋較廣路徑 | `PROXY_FALLBACK` 只在已匯入、已辨識的三個 operation 內，比對不到範例時送往固定 Supplier Sandbox；未知路徑不能宣稱全域轉送 |
| 純 proxy | 不安裝固定範例，`/*` 代理 mapping 接手 | 三個已知 operation 使用 `PROXY` dispatcher；仍受契約 operation 範圍限制 |
| 儲存與重啟 | mapping 與 request journal 是執行期狀態；切換時重建 mapping 並清空 journal；重啟套用 Compose 的 `hybrid` | Compose 使用 `microcks-uber:1.15.0`，未配置資料 volume；重啟後須讀回、必要時重匯入，不能依賴先前匯入 |
| 適合演示 | 要明確展示精準 stub 優先、其餘流量透傳，以及原生 request journal | 要展示由 API 契約、operation dispatcher、範例與原生 UI 管理服務 |

原廠能力大於本專案控制頁。WireMock.Net 的原生 request matching 可組合路徑、query、header 與 body 條件，也支援以較低優先序的 proxy mapping 接住未命中 stub 的請求；本專案控制頁只提供三種預設、固定上游及讀取／清除紀錄。Microcks 的 dispatcher 能依 operation 使用路徑參數、header、query 或腳本等規則選例，另有已知 operation 的代理選項；本專案三份 YAML 只實作表中的 URI 與 POST body 條件，管理後台不提供任意 rule 編輯。需要驗證其他欄位時，先把新情境與契約變更列為開發工作，不能從原廠功能推定目前 UI 已可設定。

建議先決定要觀察哪一種失敗：

1. 只驗證採購端對固定供應商回應的處理，選 `mock`。以 `MOCK-001` 的固定本文命中範例，同時確認 sandbox request 數沒有增加。若建立訂單，固定 `clientRequestId` 為 `9d4c99da-6517-46b2-baa7-7e81106d3d34`；普通新採購單不會自動匹配該範例。
2. 要看真實供應商 sandbox 的持久身分、逾時與衝突，選 `direct` 或對應引擎的 `proxy`。`direct` 不經測試引擎；`proxy` 能保留引擎觀察點。sandbox `REAL-001` 是真實報價商品。
3. 要展示同一端點有範例與上游兩條路，選 `hybrid`，先查 `MOCK-001`，再用不同識別查 `REAL-001`。Microcks 的 fallback 僅是既知 operation 的 response matching fallback；上游回錯、服務不存在、未知 operation 都不是同一種「未命中」。

**避免測試流量誤入上游：** 確定性 CI 若只需要替身回應，固定使用 mock-only 契約／模式，並用 sandbox request journal 前後值證明未轉送。`hybrid` 與 `proxy` 的設計目的就是轉送固定上游，不適合作為完全隔離的預設。讀到 mock 的 `origin`、WireMock mapping 或 Microcks `ready`，各自只證明一部分狀態；要證明路由仍須比對同一次唯一請求識別、回應 `origin` 與 sandbox journal。見 [展示指南](demo-guide.md)。

版本以本 repository 鎖定值為準：`WireMock.Net` 2.15.0、`microcks-uber` 1.15.0、PostgreSQL 16.15-alpine。本文不把原廠網站的最新功能視為這些已鎖定映像的已驗證能力。比較依據與官方連結見 [來源](sources.md)。
