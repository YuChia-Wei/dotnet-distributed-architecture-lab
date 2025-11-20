# 分散式架構練習專案

dotnet distributed architecture lab 是一個採用 .NET 10、容器化技術和現代軟體架構原則（如 Clean Architecture、DDD、CQRS）建構的範例專案。

此專案旨在展示如何利用 DDD 以及 Clean Architecture 、CQRS、Message Queue 等概念、技術建立一個分散式架構。

同時，有鑑於近年 AI Agent CLI 以及 Spec-Drive Development 的興起，也會利用此專案展示如何利用 Spec-kit 與 AI Agent CLI 合作完成此練習專案。

目前專案包含兩個核心業務領域：**訂單 (SaleOrders)** 和 **產品 (SaleProducts)**，並透過 RabbitMQ 或 Kafka 進行非同步通訊。

## 架構原則

本專案嚴格遵循以下架構原則：

- **Clean Architecture (CA):** 強制性的關注點分離和依賴規則，確保業務邏輯的獨立性。
- **Domain-Driven Design (DDD):** 專注於核心業務領域和領域邏輯。
- **Command Query Responsibility Segregation (CQRS):** 將讀取和寫入操作分離，以優化效能和可擴展性。

## 核心技術

- **主要框架:** .NET 9
- **主要語言:** C#
- **訊息/命令/查詢處理:** WolverineFx
- **資料庫:** PostgreSQL
- **訊息代理:** RabbitMQ / Kafka
- **容器化:** Docker

## 如何啟動專案

本專案已完全容器化，您只需要在本機安裝 Docker 和 Docker Compose 即可輕鬆啟動。

1.  **選擇訊息代理 (Message Broker)**

    在 `docker-compose/docker-compose.yml` 檔案中，您可以透過設定 `QUEUE_SERVICE` 環境變數來選擇要使用的訊息代理。

    - **使用 Kafka (預設):**
      ```yaml
      # 在 orders-api, orders-consumer, product-api, product-consumer 中
      environment:
        - QUEUE_SERVICE=Kafka
      ```

    - **使用 RabbitMQ:**
      將 `QUEUE_SERVICE` 的值改為 `RabbitMQ`。
      ```yaml
      # 在 orders-api, orders-consumer, product-api, product-consumer 中
      environment:
        - QUEUE_SERVICE=RabbitMQ
      ```

2.  **Clone 專案庫**
    ```bash
    git clone https://github.com/YuChia/dotnet-mq-arch-lab.git
    cd dotnet-mq-arch-lab
    ```

3.  **使用 Docker Compose 啟動所有服務**
    在專案根目錄下，執行以下指令：
    ```bash
    docker-compose -f ./docker-compose/docker-compose.yml up -d
    ```
    此指令將會建置並啟動所有必要的服務，包括：
    - `orders-api`
    - `orders-consumer`
    - `product-api`
    - `product-consumer`
    - `postgres`
    - `rabbitmq` (如果選擇 RabbitMQ)
    - `kafka` (如果選擇 Kafka)
    - `kafka-ui` (如果選擇 Kafka)

## OpenApi with Scalar

專案的 Web API 提供了基於 Scalar 的互動式 API 文件。當專案成功啟動後，您可以透過以下連結存取：

- **訂單服務 (Orders API):**
  - **API 文件:** [http://localhost:8080/scalar/v1](http://localhost:8080/scalar/v1)
  - **OpenAPI Spec:** [http://localhost:8080/openapi/v1](http://localhost:8080/openapi/v1)

- **產品服務 (Products API):**
  - **API 文件:** [http://localhost:8090/scalar/v1](http://localhost:8090/scalar/v1)
  - **OpenAPI Spec:** [http://localhost:8090/openapi/v1](http://localhost:8090/openapi/v1)

## 服務監控

- **Kafka UI:**
  當使用 Kafka 時，您可以透過 [http://localhost:8088](http://localhost:8088) 來存取 Kafka UI。

- **RabbitMQ Management UI:**
  當使用 RabbitMQ 時，您可以透過 [http://localhost:15672](http://localhost:15672) 來監控 RabbitMQ 的佇列和訊息。
  - **帳號:** `guest`
  - **密碼:** `guest`

## 目錄內容說明

### 專案結構

| 資料夾位置                           | 內容                                                                                          |
|---------------------------------|---------------------------------------------------------------------------------------------|
| ./.codex                        | codex cli 的資源                                                                               |
| ./.gemini                       | gemini cli 的資源                                                                              |
| ./.github                       | github & github copilot 的資源                                                                 |
| ./.specify                      | spec-kit 的語法腳本及 prompt 範本                                                                   |
| ./.specify/kit-command-prompts  | spec-kit 在各種 ai agents cli 中所使用的自訂 prompt 的備份文件，包含中譯檔案，用於研究 spec-kit 的運作邏輯                  |
| ./.specify/memory               | spec-kit 的規範文件 (constitution)                                                               |
| ./.specify/scripts              | spec-kit 使用的執行語法 (區分 bash 與 powershell)                                                     |
| ./.specify/templates            | spec-kit 使用的範本文件                                                                            |
| ./docker-compose                | docker compose 檔案與部署設定、資料                                                                   |
| ./docs                          | 說明文件與開發時額外想要記錄的議題資料                                                                         |
| ./https                         | 用於快速測試的 http 檔案                                                                             |
| ./https/<Context>               | <Context>領域的 web api 測試用 http 檔案                                                            |
| ./specs                         | 功能規格，Spec-driven development with AI 時產生的規格文件                                               |
| ./sql-script                    | 資料庫語法                                                                                       |
| ./src                           | dotnet 原始碼資料夾                                                                               |
| ./src/BC-Contracts              | 跨領域合約 (Message Queue 的傳遞物件)                                                                 |
| ./src/BuildingBlocks            | 系統所需的基礎框架                                                                                   |
| ./src/Shared                    | 通用領域的共用核心                                                                                   |
| ./src/<DomainName>              | <DomainName>領域                                                                              |
| ./src/<DomainName>/DomainCore   | <DomainName>領域的核心專案，包括但不限於領域物件層、應用層、基礎建設層等專案                                                |
| ./src/<DomainName>/Presentation | <DomainName>領域的展現層專案，包括但不限於 WebApi、Consumer                                                 |
| ./tests                         | 測試專案資料夾，包括但不限於「使用 Xunit 開發的 dotnet 測試專案」、「使用 k6 撰寫的 E2E 測試腳本」                               |

### 設計、筆記等文件紀錄

- 設計相關
  - [order / product 中的 command/command handler 做法比較](./docs/program-desighe/command-handler-comparison-of-practices.md)
  - [bc contracts 專案分類](./docs/program-desighe/bc-contracts.md)
- AI 協作紀錄 (AI Agent CLI 的對話輸出紀錄)
  - 功能 002 : order cancel
    - [使用 codex cli 進行實作的紀錄](./docs/SDD-ai-agent-history/feat-002/codex-chat-memo.md)
  - 功能 003 : product consumer order cancelled
    - [使用 gemini cli 執行 spec-kit 命令的紀錄](./docs/SDD-ai-agent-history/feat-003/spec-kit-gemini-cli-gen-history.md)
    - [使用 codex cli 進行實作的紀錄](./docs/SDD-ai-agent-history/feat-003/codex-cli-work-summary.md)

## AI Agents CLI 協作

:::info
本專案內包含各 prompt 的中文翻譯文件，可用於觀察 spec-kit 社群是如何建立相關 prompt
:::

- AI Agent CLI Default Context
  - Gemini CLI: `agents.md`
    - > 為了方便 gemini 與 codex 共用 default context，有額外於 `.gemini/settings.json` 中設定 `defaultContext`
  - GitHub Copilot: `.github/copilot-instructions.md`
  - Codex: `agents.md`
- AI Agent CLI Extension Commands
  - Gemini CLI：`.gemini/commands/`
  - GitHub Copilot：`.github/prompts/`
  - Codex: `.codex/prompts/`
    - > codex 需要利用 `setx CODEX_HOME '{project-floder}\.codex'` 語法來讓 codex 讀取到專案資料夾下的擴充命令
    - > 切換後需要重新登入 codex，且開發完畢需清除環境參數以避免後續工作目錄的錯亂
    - > 因此目前在 codex 中要使用 SDD 的擴充命令時會有諸多限制與需注意的部分

### Spec-Driven Development (規格驅動開發)

- [Spec-Kit](https://github.com/github/spec-kit)

#### agent cli commands

> 更新三種 AI Agent 的 spec kit 工具

```powershell
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai copilot --no-git --script sh
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai copilot --no-git --script ps
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai codex --no-git --script sh
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai codex --no-git --script ps
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai gemini --no-git --script sh
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai gemini --no-git --script ps
```

> agent cli 的完整擴充命令清單以及 cli 支援狀況以 spec-kit 官方文件為主

```terminaloutput
╭───────────────────────────────────────────────────────────────────── Agent Folder Security ──────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.                             │
│  Consider adding .github/ (or parts of it) to .gitignore to prevent accidental credential leakage.                                                               │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────────────── Next Steps ───────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  1. You're already in the project directory!                                                                                                                     │
│  2. Start using slash commands with your AI agent:                                                                                                               │
│     2.1 /speckit.constitution - Establish project principles                                                                                                     │
│     2.2 /speckit.specify - Create baseline specification                                                                                                         │
│     2.3 /speckit.plan - Create implementation plan                                                                                                               │
│     2.4 /speckit.tasks - Generate actionable tasks                                                                                                               │
│     2.5 /speckit.implement - Execute implementation                                                                                                              │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────────────────────────────────────────────── Enhancement Commands ──────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  Optional commands that you can use for your specs (improve quality & confidence)                                                                                │
│                                                                                                                                                                  │
│  ○ /speckit.clarify (optional) - Ask structured questions to de-risk ambiguous areas before planning (run before /speckit.plan if used)                          │
│  ○ /speckit.analyze (optional) - Cross-artifact consistency & alignment report (after /speckit.tasks, before /speckit.implement)                                 │
│  ○ /speckit.checklist (optional) - Generate quality checklists to validate requirements completeness, clarity, and consistency (after /speckit.plan)             │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

##### codex output

```terminaloutput

╭───────────────────────────────────────────────────────────────────── Agent Folder Security ──────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.                             │
│  Consider adding .codex/ (or parts of it) to .gitignore to prevent accidental credential leakage.                                                                │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────────────── Next Steps ───────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  1. You're already in the project directory!                                                                                                                     │
│  2. Set CODEX_HOME environment variable before running Codex: setx CODEX_HOME '.\dotnet-mq-arch-lab\.codex'                                       │
│  3. Start using slash commands with your AI agent:                                                                                                               │
│     2.1 /speckit.constitution - Establish project principles                                                                                                     │
│     2.2 /speckit.specify - Create baseline specification                                                                                                         │
│     2.3 /speckit.plan - Create implementation plan                                                                                                               │
│     2.4 /speckit.tasks - Generate actionable tasks                                                                                                               │
│     2.5 /speckit.implement - Execute implementation                                                                                                              │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────────────────────────────────────────────── Enhancement Commands ──────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                  │
│  Optional commands that you can use for your specs (improve quality & confidence)                                                                                │
│                                                                                                                                                                  │
│  ○ /speckit.clarify (optional) - Ask structured questions to de-risk ambiguous areas before planning (run before /speckit.plan if used)                          │
│  ○ /speckit.analyze (optional) - Cross-artifact consistency & alignment report (after /speckit.tasks, before /speckit.implement)                                 │
│  ○ /speckit.checklist (optional) - Generate quality checklists to validate requirements completeness, clarity, and consistency (after /speckit.plan)             │
│                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```