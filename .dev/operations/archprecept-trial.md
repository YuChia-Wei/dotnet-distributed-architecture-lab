# ArchPrecept 0.0.1-preview 本機試用

本次工作見 [Issue #32](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/32) 與 [試用結果](../workflows/2026-10-19-archprecept-trial/results.md)。四個套件均固定 `0.0.1-preview`。專案預設仍使用已發布 nupkg 的本機副本。初輪 GitHub Packages 匿名請求回傳 HTTP 401；負責人後續設定使用者層級 `github-yuchia` 來源後，已以全新 cache 成功還原四個 registry 套件，並確認來源 metadata 與發布 SHA-256。此實際 NuGet 驗證不依賴 gh 的套件讀取權限。

## 套件對應

| 套件 | 引用位置與取代範圍 |
| --- | --- |
| `ArchPrecept.Contracts.Domain` | `Lab.BuildingBlocks.Domains.csproj`；取代 AggregateRoot、DomainEntity、IAggregateRoot、IDomainEntity、IDomainEvent、ValueObject / IValueObject。 |
| `ArchPrecept.Contracts.Application` | `Lab.BuildingBlocks.Application.csproj`；取代 IAggregateRepository / IDomainRepository、IDomainEventDispatcher、IQueryRepository、PageResult、Result。 |
| `ArchPrecept.Contracts.Messaging.Abstractions` | `Lab.BuildingBlocks.Integrations.csproj`；取代 IIntegrationEvent、IIntegrationEventPublisher、IRequestContract、IntegrationMessageDelivery、MessagingTransportOptions / Profile。 |
| `ArchPrecept.Analyzers.Core` | `src/Directory.Build.targets`；產品 src 專案共用的 Roslyn analyzer，`PrivateAssets=all`。 |

所有直接使用端（包含既有 tests 與 EF/Wolverine sample）改用 `ArchPrecept.Contracts.*` 命名空間。業務事件原本的命名空間、序列化欄位與業務行為保持原狀。三個 BuildingBlocks 專案保留作為套件相依邊界；BC contracts 與 runtime adapters 仍由目標專案持有。

## 必須保留的相容差異

本專案 `Lab.BuildingBlocks.Domains.EsAggregateRoot<TId>` 繼承套件 `AggregateRoot<TId>`，仍自行實作 `Replay`、`Apply` 與提交版本確認。Orders 的衍生建構子在欄位初始化完成後才呼叫 `Replay`。Preview 套件的 EsAggregateRoot 在基底建構子呼叫虛擬 `When`，且沒有相同的 protected Replay API，未滿足目標 AGGREGATE-ES-001 的建構規則，因此此次不直接替換這一型別。其餘事件、實體與聚合契約已採套件型別，沒有保留另一套同名契約。

分析器保持上游的預設 error / warning，不加入 suppress。已退役的 target-local analyzer 與 runtime-validation 專案仍維持退役；此次新增的是外部 NuGet analyzer。

## 準備本機 feed

Git 不追蹤 nupkg。此工作區已將四個已發布成品複製至 `src/artifacts/archprecept-feed/`，並核對 [SHA-256 紀錄](../workflows/2026-10-19-archprecept-trial/package-hashes.json)。在其他 checkout，從可信的發布成品目錄複製四個同版套件至相同位置，核對 hashes 後再 restore；不要重新編譯同版號替代已發布成品。

以 repo 根目錄為工作目錄，將 `$packageDirectory` 指向保存這四個檔案的目錄：

```powershell
$packageDirectory = 'C:/path/to/published-0.0.1-preview'
$manifest = Get-Content .dev/workflows/2026-10-19-archprecept-trial/package-hashes.json -Raw | ConvertFrom-Json
$packages = foreach ($entry in $manifest.sha256.PSObject.Properties) {
    $file = Join-Path $packageDirectory ($entry.Name + '.0.0.1-preview.nupkg')
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.Value) {
        throw "Package hash mismatch: $($entry.Name)"
    }
    Get-Item -LiteralPath $file
}
New-Item -ItemType Directory src/artifacts/archprecept-feed -Force | Out-Null
$packages | Copy-Item -Destination src/artifacts/archprecept-feed

dotnet restore MQArchLab.slnx
dotnet build MQArchLab.slnx -c Release --no-restore
dotnet test MQArchLab.slnx -c Release --no-build --no-restore
```

`NuGet.Config` 及 `src/NuGet.Config` 都以 `ArchPrecept` source key 將 `ArchPrecept.*` 僅映射到本機 feed，其他相依來自 nuget.org。第二份設定支援既有以 src 為 Docker build context 的六個 hosts；兩份設定的 feed 相對路徑不同但指向同一目錄，來源與版本應一起維護。六個產品 Dockerfiles 在 restore 前複製設定、targets 與 feed；root `.dockerignore` 只允許此 feed 的 artifacts 子目錄進入 root build context。共用 test-runner `docker-compose/Dockerfile.tests` 也必須複製根目錄 NuGet.Config，否則 tests 與 samples 會只向 nuget.org 尋找 ArchPrecept 套件並出現 NU1101。沒有認證資料或機器專用 source path 寫入 repo。

## 使用全域 GitHub Packages 設定驗證

負責人已設定的來源名稱為 `github-yuchia`。以下命令直接交由 NuGet 使用既有全域設定與憑證，略過專案預設的本機 feed，並以新的套件 cache 驗證實際 registry 下載。全域檔案不可複製進 repository 或 image，也不要在命令或日誌印出 Token。

```powershell
$globalNuGetConfig = Join-Path $env:APPDATA 'NuGet/NuGet.Config'
dotnet restore MQArchLab.slnx --configfile $globalNuGetConfig --packages artifacts/archprecept-review/registry-packages
dotnet build MQArchLab.slnx -c Release --no-restore
dotnet test MQArchLab.slnx -c Release --no-build --no-restore
```

本次實際驗證另外以既有 nuget.org cache 作為第三方套件 fallback；四個 ArchPrecept 套件均由全新 cache 的 `.nupkg.metadata` 確認來源為 GitHub endpoint，再核對 nupkg hash，沒有將本機 feed 或舊快取誤算為 registry 下載。

目前沒有將兩份專案 NuGet.Config 的預設本機來源切換成 registry。日後切換時，兩份檔案的 source key 與 source mapping 都應使用和全域憑證一致的 `github-yuchia`，value 指向 `https://nuget.pkg.github.com/YuChia-Wei/index.json`。容器認證須另以 build secret 處理；此次 Linux 建置仍使用已核對的本機 feed，不能視為容器 registry 認證驗證。

## 驗證界線與回復

完整實際結果見 [試用結果](../workflows/2026-10-19-archprecept-trial/results.md)。預設測試不啟動外部資料庫或 broker；外部整合測試的 opt-in 與 skip 規則見 [tests/README](../../tests/README.md)。Docker 設定修改與實際 container build/runtime 驗證是不同狀態。

試用全部保留在 `codex/archprecept-package-trial`，尚未整合 main。停止試用時先保存工作區修改，再回到原本 main；日後如整合此變更，應以正常 review/revert 流程回復這一組套件導入及 namespace 變更，不能只移除 PackageReference 而留下套件型別的使用端。
