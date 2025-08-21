# 專案貢獻指南（Repository Guidelines）

本指南整合 AI_CLI_PROMPT（中/英）與本庫慣例，做為 AI 與貢獻者的單一真實來源。架構：Clean Architecture + DDD + CQRS；訊息由 WolverineFx 處理；資料庫 PostgreSQL；佇列 RabbitMQ 或 Kafka。

## 專案結構與規則
- 原始碼僅放於 `src/<Context>`。兩大群組：
  - `DomainCore`：`<Service>.Applications`、`<Service>.Domains`、`<Service>.Infrastructure`（層名用複數）。
  - `Presentation`：`<Service>.WebApi`、`<Service>.Consumer`（每個可執行專案都需 `Dockerfile`）。
- 共用程式庫：`src/BuildingBlocks`、`src/BC-Contracts`（訊息結構）、`src/Shared`（Shared Kernel）。
- 工具/資料：`docker-compose/`、`sql-script/`、設計文件在 `doc/`。方案檔 `MQArchLab.slnx` 需以方案資料夾對應目錄結構。
- API DTO 命名：輸入 `*Request`、輸出 `*Response`。公開 API 應具備摘要（建議 zh‑TW）。

## 開發流程（AI 與人）
1) 確認範圍：服務名稱（如 Invoices）、Context 資料夾（如 `Invoice`）、要建立的層級。
2) 正確路徑建立專案：
   - `dotnet new webapi -n Invoices.WebApi -o src/Invoice/Presentation/Invoices.WebApi`
   - `dotnet new classlib -n Invoices.Applications -o src/Invoice/DomainCore/Invoices.Applications`
3) 加入方案並放到對應方案資料夾：
   - `dotnet sln add src/Invoice/Presentation/Invoices.WebApi/Invoices.WebApi.csproj --solution-folder "Invoice/Presentation"`
4) 各專案內提供 DI 擴充方法（如 `AddApplicationServices`、`AddInfrastructureServices`）。
5) 所有可執行專案需 Dockerfile（多階段建置）；若需本機整合，於 `docker-compose/docker-compose.yml` 新增服務項。

## 建置、執行與 Broker
- 建置：`dotnet restore` && `dotnet build`（repo 根目錄）。
- 執行 API/Consumer：
  - Orders API：`dotnet run --project src/Order/Presentation/SaleOrders.WebApi`
  - Orders Consumer：`dotnet run --project src/Order/Presentation/SaleOrders.Consumer`（Products 類似）
- Broker 以環境變數選擇：`QUEUE_SERVICE=Kafka|RabbitMQ`，並對應設定 `ConnectionStrings__KafkaBroker` 或 `ConnectionStrings__MessageBroker`。
- 本機整包：`docker-compose -f ./docker-compose/docker-compose.yml up -d`。

## 程式風格
- 遵循 `.editorconfig`：空白縮排、CRLF、150 字元；`System` 先於其他 using；命名空間對應資料夾；優先檔案層級命名空間；允許 top‑level statements。
- 命名：介面 `I*`；型別/方法/屬性 PascalCase；實例欄位 `_camelCase`。

## 測試
- 預設採 xUnit。測試專案放於 `tests/*/*.Tests.csproj`（例：`tests/SaleProducts.Domains.Tests`）；類別 `<TypeName>Tests`；以 `dotnet test` 執行。

## Commit 與 PR
- Commit：簡短祈使句，可加範圍（例：`orders: enable Kafka auto-provision`）；必要時註明產生工具（如 “by gemini cli”）。
- PR：說明動機、關聯 Issue、影響的服務/專案，並附證據（Scalar/Kafka/RabbitMQ 截圖或日誌）；使用 `.github/pull_request_template.md`。

## 安全與設定
- 使用環境變數或使用者密鑰，避免提交機敏資訊。常用 UI：Kafka `http://localhost:19000`、RabbitMQ `http://localhost:15672`（guest/guest，僅開發）。

## PRD 模式（用於大型需求）
當需求寬泛或需節省 token，請在首次回覆提供精簡 PRD：
- 摘要：一段說明問題與預期結果。
- 目標：3–6 點列出將交付的內容。
- 非目標：明確不處理的事項。
- 侷限：技術、風格、目錄、命名、DI、Dockerfile/Compose 等約束。
- 驗收標準：可驗證的檢核（能建置/執行、端點可用、測試通過）。
- 計畫：4–8 個短步驟（建立/修改檔案、必要指令）。
