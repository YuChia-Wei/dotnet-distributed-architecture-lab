# Commerce Lab 營運工作台

內部業務與倉管的 Vue 3 + TypeScript 操作介面，部署在同源 `/web/`。商品主檔與開發控制在 `/admin/`。

```sh
npm ci
npm run typecheck
npm test
npm run build
```

本機開發使用 `npm run dev`。API 呼叫一律指向同源 `/api/...`，開發時須由反向代理提供 API；正式環境由 YARP 將 `/web/*` 轉到本容器 Nginx。

來源契約：`.dev/workflows/2026-09-26-commerce-frontend/specifications.md` 與現有 Products、Orders、Inventory、Procurement controllers。`InventoryItem.Restock` 實際為加上指定數量；UI 標為「退貨回補（增加庫存）」。訂單查詢僅顯示 `orderId` 與 `lineItems`。採購最多顯示 API 回傳的最近 100 筆。

連線或服務回應不確定時，不自動重送寫入。銷售保留原 operationId 供查核；採購固定 clientRequestId，須先查最近採購或詳情再開新草稿；收貨保留 receiptId 與數量，先讀回 receipts，才允許用相同身分重送。
