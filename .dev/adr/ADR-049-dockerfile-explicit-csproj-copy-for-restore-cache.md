# ADR-049: Dockerfile 採用顯式 csproj COPY 以維持 Restore 快取效益

## 狀態

Accepted (2026-02-22)

## 背景

本專案的容器建置流程以多階段 Dockerfile 為主，且 `dotnet restore` 前會先 `COPY` 專案檔（`*.csproj`）來提升層快取命中率。

若改為在 restore 前直接 `COPY . .`，雖可降低 Dockerfile 維護成本，但任一 `.cs` 變更都可能使 restore 層失效，導致建置時間上升。

另一方面，顯式 `COPY` 也有維護成本：當 `ProjectReference` 新增或調整時，若 Dockerfile 未同步更新，會造成 restore 失敗。

## 決策

維持目前策略：Dockerfile 在 `dotnet restore` 前，採用顯式 `COPY` 所有必要 `*.csproj`（包含入口專案與其遞迴 `ProjectReference`）。

並新增輔助腳本（先以檢查/建議模式）來降低人工維護風險：

- 檢查 Dockerfile 的 `COPY *.csproj` 是否覆蓋入口 `csproj` 的遞迴相依
- 輸出缺漏項目與建議的 `COPY` 指令
- 預設不自動改檔，先供團隊評估是否納入日常流程或 CI gate

## 理由

- 保留 `dotnet restore` 層快取優勢，縮短日常重建時間
- 在多 BC、多專案依賴場景下，避免 restore 因程式碼變動而頻繁重跑
- 以腳本補足顯式清單的維護成本，兼顧效能與可維護性

## 取捨

### 優點

- Restore 快取命中率高，建置速度穩定
- 問題定位明確（缺哪個 csproj 一目了然）
- 與官方多階段最佳實務相容

### 缺點

- Dockerfile 需要跟隨 `ProjectReference` 變更維護
- 專案新增/重構後，若忘記同步會導致 restore 失敗
- 需要額外腳本與流程約束

## 替代方案

### 方案 A：restore 前 `COPY . .`

優點：
- Dockerfile 幾乎不需維護 csproj 清單

缺點：
- 任一程式碼變更都可能使 restore 層失效，建置較慢

### 方案 B：使用 wildcard 複製 csproj

優點：
- 比顯式清單簡短

缺點：
- 路徑保留與遞迴行為不直觀，易產生不可預期結果
- 在多層資料夾結構下可讀性與可驗證性較差

## 後果與落地

- 新增/調整 `ProjectReference` 時，必須同步檢查 Dockerfile 的 `COPY *.csproj`
- 建議在 code review 或 CI 增加「Dockerfile/csproj 同步檢查」步驟
- 目前先提供腳本供團隊評估採用方式（本機檢查或 CI 阻擋）

## 相關

- `docker-compose/docker-compose.yml`
- `src/*/Presentation/*/Dockerfile`
- `.ai/scripts/check-dockerfile-csproj-copy-sync.ps1`
