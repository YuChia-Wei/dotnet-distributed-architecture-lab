# .NET Tech Stack Requirements

本文件定義 .NET 專案的技術選型，並提供對應 ADR 連結（如適用）。

| Area | Choice | Version | ADR |
| --- | --- | --- | --- |
| Language/Runtime | C# 14 / .NET | 10.0 | N/A |
| ORM (Write) | Dapper + Npgsql | Dapper 2.1.66 / Npgsql 10.0.1 | N/A |
| ORM (Read/Projection) | EF Core | 10.x | [ADR-002](../adr/ADR-002-orm-config-location.md) |
| Messaging | WolverineFx + RabbitMQ + Kafka | WolverineFx 5.16.2 | [ADR-019](../adr/ADR-019-outbox-pattern-implementation.md) |
| Database | PostgreSQL | 16 | [ADR-019](../adr/ADR-019-outbox-pattern-implementation.md) |
| Testing Framework | xUnit | 2.9.3 | [ADR-021](../adr/ADR-021-profile-based-testing-architecture.md) |
| BDD (Planned) | BDDfy (Gherkin-style naming) | (TBD) | [ADR-021](../adr/ADR-021-profile-based-testing-architecture.md) |
| Mocking | NSubstitute | 5.3.0 | N/A |
| Mutation Testing | Stryker.NET | (TBD) | [ADR-025](../adr/ADR-025-mutation-testing-ucontract-exclusion.md) |
| Web API Host | ASP.NET Core | (同 .NET 版本) | N/A |
| Queue Consumer Host | Console App (.NET Generic Host) | (同 .NET 版本) | N/A |

## ORM 使用策略

本專案採用 **Dapper + EF Core 混用策略**：

| 場景 | 選擇 | 理由 |
| --- | --- | --- |
| Command (Write) | Dapper + Npgsql | 精確控制 SQL、效能最佳化 |
| Query (Read/Projection) | EF Core | 快速開發、Projection 支援 |
| Complex Query | Dapper | 複雜 SQL、效能關鍵查詢 |

> Note: 未有 ADR 的選型，後續如需固定版本或理由，請新增對應 ADR。

## 部署平台

所有產出成品（Artifacts）除非特別指示，否則**一律以 Docker 容器化方式發佈**，目標運行環境為 **Linux**。

| 項目 | 說明 |
| --- | --- |
| 運行環境 | Linux Container (Docker) |
| Base Image | 使用官方 .NET Runtime / ASP.NET Core Runtime image |
| 跨平台要求 | 所有使用的 NuGet 套件必須支援跨平台，**禁止使用 Windows 限定套件** |
| 注意事項 | 檔案路徑請使用 `Path.Combine()` 而非硬編碼分隔符號；避免使用 Windows Registry 等平台特定 API |
