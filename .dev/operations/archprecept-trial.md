# ArchPrecept 0.0.2-preview 試用

目前試用分支為 `codex/archprecept-package-trial`，沿用 [Issue #32](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/32)。套件直接由 GitHub Packages 還原；先前 0.0.1-preview 的紀錄保留於既有 workflow，但不代表本版驗證結果。

## 套件與責任

所有採用的 ArchPrecept 套件固定為 `0.0.2-preview`。

| 套件 | 引用位置／用途 |
| --- | --- |
| `ArchPrecept.Contracts.Domain` | BuildingBlocks.Domains 的一般實體、聚合根與事件契約。 |
| `ArchPrecept.Contracts.Application` | BuildingBlocks.Application 的 Repository、Result、PageResult 與派送 port。 |
| `ArchPrecept.Contracts.Messaging` | BuildingBlocks.Integrations 引用的 IIntegrationEvent、IRequestContract。 |
| `ArchPrecept.Contracts.Application.Messaging` | BuildingBlocks.Integrations 引用的 Publisher port、IntegrationMessageDelivery。 |
| `ArchPrecept.Contracts.Domain.EventSourcing` | Orders Domain 直接引用的 EsAggregateRoot。其他 bounded contexts 不必直接引用。 |
| `ArchPrecept.Analyzers.Core` | src/Directory.Build.targets 共用，PrivateAssets=all，維持原 severity。 |

舊 `Messaging.Abstractions` 已移除。拆分改變 assembly／namespace，所有 adapters 與使用端必須重新編譯；不使用 type forwarder 或同時安裝舊套件來轉接。現行事件儲存依具體業務事件名稱與 JSON 欄位處理，沒有儲存被移動的介面型別名稱，因此本次沒有資料轉換。

`MessagingTransportOptions`／`MessagingTransportProfile` 由 Lab 自己的 `Lab.BuildingBlocks.Integrations.Configuration` 接管，直接引用 Configuration.Abstractions。原有 `Messaging:Profile`、`Messaging:Kafka:ConnectionString`、`Messaging:RabbitMq:ConnectionString` 語意與驗證保留。

Orders 使用新套件 EsAggregateRoot，在衍生建構子內呼叫 LoadFromHistory。已移除 Lab 重複的 ES 基底；保留 replay 不新增 pending、Version 只計算歷史／已提交事件、交易成功後才 MarkChangesAsCommitted 的流程。不可對 ES 直接 Add／Remove／ClearDomainEvents，包含透過一般基底／介面呼叫；dispatcher 只派送已擷取的事件，不清除聚合。未知歷史事件會拒絕載入，重播或 When 失敗後須重新載入新實例。

Orders 與 Inventory 的 Wolverine publisher 明確實作 delivery overload，保留 MessageId、PartitionKey 與 lab-message-id header。只實作單參數 overload 的 publisher 仍不保證使用 metadata。

## 開發機還原與測試

根目錄與 src/NuGet.Config 均以 `github-yuchia` 指向 `https://nuget.pkg.github.com/YuChia-Wei/index.json`，並將 ArchPrecept.* 映射到該來源。使用者層級 NuGet 憑證必須使用相同 source key；不要提交憑證。

於 repo 根目錄執行：

```powershell
dotnet restore MQArchLab.slnx
dotnet build MQArchLab.slnx -c Release --no-restore
dotnet test MQArchLab.slnx -c Release --no-build --no-restore
```

本輪升級另外使用暫時獨立 cache 確認六套件皆為 registry 的 0.0.2-preview，並檢查 assets 不含 Messaging.Abstractions；不需要準備或複製本機 feed。外部 PostgreSQL／Kafka／供應商測試仍依 [tests/README](../../tests/README.md) 明確 opt-in，skipped 不代表外部驗證成功。

## 容器還原

Dockerfiles 使用 BuildKit `nuget_config` secret，既有 Compose build entries 已接上同名 secret。以 `NUGET_CONFIG_FILE` 指定 Linux 容器可使用的 NuGet 設定檔；預設位置沿用 Windows APPDATA/NuGet/NuGet.Config。Windows 加密 Password 無法在 Linux 解密，這種設定不能直接用於 Linux build；應由外部 secret 管理提供相同 source key 的可用設定，不將使用者設定 COPY 到 image。

```powershell
$env:NUGET_CONFIG_FILE = 'C:/path/to/linux-readable/NuGet.Config'
docker compose -f docker-compose/docker-compose.yml build orders-api
# 單獨建置既有驗證入口：
docker build --secret "id=nuget_config,src=$env:NUGET_CONFIG_FILE" -f docker-compose/Dockerfile.tests -t lab-tests:local .
```

Docker context 排除 artifacts、bin、obj，避免把舊本機套件或主機還原輸出帶入。容器驗證需要另外提供適用 secret；開發機 registry restore 成功不等於 Linux 認證或 Compose 業務流程已驗證。
