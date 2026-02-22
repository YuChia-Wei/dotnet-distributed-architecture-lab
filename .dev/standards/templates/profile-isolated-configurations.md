# Profile 隔離配置模板集 (.NET)

## 目的
提供完整的 .NET DI/配置範本，實現 InMemory 與 Outbox Profile 完全隔離，避免配置衝突。

## 🚨 重要概念 (ezapp 2.0.0 對應)
ezDDD/ezapp 的 InMemory/Outbox 兩套 Repository 概念在 .NET 需保留，
目前 .NET 需以自建介面與組態實作對應功能（請以 TODO 保留概念）。

## 📁 建議的配置結構

```
src/Infrastructure/Configuration/
├── CommonConfiguration.cs        # 所有 Profile 共用
├── InMemory/
│   ├── InMemoryConfiguration.cs
│   └── InMemoryProjectionConfig.cs
└── Outbox/
    ├── OutboxInfrastructureConfig.cs
    ├── OutboxRepositoryConfig.cs
    └── OutboxProjectionConfig.cs
```

## 1️⃣ CommonConfiguration（所有 Profile 共用）

```csharp
public static class CommonConfiguration
{
    public static IServiceCollection AddCommonServices(
        this IServiceCollection services)
    {
        services.AddScoped<CreateProductHandler>();
        services.AddScoped<GetProductsHandler>();
        return services;
    }
}
```

## 2️⃣ InMemory Profile 配置

```csharp
public static class InMemoryConfiguration
{
    public static IServiceCollection AddInMemory(
        this IServiceCollection services, IConfiguration config)
    {
        // TODO: InMemory Outbox repository + message storage
        services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("app"));
        return services;
    }
}
```

## 3️⃣ Outbox Profile 配置

```csharp
public static class OutboxConfiguration
{
    public static IServiceCollection AddOutbox(
        this IServiceCollection services, IConfiguration config)
    {
        var conn = config.GetConnectionString("MainDb");
        services.AddDbContext<AppDbContext>(o => o.UseNpgsql(conn));
        // TODO: WolverineFx outbox + message persistence
        return services;
    }
}
```

## 4️⃣ 使用方式

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCommonServices();

var mode = builder.Configuration["Profiles:Mode"];
if (mode == "InMemory")
{
    builder.Services.AddInMemory(builder.Configuration);
}
else if (mode == "Outbox")
{
    builder.Services.AddOutbox(builder.Configuration);
}
```

## ⚠️ 重要提醒
- InMemory / Outbox 必須隔離組態與 DI 註冊
- Repository 介面一致（findById / save / delete）
- WolverineFx / Outbox 需保留語意與事件流程
