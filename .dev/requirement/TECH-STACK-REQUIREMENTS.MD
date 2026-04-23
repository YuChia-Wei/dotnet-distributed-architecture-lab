# .NET Tech Stack Requirements

本文件定義 .NET 專案的技術選型與對應 canonical docs。

| Area | Choice | Version | Canonical Source |
| --- | --- | --- | --- |
| Language/Runtime | C# 14 / .NET | 10.0 | `.dev/ARCHITECTURE.MD` |
| ORM (Write) | Dapper + Npgsql | Dapper 2.1.66 / Npgsql 10.0.1 | `.dev/ARCHITECTURE.MD` |
| ORM (Read/Projection) | EF Core | 10.x | `.dev/guides/implementation-guides/PERSISTENCE-CONFIGURATION-GUIDE.md` |
| Messaging | WolverineFx + RabbitMQ + Kafka | WolverineFx 5.16.2 | `.dev/ARCHITECTURE.MD` |
| Database | PostgreSQL | 16 | `.dev/ARCHITECTURE.MD` |
| Testing Framework | xUnit | 2.9.3 | [PROFILE-BASED-TESTING-GUIDE.md](../guides/design-guides/PROFILE-BASED-TESTING-GUIDE.md) |
| BDD (Planned) | BDDfy (Gherkin-style naming) | (TBD) | [profile-based-testing-rationale.MD](../standards/rationale/profile-based-testing-rationale.MD) |
| Mocking | NSubstitute | 5.3.0 | `.dev/ARCHITECTURE.MD` |
| Mutation Testing | Stryker.NET | (TBD) | `.dev/standards/coding-standards.md` |
| Web API Host | ASP.NET Core | (同 .NET 版本) | `.dev/ARCHITECTURE.MD` |
| Queue Consumer Host | Console App (.NET Generic Host) | (同 .NET 版本) | `.dev/ARCHITECTURE.MD` |

## ORM 使用策略

本專案採用 **Dapper + EF Core 混用策略**：

| 場景 | 選擇 | 理由 |
| --- | --- | --- |
| Command (Write) | Dapper + Npgsql | 精確控制 SQL、效能最佳化 |
| Query (Read/Projection) | EF Core | 快速開發、Projection 支援 |
| Complex Query | Dapper | 複雜 SQL、效能關鍵查詢 |

> Note: 若後續需要補充選型理由，請直接更新對應 standards / guides / architecture docs，不再新增 ADR 檔。

## 部署平台

所有產出成品（Artifacts）除非特別指示，否則**一律以 Docker 容器化方式發佈**，目標運行環境為 **Linux**。

| 項目 | 說明 |
| --- | --- |
| 運行環境 | Linux Container (Docker) |
| Base Image | 使用官方 .NET Runtime / ASP.NET Core Runtime image |
| 跨平台要求 | 所有使用的 NuGet 套件必須支援跨平台，**禁止使用 Windows 限定套件** |
| 注意事項 | 檔案路徑請使用 `Path.Combine()` 而非硬編碼分隔符號；避免使用 Windows Registry 等平台特定 API |
