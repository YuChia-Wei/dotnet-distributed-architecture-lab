# Architecture

本文件提供專案架構全貌。詳細技術選型見 [TECH-STACK-REQUIREMENTS.MD](./requirement/TECH-STACK-REQUIREMENTS.MD)，專案結構見 [project-structure.md](./standards/project-structure.md)。

## Architecture Overview

### Core Architecture
- **Style**: Clean Architecture + DDD + CQRS
- **Patterns**: Outbox / InMemory / Event Sourcing（依 aggregate 設定）
- **Use Case 分類**：Command / Query / Reactor

### Code Organization (概念層級)
- **Domain**: Aggregates, Entities, Value Objects, Domain Events
- **Application**: Use Cases（Command/Query/Reactor ports）
- **Infrastructure**: Repository / ORM / Messaging / Integration
- **Adapter**: REST API Controllers, DTOs

完整專案結構與命名規則：[project-structure.md](./standards/project-structure.md)

詞彙與責任邊界：

- `Use Case`、`Command`、`Query`、`Handler`、`Application Service` 的關係見 [USECASE-COMMAND-HANDLER-RELATIONSHIP.MD](./standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD)

### Architecture Config Driven
本專案的 command-sub-agent 會依照 [`project-config.yaml`](./project-config.yaml) 的 `architecture` 區塊自動產生對應結構：
- 依 aggregate 設定選擇 Outbox / InMemory / Event Sourcing
- 依 `commandDefaults.dualProfileSupport` 產生雙 Profile 配置
- repository / mapper / data model 產生邏輯由 config 控制
