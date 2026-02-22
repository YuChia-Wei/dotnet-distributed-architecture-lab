# ADR-019: Outbox Pattern Implementation (.NET)

## 狀態
已實施 (Implemented)

## 日期
2025-08-23

## 背景 (Context)
專案需要可靠的事件發布機制，確保領域事件與業務資料在同一交易提交。Outbox Pattern 是解決「雙寫問題」的標準方案。

## 決策 (Decision)
在 .NET 使用 **WolverineFx Outbox + EF Core + PostgreSQL** 實作 Outbox Pattern。

## 實作架構

### 1. 核心組件結構（範例）
```
[Aggregate]
  ├── Domain/
  ├── Application/
  │   └── UseCases/Ports/Out/
  │       └── [Aggregate]Data.cs      # EF Core data model (IOutboxData)
  ├── Application/
  │   └── UseCases/Ports/
  │       └── [Aggregate]Mapper.cs    # 含 IOutboxMapper 內部實作
  └── Infrastructure/
      ├── Persistence/
      │   └── [Aggregate]DbContext.cs
      └── Messaging/
          └── WolverineOutboxConfig.cs
```

### 2. 關鍵實作步驟

#### Step 1: 建立 Data 類別（EF Core）
每個 Aggregate 需要對應的 Data 類別，實作 `IOutboxData<string>`（BuildingBlocks 介面）：

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("[aggregate]")]
public class [Aggregate]Data : IOutboxData<string>
{
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string? StreamName { get; set; }

    [Key]
    public string [aggregate]Id { get; set; } = default!;

    [ConcurrencyCheck]
    public long Version { get; set; }

    public string GetId() => [aggregate]Id;
}
```

#### Step 2: 實作 Mapper 類別（含內部 OutboxMapper）
```csharp
public static class [Aggregate]Mapper
{
    public static IOutboxMapper<[Aggregate], [Aggregate]Data> NewMapper() => new Mapper();

    public static [Aggregate]Data ToData([Aggregate] aggregate)
    {
        var data = new [Aggregate]Data();
        data.DomainEventDatas = aggregate.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList();
        data.StreamName = aggregate.StreamName;
        return data;
    }

    public static [Aggregate] ToDomain([Aggregate]Data data)
    {
        if (data.DomainEventDatas is { Count: > 0 })
        {
            var domainEvents = data.DomainEventDatas
                .Select(DomainEventMapper.ToDomain)
                .Cast<[Aggregate]Events>()
                .ToList();
            var aggregate = new [Aggregate](domainEvents);
            aggregate.SetVersion(data.Version);
            aggregate.ClearDomainEvents();
            return aggregate;
        }

        // fallback: rebuild from current state
        return new [Aggregate](data);
    }

    private sealed class Mapper : IOutboxMapper<[Aggregate], [Aggregate]Data>
    {
        public [Aggregate] ToDomain([Aggregate]Data data) => [Aggregate]Mapper.ToDomain(data);
        public [Aggregate]Data ToData([Aggregate] aggregate) => [Aggregate]Mapper.ToData(aggregate);
    }
}
```

#### Step 3: 設定 EF Core + Wolverine Outbox
```csharp
services.AddDbContext<[Aggregate]DbContext>(options =>
    options.UseNpgsql(connectionString));

services.AddWolverine(opts =>
{
    opts.PersistMessagesWithEntityFrameworkCore<[Aggregate]DbContext>();
    opts.UseEntityFrameworkCorePersistence<[Aggregate]DbContext>();
    opts.UsePostgresqlOutbox(connectionString);
});
```

#### Step 4: Repository 設定
```csharp
services.AddScoped<IRepository<[Aggregate], [Aggregate]Id>>(
    _ => new OutboxRepository<[Aggregate], [Aggregate]Id>(
        outboxStore, [Aggregate]Mapper.NewMapper()));
```

## 重要注意事項

### 1. 必須遵守的規範
- ❗ **[NotMapped]**：`DomainEventDatas` 與 `StreamName` 必須是 EF Core 不持久化欄位。
- ❗ **內部 Mapper**：OutboxMapper 必須是 Mapper 的內部類別（避免散落規則）。
- ❗ **版本控制**：使用 `ConcurrencyCheck` 或 `RowVersion`，確保樂觀鎖一致。

### 2. 版本號處理
新建立 aggregate 版本號從 0 開始是正常的：
```csharp
Assert.True(aggregate.Version >= 0);
```

### 3. Profile / Environment 啟用策略
- 開發環境：InMemory Repository
- 測試環境：Outbox + PostgreSQL
- 生產環境：Outbox + Production 設定

使用 `appsettings.{Environment}.json` 控制切換。

### 4. 測試策略（xUnit + BDDfy）
每個 OutboxRepository **必須**有完整整合測試：
1. 資料持久化測試
2. 資料讀取測試
3. 軟刪除測試（以 `Save` 表示）
4. 版本控制測試

```csharp
[TestClass]
public class [Aggregate]OutboxRepositoryTests
{
    [Fact]
    public void should_persist_and_reload_aggregate_outbox()
    {
        this.Given(...).When(...).Then(...).BDDfy();
    }
}
```

### 5. 測試配置範例
```json
// appsettings.TestOutbox.json
{
  "ConnectionStrings": {
    "MessageStore": "Host=localhost;Port=5800;Database=board;Username=postgres;Password=root"
  }
}
```

## 效益 (Consequences)
- ✅ 交易一致性
- ✅ 可靠事件發布
- ✅ 可觀測性與審計
- ✅ 冪等支援
- ⚠️ 組件與測試成本提高
- ⚠️ Outbox 表需要清理策略

## 參考資料
- `.dev/standards/examples/outbox/README.md`

