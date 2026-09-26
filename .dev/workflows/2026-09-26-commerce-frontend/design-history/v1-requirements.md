# 前台與營運開發後台需求

created_at: 2026-09-26T06:15:44+00:00; updated_at: 2026-09-26T06:15:44+00:00

Issue: [#18](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/18)。來源：2026-09-26 使用者直接要求；框架任選、src 放置、Nginx、YARP 單入口、Sol 實作與 coordinator 覆核；授權 Issue、PR、main 合併與本次分支/worktree 清理。這是同一個完整 workflow。

一般使用者先採商品瀏覽、單品下單與訂單查詢；後台採商品、庫存、採購收貨、mock/proxy 管理。此分工為 coordinator 在委託設計範圍內的選擇，使用者可調整。不是新增身份領域：現有匿名 localhost 實驗入口保留，前後台名稱不代表已實作認證、角色授權或租戶隔離。

| ID | 使用者故事與驗收結果 |
| --- | --- |
| AC01 | 顧客能搜尋現有商品、查看商品、選擇正整數數量下單，看到真實訂單 ID，依 ID 查詢行項。錯誤不顯示成功；不編造訂單狀態、物流、付款或伺服器訂單歷史。 |
| AC02 | 營運人員能新增/修改/刪除商品，查詢及初始化/調整庫存，查詢供應商報價、建立採購、核對不確定結果、部分收貨。每次具副作用操作都有提交中狀態，錯誤後保留需要查核的識別與輸入。 |
| AC03 | 維護/開發人員能在後台切換兩個真實引擎的 mock/proxy/hybrid、讀取目前狀態/規則；WireMock 請求紀錄可查看及明確清除；Sandbox 可查看請求/訂單及設定延遲。Microcks 現況由原生 API 讀回，未知/自訂設定不得冒稱已套用預設。 |
| AC04 | 生產 build 由 Nginx 提供，YARP 入口 /web/*、/admin/*、/api/{domain}/*。重新整理深層路由與資源載入成功，API/不存在的資源不回傳 SPA HTML。 |
| AC05 | 桌面及 390px 手機可操作，表單有可見 label、鍵盤焦點、loading/empty/error；Vue/TS build 與必要測試、實際 YARP/Docker/API/browser 旅程有證據。保留既有 volume 與受保護 observability。 |
| AC06 | Sol 子代理分工與首輪/修復結果可追溯，parent review 完成後建立 PR、合併 main、核對遠端、清理本次 worktrees/branches，運行服務供 owner 檢視。 |

不擴充：付款/物流、登入/SSO/權限、客戶或租戶資料、全站後端重構、任意 mock 腳本上傳、公開網路部署、既有 domain ORM 改選。產品資料無圖片/分類：使用中性的產品圖示，不捏造商品圖片或分類。金額 UI 採 TWD 的實驗顯示慣例，既有 Products/Orders 並無新增 currency contract。

現況來源：main 8213a9e；ProductsController、OrdersController、ProcurementController、InventoryController、SupplierMock/SupplierSandbox Program.cs，以及現有 Compose/YARP JSON。兩位 Sol discovery 先查 code graph，Procurement 缺漏及旧圖內容改由實際檔案核對。已有 /api/products 無分頁列表、/api/orders 無列表且 details 僅行項；不以 UI 虛構缺少資料。所有資料持久化與不變條件仍由既有 domain API 負責。
