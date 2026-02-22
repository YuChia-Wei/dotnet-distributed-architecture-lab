# Building Blocks 類別索引（概念層）

這是 .NET 版 Building Blocks 的**概念設計**類別索引，描述完整架構的目標類別。
實際專案中已實作的類別請參考 [`.dev/BUILDING-BLOCKS-CLASS-INDEX.MD`](../.dev/BUILDING-BLOCKS-CLASS-INDEX.MD)。

> [!NOTE]
> 以下 namespace 為設計目標命名，實際套件完成後請更新。

## Domain Layer 核心類別

```
BuildingBlocks.Domain.DomainEntity<TId>        # 領域實體基底（Id + DomainEvents）
BuildingBlocks.Domain.AggregateRoot<TId>       # 聚合根基底（Version）
BuildingBlocks.Domain.EsAggregateRoot<TId>     # ES 聚合根（Apply/When 模式）
BuildingBlocks.Domain.IDomainEvent             # 領域事件介面（EventId + OccurredOn）
BuildingBlocks.Domain.IAggregateRoot<TId>      # 聚合根介面
BuildingBlocks.Domain.IDomainEntity<TId>       # 實體介面
BuildingBlocks.Domain.ValueObject              # Value Object 基底（設計目標）
BuildingBlocks.Domain.InternalDomainEvent      # 內部事件（設計目標）
BuildingBlocks.Domain.DomainEventTypeMapper    # 事件類型映射（設計目標）
```

## Use Case Layer 核心類別

```
BuildingBlocks.Application.Cqrs.Input
BuildingBlocks.Application.Cqrs.ExitCode
BuildingBlocks.Application.Cqrs.UseCaseFailureException
BuildingBlocks.Application.Cqrs.Command
BuildingBlocks.Application.Cqrs.CqrsOutput
```

## Repository Pattern 類別

```
BuildingBlocks.Domain.IDomainRepository<TEntity, TId>  # 領域 Repository 介面（FindByIdAsync/SaveAsync/DeleteAsync）
BuildingBlocks.Application.Repositories.IRepository    # 通用 Repository（設計目標）
BuildingBlocks.Application.Repositories.OutboxRepository
BuildingBlocks.Application.Repositories.IOutboxData
BuildingBlocks.Application.Repositories.IOutboxMapper
BuildingBlocks.Application.Repositories.IRepositoryPeer
BuildingBlocks.Application.Repositories.IStoreData
```

## Query Pattern 類別

```
BuildingBlocks.Application.Queries.IQuery
BuildingBlocks.Application.Queries.IProjection
BuildingBlocks.Application.Queries.IProjectionInput
BuildingBlocks.Application.Queries.IArchive
```

## Domain Event Data 類別

```
BuildingBlocks.Application.Events.DomainEventData
BuildingBlocks.Application.Events.DomainEventMapper
BuildingBlocks.Application.Events.ExternalDomainEvent
BuildingBlocks.Application.Events.ExternalDomainEventDto
BuildingBlocks.Application.Events.InternalDomainEventDto
```

## Messaging 類別

```
BuildingBlocks.Messaging.MessageProducer
BuildingBlocks.Messaging.PostEventFailureException
```

## Reactor Pattern 類別

```
BuildingBlocks.Application.Reactors.IReactor
BuildingBlocks.Application.Reactors.IGenericReactor
```

## Outbox Infrastructure 類別

```
BuildingBlocks.Infrastructure.Outbox.OutboxRepositoryPeer
BuildingBlocks.Infrastructure.Outbox.OutboxStore
BuildingBlocks.Infrastructure.Outbox.OutboxClient
BuildingBlocks.Infrastructure.Outbox.OutboxStoreAdapter
BuildingBlocks.Infrastructure.Outbox.EfCoreOutboxClient
BuildingBlocks.Infrastructure.Outbox.IOrmClient
```

## InMemory Infrastructure 類別

### Outbox InMemory 支援
```
BuildingBlocks.Infrastructure.Outbox.InMemoryOrmDb
BuildingBlocks.Infrastructure.Outbox.InMemoryOrmClient
```

### Event Store InMemory 支援
```
BuildingBlocks.Infrastructure.EventStore.InMemoryMessageDb
BuildingBlocks.Infrastructure.EventStore.InMemoryMessageDbClient
```

### Message Broker InMemory 支援
```
BuildingBlocks.Messaging.InMemoryMessageBroker
BuildingBlocks.Messaging.InMemoryMessageProducer
BuildingBlocks.Messaging.InMemoryProducer
BuildingBlocks.Messaging.InMemoryConsumer
BuildingBlocks.Messaging.InternalInMemoryMessageConsumer
BuildingBlocks.Messaging.ExternalInMemoryMessageConsumer
```

## Event Sourcing Infrastructure 類別

```
BuildingBlocks.Application.Repositories.EsRepository
BuildingBlocks.Application.Repositories.EventStoreData
BuildingBlocks.Application.Repositories.EventStoreMapper
BuildingBlocks.Infrastructure.EventStore.EsRepositoryPeer
BuildingBlocks.Infrastructure.EventStore.EventStore
BuildingBlocks.Infrastructure.EventStore.MessageDbClient
BuildingBlocks.Infrastructure.EventStore.MessageData
BuildingBlocks.Infrastructure.EventStore.CatchUpRelay
BuildingBlocks.Infrastructure.EventStore.VolatileRelay
BuildingBlocks.Infrastructure.EventStore.MessageDbToDomainEventDataConverter
```

## Testing Support 類別（BDDfy）

```
TestStack.BDDfy.BDDfyExtensions
TestStack.BDDfy.Xunit.BddfyFactAttribute
```

## Design by Contract 類別（uContract）

```
UContract.Contract
UContract.PreconditionViolationException
UContract.PostconditionViolationException
```

## Utility 類別

```
BuildingBlocks.Common.Converter
BuildingBlocks.Infrastructure.OptimisticLockingFailureException
```

## 使用說明

1. **查找類別**：使用 Ctrl+F 搜尋類別名稱
2. **確認 namespace**：複製完整路徑作為 using
3. **避免猜測**：若不存在，請回到 Building Blocks 專案確認

## 重要注意事項

### 概念 vs 實作
- 📘 此文件為**概念設計**索引，涵蓋完整架構目標
- 📗 已實作的類別請參考 `.dev/BUILDING-BLOCKS-CLASS-INDEX.MD`
- ✅ `BuildingBlocks.*` 為暫定命名，不代表最終套件

### 常見錯誤路徑（請避免）
- ❌ `DomainModel.*` → ✅ `BuildingBlocks.Domain.*`
- ❌ `Infrastructure.Common.*` → ✅ `BuildingBlocks.Infrastructure.*`
- ❌ `EventSourcingAggregate` → ✅ `EsAggregateRoot`

### Reactor 介面使用
```csharp
public interface MyReactor : IReactor<DomainEventData>
{
}
```

### InMemory Repository 配置範例（示意）
```csharp
public static IServiceCollection AddInMemoryRepositories(this IServiceCollection services)
{
    services.AddSingleton<InMemoryOrmDb<ProductData>>();
    services.AddSingleton<InMemoryMessageDb>();
    services.AddSingleton<InMemoryMessageDbClient>();
    return services;
}
```
