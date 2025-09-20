# Repository Guidelines

## 適用範圍與優先序
- 本檔為整個 repository 的 AI Agents 與人類協作準則（資料夾樹全域適用）。
- 若子資料夾另有 AGENTS.* 檔，則「越深層越優先」。
- 指令優先序：使用者/審批 > 子資料夾 AGENTS > 本檔 > 其餘一般文件。
- 非必要請避免大規模重構與破壞性操作（刪檔、移動大量檔案、重設 git）。
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
- DTO 命名慣例
  - 在 <DomainName>.WebApi 中的 input: `*Request`, output: `*Response`
  - 在 <DomainName>.Application 中的 input: `*Input`, output: `*Output`
- 公開的介面、類別、方法都需要有以`繁體中文臺灣用語`撰寫的摘要

## 分支與命名規範
- 功能分支一律使用三位流水號前綴：`NNN-簡述`（例：`001-init-service`）。
- `scripts/common.sh` 會檢查規則（正則：`^[0-9]{3}-`）。不符合時部分腳本將中止。
- 目錄與專案名稱請遵循上節「專案規則」與「資料夾結構」。

## 開發流程（AI 與人）
1) 確認範圍：服務名稱（如 Invoices）、Context 資料夾（如 `Invoice`）、要建立的層級。
2) 正確路徑建立專案：
   - `dotnet new webapi -n Invoices.WebApi -o src/Invoice/Presentation/Invoices.WebApi`
   - `dotnet new classlib -n Invoices.Applications -o src/Invoice/DomainCore/Invoices.Applications`
3) 加入方案並放到對應方案資料夾：
   - `dotnet sln add src/Invoice/Presentation/Invoices.WebApi/Invoices.WebApi.csproj --solution-folder "Invoice/Presentation"`
4) 各專案內提供 DI 擴充方法（如 `AddApplicationServices`、`AddInfrastructureServices`）。
5) 所有可執行專案需 Dockerfile（多階段建置）；若需本機整合，於 `docker-compose/docker-compose.yml` 新增服務項。

## CQRS 與 WolverineFx 約定
- Command/Query/Event 物件應為 immutable（建議 `record`）並語義明確，命名採動詞開頭（例：`CreateOrder`）。
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

## 消息契約（BC-Contracts）與版本控管
- 變更原則：
  - 向後相容可直接擴充（新增 optional 欄位）。
  - 破壞性變更需發佈新版本 Schema（並保留舊版本可讀期）。
- 命名空間：`Lab.MessageSchemas.<DomainName>` 下以資料夾/命名空間明確區分版本。
- 測試：每次契約調整需附上 Producer/Consumer 端契約測試（見「測試」章）。
- 位置：Integration Event 放置於 `Lab.MessageSchemas.<DomainName>` 專案的 `IntegrationEvents` 資料夾。

## 建置、執行與 Broker
- 建置：`dotnet restore` && `dotnet build`（repo 根目錄）。
 - 執行 API/Consumer：`dotnet run --project <path-to-csproj>`
- Broker 以環境變數選擇：`QUEUE_SERVICE=Kafka|RabbitMQ`，並對應設定 `ConnectionStrings__KafkaBroker` 或 `ConnectionStrings__MessageBroker`。
- 本機整包：`docker-compose -f ./docker-compose/docker-compose.yml up -d`。

## 程式風格
- 遵循 `.editorconfig`：空白縮排、CRLF、150 字元；`System` 先於其他 using；命名空間對應資料夾；優先檔案層級命名空間；允許 top‑level statements。
- 命名：介面 `I*`；型別/方法/屬性 PascalCase；實例欄位 `_camelCase`。

## 測試
- 預設採 xUnit。測試專案放於 `tests/*/*.Tests.csproj`（例：`tests/SaleProducts.Domains.Tests`）；類別 `<TypeName>Tests`；以 `dotnet test` 執行。
- 測試層次建議（由外而內）：Contract → Integration → Unit。變更契約或跨 Context 行為時至少補齊 Contract/Integration 測試。
- 測試資料與設定應自足（避免依賴本機不可控狀態），必要時於 `docker-compose` 定義對應服務。
- 事件與消息處理需具備冪等與重複投遞測試情境。

## AI Agents 作業準則
- spec-driven development (規格驅動開發)
- 計畫先行：
  - 以 `.specify/scripts/powershell/create-new-feature.sh "feature description"` 建立功能分支與 `specs/<branch>/spec.md`。
  - 以 `.specify/scripts/powershell/setup-plan.sh` 產生 `plan.md` 骨架，並依範本填寫。
  - 以 `.specify/scripts/powershell/check-task-prerequisites.sh` 檢查 `plan.md` 與可用設計文件。
  - 依需求執行 `.specify/scripts/powershell/update-agent-context.sh [claude|gemini|copilot]` 同步根目錄 Agent 說明檔。
- 變更原則：最小且聚焦；遵循現有結構與命名，不任意搬移/重命名無關檔案。
- 互動原則：
  - 大量檔案寫入或結構變動前，先更新計畫並標示預期輸出位置。
  - 具風險操作（刪檔、大規模重構、依賴升級、網路與金鑰設定）需先徵求審批或提出替代方案。
- 驗證原則：
  - 優先執行與變更最相關之測試；再逐步擴至整體測試。
  - 若新增功能，務必補齊相應測試與文件（`docs/` 或 feature 目錄）。
- 工具鏈說明：上述 `scripts/*` 主要服務於 Gemini CLI 與 GitHub Copilot 的擴充流程；對應命令與提示位於 `.gemini/commands/` 與 `.github/prompts/`。其他代理可忽略工具鏈特定命令，但仍須遵循本檔原則與產出位置。

## 文件與紀錄
- 功能文件：於 `specs/<branch>/` 維護 `spec.md`、`plan.md`、必要的 `contracts/`、`data-model.md`、`quickstart.md`。
- 倘若引入跨領域契約或重大架構決策，請在 `docs/` 補充設計說明或 ADR（如採用）。
- 於 PR 描述中連結關聯規格與測試證據（日誌/截圖/指令輸出）。

## Commit 與 PR
- Commit：簡短祈使句，可加範圍（例：`orders: enable Kafka auto-provision`）；必要時註明產生工具（如 “by gemini cli”）。
- PR：說明動機、關聯 Issue、影響的服務/專案，並附證據（Scalar/Kafka/RabbitMQ 截圖或日誌）；使用 `.github/pull_request_template.md`。

## 常用腳本與指令速查
- 建立新功能（自動分支與規格骨架）：`scripts/create-new-feature.sh "描述"`
- 產生計畫骨架：`scripts/setup-plan.sh`
- 檢查計畫與附檔：`scripts/check-task-prerequisites.sh`
- 更新 Agent 說明檔：`scripts/update-agent-context.sh [claude|gemini|copilot]`
- 建置：`dotnet restore && dotnet build`
- 執行 API/Consumer：`dotnet run --project <csproj>`
- 本機整包：`docker-compose -f ./docker-compose/docker-compose.yml up -d`

## 安全與設定
- 使用環境變數或使用者密鑰，避免提交機敏資訊。常用 UI：Kafka `http://localhost:19000`、RabbitMQ `http://localhost:15672`（guest/guest，僅開發）。
 - 佈署/本機執行的 Broker 選擇：`QUEUE_SERVICE=Kafka|RabbitMQ`
 - 連線字串：`ConnectionStrings__KafkaBroker` 或 `ConnectionStrings__MessageBroker`（依所選 Broker）
