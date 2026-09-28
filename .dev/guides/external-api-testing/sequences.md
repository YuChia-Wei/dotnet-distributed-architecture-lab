# 供應商替身與商務流程時序

以下是依目前程式和設定整理的**預期資料流**，不是一次實際執行的錄影或驗收紀錄。先選定 provider 和引擎模式，再用回應 `origin`、引擎紀錄及 sandbox request journal 交叉比對。圖中省略無關的 HTTP 包裝與 UI 輪詢。各圖的路徑和可觀察欄位見 [展示指南](demo-guide.md)。

## 1. 僅模擬：固定範例沒有進上游

`wiremock` 和 `microcks` 是互斥的 provider 選項；圖中 `Mock engine` 代表所選的一套。WireMock mock 模式只裝固定範例 mapping；Microcks mock 契約僅為三個已知 operation 提供範例。`MOCK-001` 報價可直接示範；若示範 POST，必須使用固定完整本文，不能把任意新單當作範例命中。

```mermaid
sequenceDiagram
  actor User as 操作員
  participant P as Procurement API
  participant G as ISupplierGateway / HTTP adapter
  participant M as 所選 mock 引擎
  participant S as Supplier Sandbox
  User->>P: GET /api/procurement/suppliers/{provider}/catalog/MOCK-001
  P->>G: QuoteAsync(provider, MOCK-001)
  G->>M: GET /supplier/catalog/MOCK-001
  M-->>G: 範例報價，origin=wiremock 或 microcks
  G-->>P: 已驗證的報價
  P-->>User: 200 與 origin
  Note over S: 本情境不應新增 sandbox request
```

## 2. WireMock hybrid：高優先序範例與廣域代理

控制器先安裝優先序 1 的固定 GET/POST mapping，再裝優先序 10 的 `/*` 原生 proxy mapping。`MOCK-001` 的 GET 命中 stub；`REAL-001` 未命中該 stub，故流向固定 sandbox。此處的 `/*` 範圍比 Microcks 的契約 operation 更廣。

```mermaid
sequenceDiagram
  participant Client as Procurement / HTTP client
  participant W as WireMock.Net :9091
  participant S as Supplier Sandbox
  Client->>W: GET /supplier/catalog/MOCK-001
  W-->>Client: 優先序 1 範例，origin=wiremock
  Note over S: 不新增 request
  Client->>W: GET /supplier/catalog/REAL-001
  W->>S: 優先序 10 代理同一請求
  S-->>W: 真實報價，origin=sandbox
  W-->>Client: sandbox 回應
```

## 3. Microcks hybrid：已知 operation 的範例與 fallback

匯入 `supplier-hybrid.yaml` 後，`Supplier API` 1.0.0 只有 catalog GET、orders POST、by-client-request GET 三個 operation。各自使用 `PROXY_FALLBACK`：先以 URI 部分或 JS 本文規則找範例，未命中**該已知 operation 的範例**時才代理。`/supplier/unknown` 沒有 operation，不能宣稱會走 fallback。

```mermaid
sequenceDiagram
  participant Client as Procurement / HTTP client
  participant M as Microcks :8080
  participant S as Supplier Sandbox
  Client->>M: GET /rest/Supplier+API/1.0.0/supplier/catalog/MOCK-001
  M-->>Client: URI_PARTS 命中，origin=microcks
  Note over S: 不新增 request
  Client->>M: GET /rest/Supplier+API/1.0.0/supplier/catalog/REAL-001
  M->>S: 已知 GET operation 的 PROXY_FALLBACK
  S-->>M: 真實報價，origin=sandbox
  M-->>Client: sandbox 回應
  Client->>M: GET /rest/Supplier+API/1.0.0/supplier/unknown
  M-->>Client: 未描述 operation；觀察實際狀態
  Note over S: 不應把未知路徑解釋為全域代理
```

## 4. 模式切換與讀回：控制成功不等於流量正確

管理後台的 WireMock 操作送到自製 `/control/mode`，控制器重建原生 mapping 並清除 journal；Microcks 操作送到 `/control/microcks/mode`，控制器匯入固定 YAML 並確認三個原生 operation。兩者須再次讀回狀態；之後再發唯一測試請求核對資料路徑。

```mermaid
sequenceDiagram
  actor User as 操作員
  participant Admin as /admin/ 整合工具
  participant C as SupplierMock 控制服務
  participant Native as WireMock 或 Microcks 原生 API
  participant S as Supplier Sandbox
  User->>Admin: 選 mock / proxy / hybrid
  Admin->>C: POST 固定模式
  alt WireMock
    C->>Native: 清 mapping 和 journal，安裝預設 mapping
  else Microcks
    C->>Native: 固定檔名上傳 YAML，必要時校正三個 operation
  end
  Native-->>C: 原生設定
  C-->>Admin: 套用結果
  Admin->>C: GET 狀態與規則
  C->>Native: 即時讀回
  Native-->>Admin: 確認的模式或 custom / unavailable
  User->>Native: 用新識別發測試 HTTP 請求
  Native-->>User: 回應 origin
  User->>S: 查看請求紀錄前後值
```

## 5. 供應商已提交、呼叫端逾時：保留原 key 協調

在 sandbox 把 `delayAfterCommitMs` 設為受控值時，可讓供應商持久化訂單後才延遲回應。Procurement 先在本地保存唯一 `clientRequestId`，送單只有一次 HTTP POST；逾時標記 `SubmissionUnknown`。依原本採購單 `id` 呼叫 reconcile，系統使用同一 provider 和同一 `clientRequestId` 查供應商，不產生新採購身分。查不到或通訊不確定仍保持未知狀態，不能當拒絕。

```mermaid
sequenceDiagram
  actor User as 操作員
  participant P as Procurement API
  participant DB as Procurement PostgreSQL
  participant G as HTTP Supplier Gateway
  participant S as Supplier Sandbox
  User->>P: POST purchase-orders，固定 clientRequestId
  P->>DB: 原子建立或取回同 key 採購身分
  P->>G: SubmitAsync(原身分)
  G->>S: POST /supplier/orders
  S->>S: 保存供應商訂單
  Note over S,G: 提交後延遲，呼叫端逾時
  G-->>P: supplier_timeout
  P->>DB: 標示 SubmissionUnknown
  P-->>User: 202 與原採購單 id
  User->>P: POST /purchase-orders/{id}/reconcile
  P->>DB: 讀取原 provider 與 key
  P->>G: LookupAsync(原身分)
  G->>S: GET /supplier/orders/by-client-request/{原 key}
  S-->>G: 已存在的同一訂單
  G-->>P: Found 與身分驗證後結果
  P->>DB: 條件式套用 Accepted
  P-->>User: 同一採購單的確認狀態
```

## 6. 實際收貨才入庫：兩端各自保證冪等

收貨與 Procurement source outbox 同交易；relay 的 `published_at` 只代表持久化傳輸交接，不代表 Kafka 已消費。Inventory Consumer 以 `ReceiptId` 執行庫存端收貨；Inventory PostgreSQL 同交易保存 receipt、增加 stock 並寫 Inventory outbox。重送相同 ID 與相同內容讀回既有結果；不同內容必須衝突。

```mermaid
sequenceDiagram
  actor User as 倉管
  participant P as Procurement API
  participant PDB as Procurement PostgreSQL
  participant Relay as Procurement outbox relay
  participant K as Kafka / Wolverine
  participant C as Inventory Consumer
  participant IDB as Inventory PostgreSQL
  User->>P: POST /purchase-orders/{id}/receipts，ReceiptId 與數量
  P->>PDB: 同交易保存收貨和 GoodsReceived source outbox
  P-->>User: 201 created=true 或重播 200 created=false
  Relay->>PDB: 取得待交付 source outbox
  Relay->>K: 持久化交接並發布 GoodsReceived
  K->>C: 至少一次交付事件
  C->>IDB: 同交易認領 ReceiptId、加 stock、寫 Inventory outbox
  IDB-->>C: 新結果或同內容已處理
  User->>P: 以同 ReceiptId、同數量重送
  P->>PDB: 讀回既有 receipt，不再建立 source outbox
  P-->>User: 200 created=false
```

## 7. 銷售訂單另走庫存保留

銷售不是供應商採購。Orders 在建立銷售訂單前向 Inventory 要求保留，保留失敗便不提交訂單；成功後 Orders 保存訂單與自己的 `OrderPlaced` 來源事件。此圖只描述目前同步保留的責任順序，沒有聲稱銷售與採購共享交易。

```mermaid
sequenceDiagram
  actor User as 業務
  participant O as Orders API / PlaceOrderUseCase
  participant I as Inventory API / reservation
  participant ODB as Orders PostgreSQL
  User->>O: 建立銷售訂單，OperationId
  O->>I: ReserveAsync(OperationId, ProductId, Quantity)
  alt 庫存不足或保留失敗
    I-->>O: Result=false
    O-->>User: 不建立訂單
  else 保留成功
    I-->>O: Result=true
    O->>ODB: Commit 訂單與 OrderPlaced
    O-->>User: OrderId
  end
```
