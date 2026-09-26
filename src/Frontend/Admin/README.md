# 商務實驗室管理後台

/admin/ 是內部商品主檔與供應商整合工具工作區。庫存、採購、收貨與銷售訂單的日常作業位於 /web/。目前本機實驗環境維持匿名入口；本應用程式沒有聲稱提供登入或角色授權。

## 開發與檢查

需求：Node.js 22.12–22.x、npm。於此目錄執行：

    npm ci
    npm run dev
    npm run typecheck
    npm run test
    npm run build

Vite 開發伺服器將 /api 代理至本機 YARP localhost:8888。瀏覽器資料請求一律使用同源 /api/...。生產建置的資源 base 與 Vue Router history 都是 /admin/。Dockerfile 建立獨立 Nginx 映像；YARP 必須保留 /admin 前綴至 Nginx。Nginx 只對 /admin/ 下的應用路由回退至入口 HTML，缺失的 /admin/assets/ 資源及前綴外路徑回傳 404。

管理工具使用 /api/admin/supplier-mock/control/* 及 /api/admin/supplier-sandbox/sandbox/*。WireMock 模式/重設可能清除規則與請求紀錄；Microcks 預設匯入會替換 Supplier API 原生規則。介面要求確認，並在完成後重新讀取服務狀態。Microcks 自訂或不可用狀態不顯示為預設已就緒。原生 Microcks 進階介面可在整合環境的 localhost:8184 獨立檢查；日常控制不需從瀏覽器直連該埠。

本目錄的單元測試覆蓋 HTTP 失敗/格式、商品與延遲驗證、控制回應辨識。實際 Docker、YARP、原生引擎及瀏覽器操作由整合階段驗證。
