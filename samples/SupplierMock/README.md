# 供應商模擬器與 Microcks 契約

`SupplierMock.WebApi` 在固定內部連接埠執行真正的 WireMock.Net 伺服器，並提供本機實驗室操作頁面。WireMock 會依啟動設定中的固定上游網址轉送請求；操作頁面不接受任意上游網址。

Microcks 契約位於 `microcks/`：

- `supplier-mock.yaml` 提供固定範例回應；建立訂單以原生 JS dispatcher 比對完整固定範例內容，其他本文不會收到固定接受回應。
- `supplier-proxy.yaml` 對已描述的操作使用原生 `PROXY` dispatcher。
- `supplier-hybrid.yaml` 使用原生 `PROXY_FALLBACK` dispatcher；商品路徑與查詢識別碼依 URI 範例分派，建立訂單則用原生 JS dispatcher 比對完整固定範例內容，其他內容交由 Microcks 原生代理功能轉送。

## 切換 Microcks 契約

建議使用 repo 根目錄的匯入腳本。它會將所選契約固定以上傳名稱 `supplier-api.yaml` 匯入，檢查服務識別資料，並讀回匯入結果：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/procurement-lab/Set-MicrocksMode.ps1 -Mode hybrid
```

`-Mode` 可設為 `mock`、`proxy` 或 `hybrid`。若使用 Microcks 網頁操作介面手動切換，請先將欲匯入的選定契約檔以相同名稱 `supplier-api.yaml` 上傳。Microcks 會依來源檔案名稱累積契約；直接用三個不同檔名匯入會留下多份同名服務版本，造成操作頁面與呼叫結果混淆。

Microcks uber 1.15.0 的內部資料庫是暫存的。Microcks 重新啟動後，請重新匯入所需契約。供應商沙盒與 Procurement 的 PostgreSQL 資料則由持久化資料磁碟區保存。

Microcks 的 dispatcher 只作用於已匯入契約所描述的操作；未知路徑不是全域代理。匯入契約或讀到範例回應本身不能證明代理已生效，請由整合驗收以實際 HTTP 請求驗證。
