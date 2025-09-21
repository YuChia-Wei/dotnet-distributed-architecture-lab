# Repository Guidelines

## 適用範圍與優先序
- 本檔為整個 repository 的 AI Agents 與人類協作準則（資料夾樹全域適用）。
- 若子資料夾另有 AGENTS.* 檔，則「越深層越優先」。
- 指令優先序：使用者/審批 > 子資料夾 AGENTS > 本檔 > 其餘一般文件。
- 非必要請避免大規模重構與破壞性操作（刪檔、移動大量檔案、重設 git）。

## 技術背景
- **語言/版本**：C# 13, .NET 9
- **Primary Dependencies**：
  - **Message Handling**: Wolverine.NET
  - **Persistence**: Dapper, Npgsql
  - **Web Api Servers**: ASP.NET Core
  - **Queues Consumer Programs**: Console App
  - **Message Bus**: RabbitMQ and Kafka
- **Database**: PostgreSQL 16
- **Testing**: xUnit
- **Target Platform**: Linux container (via Docker)
- **Constraints**：
  - 跨領域資料同步允許「最終一致性」
  - 整個系統採用 Domain-Driven Design 模式設計
  - 軟體架構採用 Clean Architecture
  - 使用 CQRS
  - 跨領域服務不允許使用 web api 溝通，僅能利用 message queue 機制互動

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
- DTO 命名慣例
  - 在 <DomainName>.WebApi 中的 input: `*Request`, output: `*Response`
  - 在 <DomainName>.Application 中的 input: `*Input`, output: `*Output`
- 公開的介面、類別、方法都需要有以`繁體中文臺灣用語`撰寫的摘要

## CQRS 與 WolverineFx 約定
- Command/Query/Event 物件應為 immutable（`record`）並語義明確，命名採動詞開頭功能結尾（例：`CreateOrderCommand`）。
- Handler 應保持小而專一；避免在 Handler 內混入基礎設施細節（以注入服務協作）。
- 事件處理需考量「至少一次」語意與冪等性；外部 I/O 前先檢查重複處理條件。
- 發佈與訂閱：同邊界內優先使用 Domain Event，跨邊界使用 Integration Event（置於 `BC-Contracts`）。
- 交易邊界：命令處理內的狀態改變需與儲存一致性策略對齊（Outbox/Inbox 如導入則遵循該模式慣例）。
- 使用 WolverineFx 處理 Command / Query / Event 的發布與處理。
- 命名與檔案/位置約定：
  - Command 與 Command Handler 放置於同一個 cs 檔案下，檔案以 Command 命名。
  - Query 與 Query Handler 放置於同一個 cs 檔案下，檔案以 Query 命名。
  - Event 與 Event Handler 依據以下規則放置：
    - Domain Event 放置於 `<DomainName>.Domains` 專案的 `DomainEvents` 資料夾。
    - Domain Event Handler 放置於 `<DomainName>.Applications` 專案的 `DomainEventHandlers` 資料夾。
    - Integration Event Handler 放置於要處理該跨領域事件的 `<DomainName>.Consumer` 專案的 `IntegrationEventHandlers` 資料夾。
