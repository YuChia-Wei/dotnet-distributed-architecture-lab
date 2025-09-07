# Repository Guidelines

- 本專案採用以下設計模式並嚴格遵守
  - Domain-Driven Design
  - Clean Architecture
  - CQRS
- 外部系統選型
  - 資料庫：PostgreSQL 16
  - Message Queue：同時支援 RabbitMQ 與 Kafka
- 展現層專案預設以容器發布

## 資料夾結構

| 資料夾位置                           | 內容                                                                                          |
|---------------------------------|---------------------------------------------------------------------------------------------|
| ./.gemini                       | gemini cli 的設定資料                                                                            |
| ./.github                       | github & github copilot 的資源                                                                 |
| ./docker-compose                | docker compose 檔案與部署設定、資料                                                                   |
| ./docs                          | 說明文件與開發時額外想要記錄的議題資料                                                                         |
| ./https                         | 用於快速測試的 http 檔案                                                                             |
| ./https/<Context>               | <Context>領域的 web api 測試用 http 檔案                                                            |
| ./memory                        | AI Agents 作業時的進度資料                                                                          |
| ./scripts                       | spec-kit 使用的執行語法                                                                            |
| ./specs                         | 功能規格，Spec-driven development with AI 時的必要檔案                                                 |
| ./sql-script                    | 資料庫語法                                                                                       |
| ./src                           | dotnet 原始碼資料夾                                                                               |
| ./src/BC-Contracts              | 跨領域合約 (Message Queue 的傳遞物件)                                                                 |
| ./src/BuildingBlocks            | 系統所需的基礎框架                                                                                   |
| ./src/Shared                    | 通用領域的共用核心                                                                                   |
| ./src/<DomainName>              | <DomainName>領域                                                                              |
| ./src/<DomainName>/DomainCore   | <DomainName>領域的核心專案，包括但不限於領域物件層、應用層、基礎建設層等專案                                                |
| ./src/<DomainName>/Presentation | <DomainName>領域的展現層專案，包括但不限於 WebApi、Consumer                                                 |
| ./templates                     | Spec-driven development with AI 的範本檔案，提供 AI Agents 在 `/spec` `/plan` `/task` 等功能指令時所需要的範本檔案 |
| ./tests                         | 測試專案資料夾，包括但不限於「使用 Xunit 開發的 dotnet 測試專案」、「使用 k6 撰寫的 E2E 測試腳本」                               |

## 專案規則

| 對應分層  | 專案職責                           | 命名規則                            | 放置位置                            |
|-------|--------------------------------|---------------------------------|---------------------------------|
| 領域層   | 領域核心物件                         | <DomainName>.Domains            | ./src/<DomainName>/DomainCore   |
| 服務層   | 應用服務實作                         | <DomainName>.Applications       | ./src/<DomainName>/DomainCore   |
| 基礎建設層 | 基礎建設 (技術細節)                    | <DomainName>.Infrastructure     | ./src/<DomainName>/DomainCore   |
| 展現層   | Web Api                        | <DomainName>.WebApi             | ./src/<DomainName>/Presentation |
| 展現層   | Queue Consumer                 | <DomainName>.Consumer           | ./src/<DomainName>/Presentation |
|       | Cross Bounded Context Contract | Lab.MessageSchemas.<DomainName> | ./src/BC-Contracts              |
|       | Building Blocks                | Lab.BuildingBlocks.<layer>      | ./src/BuildingBlocks            |
|       | Tests Project                  | <Target Project>.Tests          | ./tests                         |

## 軟體實作規則

- 專案內資料夾應使用複數型命名
- 方案檔 (.slnx) 中的方案資料夾除了 測試專案 (tests) 外，都應符合實際的檔案目錄
- 偏好使用 `this.`
- 使用 WolverineFx 處理 Command / Query / Event 的發布與處理
- 除非特別指定，不然 CQRS 相關物件皆遵循以下規則
  - Command 與 Command Handler 放置於同一個 cs 檔案下，檔案以 command 命名
  - Query 與 Query Handler 放置於同一個 cs 檔案下，檔案以 Query 命名
  - Event 與 Event Handler 依據以下規則放置
    - Domain Event 放置於 `<DomainName>.Domains` 專案的 `DomainEvents` 資料夾
    - Domain Event Handler 放置於 `<DomainName>.Applications` 專案的 `DomainEventHandlers` 資料夾
    - Integration Event 放置於 `Lab.MessageSchemas.<DomainName>` 專案的 `IntegrationEvents` 資料夾
    - Integration Event Handler 放置於要處理該跨領域事件的 `<DomainName>.Consumer` 專案的 `IntegrationEventHandlers` 資料夾
- DTO 命名慣例
  - 在 <DomainName>.WebApi 中的 input: `*Request`, output: `*Response`
  - 在 <DomainName>.Application 中的 input: `*Input`, output: `*Output`
- 公開的介面、類別、方法都需要有以`繁體中文臺灣用語`撰寫的摘要

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
