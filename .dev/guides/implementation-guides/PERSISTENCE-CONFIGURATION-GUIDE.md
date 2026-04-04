# Persistence Configuration Guide

本文件定義 ORM / persistence configuration 在 repo 中的建議落點與責任邊界。

## 核心規則

- `DbContext`
- EF Core configurations
- connection-string-oriented persistence setup
- migration-related persistence registration

都應放在：

- `Infrastructure/Persistence`

或其明確子區域，例如：

- `Infrastructure/Configuration/Persistence`

## Why

- ORM 屬於 persistence concern，不是 Web concern
- Web / API 層應只保留 transport、middleware、endpoint concern
- 將 persistence 配置集中在 Infrastructure，可避免層級語意混亂

## Recommended Placement

```text
<Domain>.Infrastructure/
  Persistence/
    <Domain>DbContext.cs
    Configurations/
    Migrations/
```

若專案規模需要更細分，可採：

```text
<Domain>.Infrastructure/
  Configuration/
    Persistence/
```

但不要把 DbContext / EF Core configuration 放回 WebApi 專案。

## Practical Rule

- WebApi:
  - host startup, middleware, controller, transport adapter
- Infrastructure/Persistence:
  - DbContext, EF Core mapping, persistence registration

## Related

- `../../standards/project-structure.md`
- `../../standards/coding-standards.md`
