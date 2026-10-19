# ArchPrecept 本機試用結果

日期：2026-10-19（Asia/Taipei）。工作項目：[Issue #32](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/32)。分支：`codex/archprecept-package-trial`。工作區：`F:/git-worktree/4ac5/dotnet-mq-arch-lab`。

## 實作結果

- 四套件均固定 `0.0.1-preview`；Domain / Application / Messaging 分別由原有三個 BuildingBlocks csproj 引用，產品 src 的 analyzer 由 `src/Directory.Build.targets` 引用。
- 移除 16 份重複契約實作；直接呼叫端、既有測試與 EF/Wolverine sample 改用套件命名空間。
- 保留 target `EsAggregateRoot`，繼承套件 AggregateRoot 並保留衍生建構子重播規則。套件的基底建構子重播不符合本專案 AGGREGATE-ES-001，未直接使用。
- BC-owned 事件、診斷訊息、Infrastructure adapters 與資料 schema 沒有改變責任；沒有改變 ORM、broker、業務流程、交易與測試 mock 選擇。
- `NuGet.Config` 與 `src/NuGet.Config` 映射 `ArchPrecept.*` 至被 Git 忽略的 `src/artifacts/archprecept-feed/`。已修改六個 src-context Dockerfiles 以在 restore 前帶入設定與 feed，並讓 root context 只放行這個 feed 子目錄。
- 已補上 [操作指南](../../operations/archprecept-trial.md)、architecture 事實、operation 導覽、plan 與 [套件 hashes](package-hashes.json)。原始編碼標記與 LF 政策保持。

## 實際驗證

環境：Windows / PowerShell、.NET SDK `10.0.402`，符合 global.json 的 roll-forward；工作目錄為 repo 根目錄。外部整合測試未 opt-in。

| 檢查 | 結果與界線 |
| --- | --- |
| 發布成品 hashes | `passed`：四個本機 nupkg 與上游發布紀錄 SHA-256 全部相符，未重新 pack。 |
| 隔離 cache restore | `passed`：41 個 solution 專案完成還原。四套件 `.nupkg.metadata` 的 source 均為本次 worktree 的 local feed。既有第三方套件 cache 作為 fallback。 |
| Release solution build | `passed`：0 errors / 12 warnings；這次 build 的 warning 為 xUnit3003 / xUnit1051。產品編譯未出現 DBA 診斷或 analyzer load/execution failures。初次 build 的三個 CS0246 已補上診斷訊息的套件 using；初次記錄仍保留。 |
| Analyzer 安裝 | `passed`：27 個產品 csproj 的 restore assets 都含 `ArchPrecept.Analyzers.Core/0.0.1-preview`。 |
| Analyzer 載入行為 | `passed`：忽略追蹤的 fixture import 相同 targets；上游已使用的 `public interface IRepository<TEntity, TId> { }` 造成預期 `error DBA1001`，並無 CS8032 / CS9057 / AD0001。預期失敗不是產品 build 失敗，也不表示完整架構合規。 |
| 預設 solution tests | `passed`：9 個 test projects、201 cases、155 passed / 0 failed / 46 skipped；skip 是未執行的外部證據。 |
| Namespace / diff | `passed`：tracked src/tests/samples 中已無未說明的舊契約 namespace；保留的是本專案 EsAggregateRoot 與 Diagnostics namespace。`git diff --check` 通過。 |
| Managed authority | `passed`：官方 framework.lock 與目標工程規則 hashes 未變。沒有修改 `.ai/`、runtime entries 或歷史 workflow。 |

原始碼探索先以 fresh worktree graph 定位，再讀 tracked files；samples 等排除範圍用直接檔案盤點補足。此次未宣稱 optional specialist knowledge reader、framework admission、獨立 code review、Hosted CI 或完整規格符合性驗證通過。

### 測試明細

| Test project | Passed | Failed | Skipped | Total |
| --- | --- | --- | --- | --- |
| EfCoreWolverine.Tests | 12 | 0 | 4 | 16 |
| InventoryControl.Tests | 37 | 0 | 27 | 64 |
| Procurement.Tests | 29 | 0 | 10 | 39 |
| SaleOrders.Domains.Tests | 13 | 0 | 0 | 13 |
| SaleOrders.Tests | 19 | 0 | 0 | 19 |
| SaleProducts.Domains.Tests | 9 | 0 | 0 | 9 |
| SaleProducts.Tests | 22 | 0 | 4 | 26 |
| SupplierMock.Tests | 13 | 0 | 0 | 13 |
| SupplierSandbox.Tests | 1 | 0 | 1 | 2 |
| **合計** | **155** | **0** | **46** | **201** |

Orders Domain 的 13 個 cases、Orders Application/API 的 19 個 cases 全部通過；其中保留的重播、pending events、版本提交及事件序列化相關案例使用實際套件契約。其他既有案例涵蓋 Products、Inventory、Procurement 與 supplier / EF-Wolverine sample 的預設測試範圍。

46 個 skipped cases 分別是 Inventory 27、Procurement 10、EF/Wolverine 4、Products Kafka 4、SupplierSandbox PostgreSQL 1；其具體原因與逐案名稱保存於 `artifacts/archprecept-trial/test-summary.json`。這些結果不證明真實 PostgreSQL、Kafka、交易、outbox/inbox 或外部 supplier runtime 行為。

### 實際執行命令與本機證據

```powershell
dotnet restore MQArchLab.slnx --packages artifacts/nuget-packages -p:RestoreFallbackFolders=C:/Users/h4227/.nuget/packages --verbosity minimal
dotnet build MQArchLab.slnx -c Release --no-restore --disable-build-servers -m:1 --verbosity minimal
dotnet test MQArchLab.slnx -c Release --no-build --no-restore --logger trx --results-directory artifacts/archprecept-trial/test-results --verbosity minimal
```

本機 ignored 證據位於 `artifacts/archprecept-trial/`：`restore.log`、`build-initial.log`、`build.log`、`tests.log`、`test-results/*.trx`、`test-summary.json`、`analyzer-projects.json` 與 `analyzer-smoke.log`。Fixture 是一次性的 analyzer 消費驗證，沒有加入新的維護用測試專案或 solution 成員。

## 首輪交付狀態（後續結果見文末）

- GitHub registry restore：原先 `blocked-by-authentication`（匿名 HTTP 401、gh token 缺 read:packages）；負責人隨後選擇先使用本機版本。此次本機試用已完成，registry 認證與 round trip 仍未驗證。
- Docker image build / Compose runtime / 外部整合測試：`not-run`。Docker 接線已修改，未以設定靜態檢查冒充容器 build 或服務驗收。
- CI / 獨立 review / engine-2 optional knowledge coverage：`not-run`，不以本機測試替代。
- 所有變更仍在本機試用分支，尚未 commit、push、建立 PR、merge、關閉 Issue、tag 或發布。
- 下一步可直接依操作指南繼續本機試用；registry 認證解決後再將兩份 feed URL 一起切回 GitHub Packages，另做隔離 cache restore。停止試用或整合 main 均需保留與上述證據的區別。


## 2026-10-19 Code review 與本機 commit 續行

負責人授權先 code review、確認相容性後 commit 到目前試用分支，明確排除 push 與 merge；之後補充已設定全域 GitHub Packages 來源，可進行實際 NuGet 安裝測試。

正式審查保存於 [ASM-20261019-001](../../assessments/ASM-20261019-001/review-report.md)，workflow 僅引用，不複製報告。Review 由同一 Codex agent 執行，沒有宣稱獨立審查或未執行的 specialist gate。

審查發現一項 P2：test-runner Dockerfile 沒有複製根目錄 NuGet.Config。乾淨 Linux image build 實際出現 NU1101；補上 COPY 後完整重建及預設測試通過。初始失敗證據與修正後成功日誌均保留。

| 續行檢查 | 實際結果 |
| --- | --- |
| 原契約與發布 DLL 相容性 | `passed`：16 個原始 source files 對應 20 個公開型別 API shape；58 項 API/序列化/事件清單/設定/Publisher 行為 assertion 通過。刻意 namespace migration 不承諾外部未重編譯 binary consumer 的 ABI 相容。 |
| 真實 GitHub Packages 還原 | `passed`：直接使用既有全域 `github-yuchia` 設定，四套件下載至全新 `artifacts/archprecept-review/registry-packages`。四份 `.nupkg.metadata` 指向 GitHub endpoint，四個 SHA-256 與發布紀錄一致；未讀出、搬移或提交憑證。 |
| Registry 套件的 Windows Release build | `passed`：SDK 10.0.402，0 errors / 20 warnings，警告類別為 CS8618、xUnit3003、xUnit1051；沒有 DBA、CS8032、CS9057 或 AD0001 診斷。 |
| Windows 預設 tests | `passed`：9 projects / 201 cases，155 passed / 0 failed / 46 skipped。 |
| 修正後 Linux test-runner build | `passed`：SDK 10.0.401，完整 solution restore/build 成功，0 errors / 20 warnings；image `archprecept-review-tests:local`。容器使用本機 feed，未將使用者認證放入 image。 |
| Linux container 預設 tests | `passed`：9 projects / 201 cases，155 passed / 0 failed / 46 skipped。測試容器執行後自動移除，TRX 保存至指定 evidence 子目錄。 |
| Commit message | `passed`：完整 message file 由目前 source `tools/maintenance/validate-git-commits.py --message-file ... --workflow-id 2026-10-19-archprecept-trial` 驗證；工作目錄為 source checkout。此為本次 message-only 檢查，不是 target history 或自動 gate。 |

兩個平台各自執行同一組 201 cases，不能相加為 402 個獨立案例。46 個外部服務案例維持 skip；未執行 Compose 商務流程、實際 PostgreSQL/Kafka opt-in、六個產品 image 的個別建置、容器 registry 認證、Hosted CI、push、merge、Issue 關閉或發布。

專案預設 feed 保留本機試用設定；本輪實際 registry 驗證以 `--configfile` 直接使用使用者層級設定，已排除先前認證 blocker。使用方式見更新後操作指南。

### 本輪證據與命令

本機 ignored evidence 位於 `artifacts/archprecept-review/`：initial subject、compatibility.log、registry-verification.json、registry-restore.log、registry-build.log、windows/linux TRX 與 summary、docker-tests-initial.log、docker-tests.log、linux-tests.log 及完整 commit-message.txt。

```powershell
dotnet restore MQArchLab.slnx --configfile C:/Users/h4227/AppData/Roaming/NuGet/NuGet.Config --packages artifacts/archprecept-review/registry-packages -p:RestoreFallbackFolders=C:/Users/h4227/.nuget/packages --verbosity minimal
dotnet build MQArchLab.slnx -c Release --no-restore --disable-build-servers -m:1 --verbosity minimal
dotnet test MQArchLab.slnx -c Release --no-build --no-restore --logger trx --results-directory artifacts/archprecept-review/windows-test-results --verbosity minimal
docker build --progress plain --file docker-compose/Dockerfile.tests --tag archprecept-review-tests:local .
# Docker run 使用 evidence 目錄 bind mount 至 /results；沒有啟動 Compose 服務。
```

續行的交付邊界為一個經檢查的本機 commit。實際 commit SHA 與 tree、分支和乾淨工作區由 Git read-back 確認；不在本 commit 的內容中自我嵌入其尚未產生的 SHA。Commit 不改變 Issue 的開啟狀態，也不代表 owner 試用驗收或整合 main。
