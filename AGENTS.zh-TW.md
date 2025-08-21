# 專案貢獻指南（Repository Guidelines）

本指南整合 AI_CLI_PROMPT（中/英）與本庫慣例。系統採用 Clean Architecture、DDD、CQRS；訊息由 WolverineFx 處理；資料庫為 PostgreSQL；佇列採 RabbitMQ 或 Kafka。

## 專案結構與模組
- 原始碼位於 `src/<Context>`，分兩層級：
  - `DomainCore`：`<Service>.Applications`、`<Service>.Domains`、`<Service>.Infrastructure`（層名用複數）。
  - `Presentation`：`<Service>.WebApi`、`<Service>.Consumer`（每個可執行專案都需 `Dockerfile`）。
- 共用程式庫：`src/BuildingBlocks`、`src/BC-Contracts`（訊息結構）、`src/Shared`（Shared Kernel）。
- 工具與資料：`docker-compose/`、`sql-script/`、設計文件在 `doc/`。方案檔：`MQArchLab.slnx`，其資料夾結構需對應目錄。

## 建置、測試與開發指令
- 還原/建置：`dotnet restore` && `dotnet build`（於 repo 根目錄）。
- 執行 API：`dotnet run --project src/Order/Presentation/SaleOrders.WebApi`（Products 類似）。
- 執行 Consumer：`dotnet run --project src/Order/Presentation/SaleOrders.Consumer`（Products 類似）。
- 選擇 Broker：設定 `QUEUE_SERVICE=Kafka` 或 `RabbitMQ`，並設定 `ConnectionStrings__KafkaBroker` / `ConnectionStrings__MessageBroker`。
- 一鍵本機環境：`docker-compose -f ./docker-compose/docker-compose.yml up -d`。

## 程式風格與命名
- 依 `.editorconfig`：空白縮排、CRLF、150 字元；`using` 先 System；命名空間對應資料夾。
- 命名：介面 `I*`；型別/方法/屬性 PascalCase；實例欄位 `_camelCase`；優先檔案層級命名空間。
- DI：於各專案提供 `AddApplicationServices`、`AddInfrastructureServices` 擴充方法。
- API DTO：輸入 `*Request`、輸出 `*Response`；WebApi 啟用 Scalar 與 OpenAPI。

## 測試指南
- 採 xUnit；測試專案命名 `*.Tests`（例：`tests/SaleProducts.Domains.Tests`），類別 `<TypeName>Tests`；使用 `dotnet test` 執行。

## Commit 與 PR 準則
- Commit：簡短祈使句，必要時加範圍（例：`orders: enable Kafka auto-provision`）；可註明工具（如 “by gemini cli”）。
- PR：說明動機、關聯 Issue、影響的服務/專案，並附本機證據（Scalar/Kafka/RabbitMQ 截圖或日誌）；使用 `.github/pull_request_template.md`。

## 安全與設定
- 使用環境變數或密碼管理，避免提交機敏資訊。常用 UI：Kafka `http://localhost:19000`、RabbitMQ `http://localhost:15672`（guest/guest 僅供開發）。

