# 商務作業前台與管理後台實驗

本手冊對應 Issue #18 與 workflow `2026-09-26-commerce-frontend`。`/web/` 是內部業務／倉管作業台，`/admin/` 是商品主檔與整合工具。此 localhost 實驗入口沒有新增登入、角色授權或公開部署保護。

## 啟動與檢視

在 repository 根目錄使用 PowerShell 7、Docker Compose，並使用現有整合專案 `mqarchlab-pr5-integration`。啟動腳本先調用採購實驗的既有 bootstrap，再啟動 Orders、Products、兩套前端及 YARP；所有 `up` 均限於指定服務並加 `--no-deps`，不啟動受保護的 observability。腳本不執行 `down`、`down -v` 或 `prune`，保留既有 PostgreSQL/Kafka volumes 與資料。若映像已建好，可傳 `-NoBuild`。

```powershell
./scripts/frontend-lab/Start-Lab.ps1
```

完整 Compose 合成順序必須保留 base、override、verification、procurement、frontend 五份；少了 verification overlay 時原有 regression-tests 設定無法合成：

```powershell
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

YARP 單入口為 `http://127.0.0.1:8888`；前台 `/web/`、後台 `/admin/`。兩套 Nginx 僅在 Docker 網路提供 port 80，不發布主機 port。YARP 保留 `/web`、`/admin` 前綴給各自 Nginx，裸前綴由 Nginx 轉為尾斜線。API 仍走 `/api/products`、`/api/orders`、`/api/inventory`、`/api/procurement`，不會落入 SPA fallback。管理入口僅允許 `/api/admin/supplier-mock/*` 及 `/api/admin/supplier-sandbox/*`，YARP 只移除該管理前綴，保留 `/control/*` 與 `/sandbox/*` 給現有服務。

供應商控制：WireMock `GET /api/admin/supplier-mock/control/state`、`POST /control/mode`、`POST /control/reset`、`GET /control/mappings`、`GET/DELETE /control/requests`。Microcks `GET /api/admin/supplier-mock/control/microcks/state`、`POST /control/microcks/mode`。Sandbox `GET /api/admin/supplier-sandbox/sandbox/orders`、`GET /sandbox/requests`、`GET/PUT /sandbox/control`。瀏覽器資料 API 使用同源 YARP；Microcks 進階原生 UI 仍在 `http://127.0.0.1:8184/`。

Microcks 控制器僅接受 `mock`、`proxy`、`hybrid`，從程式隨附的三個 YAML 套用固定 `supplier-api.yaml` 上傳檔名。上傳後若原生匯入保留舊派送設定，控制器只針對 `Supplier API` `1.0.0` 的三個已知 operation 校正 dispatcher/rules，並在完整原生讀回吻合後才回報 `ready`。狀態每次讀原生 `/api/services` 的 operations/dispatcher/rules；清單查找最多讀取十頁、每頁一百筆，超出界限時回報 `unavailable`，不猜測模式。尚未匯入、外部手動改動、失敗或無法連線會分別回報 `unconfigured`、`custom`、`failed`、`unavailable`，不沿用舊模式。Microcks 的 proxy/fallback 只作用於已匯入的 operation；WireMock 的原生 fallback 可涵蓋更廣路徑。切換後仍應以實際供應商 origin 與 Sandbox request log 驗證路由。

若啟動或請求失敗，先讀 `docker compose @compose ps` 及 `docker compose @compose logs --tail 100 <service>`，再檢查對應 API／資料庫。F: RAM disk worktree 可作 Docker build context；Docker Desktop 對該磁碟的執行期 bind mount 可能無法使用，因此需要 bind mount 的 Compose 部署應從持久 primary main 執行。合併後在該路徑重新部署並核對 `/web/`、`/admin/`，再清理 worktree。Compose 語法成功、單元測試成功與實際 Docker/瀏覽器旅程是不同證據；本手冊不宣稱後者已通過。
