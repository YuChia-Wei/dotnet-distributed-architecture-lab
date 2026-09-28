# 來源與可驗證範圍

本指南以目前 repository 的追蹤檔案決定「此實驗室實作了什麼」，用原廠文件說明引擎可用的概念。原廠文件可能描述較新版本或更廣功能；功能進入本實驗室仍須看鎖定版本、設定、契約與當次 HTTP 讀回。

| 指南中的結論 | 本專案主要依據 |
| --- | --- |
| YARP 的 `/web`、`/admin`、四組業務 API 及管理前綴；Nginx 的 SPA 邊界 | [`docker-compose.frontend.yml`](../../../docker-compose/docker-compose.frontend.yml)、[`RoutesSetting.json`](../../../docker-compose/config/frontend-lab/RoutesSetting.json)、[`ClustersSetting.json`](../../../docker-compose/config/frontend-lab/ClustersSetting.json)、[`Web nginx.conf`](../../../src/Frontend/Web/nginx.conf)、[`Admin nginx.conf`](../../../src/Frontend/Admin/nginx.conf) |
| 本機 port、五份 Compose 合成順序、各 DB、Kafka、固定 provider URL、Microcks 無持久 volume | [`docker-compose.yml`](../../../docker-compose/docker-compose.yml)、[`docker-compose.procurement.yml`](../../../docker-compose/docker-compose.procurement.yml)、[`docker-compose.frontend.yml`](../../../docker-compose/docker-compose.frontend.yml)、[採購手冊](../../operations/procurement-supplier-lab.md)、[前台手冊](../../operations/commerce-frontend.md) |
| `ISupplierGateway` 屬於 Procurement；provider 限三條命名路由；送單、協調、收貨端點 | [`ProcurementOperations.cs`](../../../src/Procurement/DomainCore/Procurement.Applications/ProcurementOperations.cs)、[`HttpSupplierGateway.cs`](../../../src/Procurement/DomainCore/Procurement.Infrastructure/HttpSupplierGateway.cs)、[`ProcurementController.cs`](../../../src/Procurement/Presentation/Procurement.WebApi/ProcurementController.cs) |
| WireMock 控制頁與原生伺服器分離，固定預設、優先序、本文匹配、切換清紀錄 | [`SupplierMock Program.cs`](../../../samples/SupplierMock/SupplierMock.WebApi/Program.cs)、[`SupplierMock.WebApi.csproj`](../../../samples/SupplierMock/SupplierMock.WebApi/SupplierMock.WebApi.csproj)、[`presets`](../../../samples/SupplierMock/presets/hybrid.json) |
| Microcks 三份固定 OpenAPI、已知 operation、`PROXY_FALLBACK` 與原生讀回 | [`supplier-hybrid.yaml`](../../../samples/SupplierMock/microcks/supplier-hybrid.yaml)、[`supplier-proxy.yaml`](../../../samples/SupplierMock/microcks/supplier-proxy.yaml)、[`supplier-mock.yaml`](../../../samples/SupplierMock/microcks/supplier-mock.yaml)、[`MicrocksPresetController.cs`](../../../samples/SupplierMock/SupplierMock.WebApi/MicrocksPresetController.cs) |
| 供應商提交後延遲、持久訂單與安全觀察端點 | [`SupplierSandbox Program.cs`](../../../samples/SupplierSandbox/SupplierSandbox.WebApi/Program.cs)、[`supplier/init.sql`](../../../docker-compose/sql-script/supplier/init.sql) |
| 採購 receipt/source outbox、relay 交接，Inventory receipt/stock/outbox 一次性提交 | [`PostgresPurchaseStore.cs`](../../../src/Procurement/DomainCore/Procurement.Infrastructure/PostgresPurchaseStore.cs)、[`ProcurementOutboxRelay.cs`](../../../src/Procurement/DomainCore/Procurement.Infrastructure/ProcurementOutboxRelay.cs)、[`GoodsReceivedHandler.cs`](../../../src/Inventory/Presentation/InventoryControl.Consumer/Messaging/GoodsReceivedHandler.cs)、[`PostgresInventoryGoodsReceiptStore.cs`](../../../src/Inventory/DomainCore/InventoryControl.Infrastructure/Applications/Repositories/PostgresInventoryGoodsReceiptStore.cs) |
| 管理後台讀回與前台採購／收貨操作；銷售以 Wolverine/Kafka 請求／回覆向 Inventory 保留 | [`IntegrationsPage.vue`](../../../src/Frontend/Admin/src/pages/IntegrationsPage.vue)、[`Procurement.vue`](../../../src/Frontend/Web/src/pages/Procurement.vue)、[`PurchaseDetail.vue`](../../../src/Frontend/Web/src/pages/PurchaseDetail.vue)、[`PlaceOrderCommand.cs`](../../../src/Order/DomainCore/SaleOrders.Applications/Commands/PlaceOrderCommand.cs)、[`Orders Program.cs`](../../../src/Order/Presentation/SaleOrders.WebApi/Program.cs)、[`Inventory Program.cs`](../../../src/Inventory/Presentation/InventoryControl.WebApi/Program.cs) |

原廠概念依據（2026-09-28 查閱）：

- [WireMock.Net Request Matching](https://wiremock.org/dotnet/request-matching/)：路徑、URL、HTTP method、query、header、cookie、body 都屬原生匹配範圍；本專案的固定預設只用到其中部分欄位。
- [WireMock.Net Proxying](https://wiremock.org/dotnet/proxying/)：原生 proxy mapping 可與較高優先序 stub 共存；本專案使用優先序 1／10 的具體 mapping，不是任意上游轉發 UI。
- [WireMock.Net Admin API Reference](https://wiremock.org/dotnet/admin-api-reference/)：管理 API 與 request log 等端點的原生能力；本專案自製控制頁包裝一小部分。
- [Microcks Dispatcher & Dispatching Rules](https://microcks.io/documentation/explanations/dispatching/)：`URI_PARTS`、query／header／body 派送策略及 `PROXY`、`PROXY_FALLBACK` 的規則。代理行為設定在 operation 上。
- [Microcks Proxy Features 1.9.1](https://microcks.io/blog/new-proxy-features-1.9.1/)：代理與 fallback 為每個 operation 設定，未命中範例才轉發。
- [Microcks Deployment Options](https://microcks.io/documentation/explanations/deployment-options/)：uber 發行形態使用內嵌記憶體資料庫；本專案 Compose 沒有為 `microcks` 掛資料 volume，因此重啟須讀回並視情況重匯入。

證據界線：靜態程式、設定與 Mermaid 圖能證明設計和預期路由；Compose 合成只能證明設定可解析；控制面 `ready` 只證明引擎原生設定讀回；HTTP 回應加 sandbox journal 才能說明當次是否代理；Procurement／Inventory PostgreSQL、Kafka 與 Consumer 的當次紀錄才可證明完整收貨。歷史 workflow 與測試輸出不可替代本次環境的驗收。
