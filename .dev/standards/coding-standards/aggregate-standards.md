# Aggregate 編碼規範 (.NET)

本文件定義 Aggregate、Entity、Value Object 和 Domain Event 的編碼標準。

---

## 📌 概述

Aggregate 是 DDD 的核心模型，需遵循 Event Sourcing / Invariant 維護的規範。

- **Aggregate Root** 是唯一對外修改入口
- **狀態變更**透過 Domain Event 記錄
- **不可變性**：Value Objects 必須是 immutable
- **交易邊界**：一個 Command 只能修改一個 Aggregate

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# Aggregate Root 規則
Pattern (required): Apply\(
Pattern (required): protected override void When
Pattern (required): Ensure\.|Contract\.|Guard\.
Pattern (required): IsDeleted

# 禁止規則
Pattern (forbidden, ignore-comment): DbContext
Pattern (forbidden): new .*Service\(
```

---

## ⚠️ 關鍵警告：集合欄位初始化時機

**問題**: 在建構子中於 `base()` 之後初始化集合欄位會導致事件重播的資料被清空！

```csharp
// ❌ 絕對錯誤：會清空事件重播的資料
public class ScrumTeam : AggregateRoot<ScrumTeamId>
{
    private readonly List<TeamMember> _members;
    
    public ScrumTeam(IEnumerable<IDomainEvent> domainEvents) : base(domainEvents)
    {
        _members = new List<TeamMember>();  // 錯誤！清空了剛重播的資料
    }
}

// ✅ 正確：在欄位宣告時初始化
public class ScrumTeam : AggregateRoot<ScrumTeamId>
{
    private readonly List<TeamMember> _members = new();  // 正確初始化時機
    
    public ScrumTeam(IEnumerable<IDomainEvent> domainEvents) : base(domainEvents)
    {
        // _members 已經存在，事件重播不會被清空
    }
}
```

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 0. Soft Delete 欄位要求

**強制規定**: 每個 Aggregate 必須支援軟刪除功能：

#### Aggregate Root 必須有 IsDeleted 欄位和方法

```csharp
// ✅ 正確：Aggregate Root 必須實作 IsDeleted
public class ProductBacklogItem : AggregateRoot<PbiId>
{
    public bool IsDeleted { get; private set; }  // 必須欄位：軟刪除標記
    
    // 在處理刪除事件時設置 IsDeleted = true
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case ProductBacklogItemDeleted e:
                IsDeleted = true;  // 標記為已刪除
                break;
            // 其他事件處理...
        }
    }
}
```

---

### 1. Aggregate Command Method 後置條件檢查

**強制規定**: 每個 Aggregate 的 command method 必須使用 Guard Clauses 或 Contracts 檢查：
1. 業務狀態變更的正確性
2. Domain Event 產生的正確性

```csharp
// ✅ 正確：完整的後置條件檢查
public void CreateTask(TaskId taskId, string name, int? estimatedHours, string creatorId)
{
    // 前置條件
    ArgumentNullException.ThrowIfNull(taskId);
    ArgumentException.ThrowIfNullOrEmpty(name);
    
    // Apply domain event
    Apply(new TaskCreated(Id, taskId, name, estimatedHours, creatorId, DateTime.UtcNow));
    
    // 後置條件：檢查業務狀態
    var createdTask = _tasks.FirstOrDefault(t => t.Id.Equals(taskId));
    
    Contract.Ensure(createdTask is not null, "Task must be created");
    Contract.Ensure(createdTask!.Id.Equals(taskId), "Task ID must be set");
    Contract.Ensure(createdTask.Name == name, "Task name must be set");
    Contract.Ensure(createdTask.State == TaskState.Todo, "Task initial state must be TODO");
    
    // 後置條件：檢查 Domain Event 正確性
    var lastEvent = GetLastDomainEvent();
    Contract.Ensure(
        lastEvent is TaskCreated created && 
        created.TaskId.Equals(taskId) && 
        created.Name == name,
        "TaskCreated event must be generated correctly"
    );
}
```

---

### 2. 驗證方法選擇規則

| 元件類型 | 驗證方法 | 說明 |
|---------|---------|------|
| Aggregate Root | Guard Clauses + Contracts | `Contract.Require()`, `Contract.Ensure()` |
| Entity | `ArgumentNullException.ThrowIfNull` | 標準 .NET 7+ 方法 |
| Value Object | `ArgumentNullException.ThrowIfNull` | 標準 .NET 7+ 方法 |
| Domain Event | `ArgumentNullException.ThrowIfNull` | 在 record 建構子中驗證 |

---

## 🎯 Aggregate Root 設計原則

### 1. 繼承規則

```csharp
// ✅ Event Sourcing Aggregate
public class Product : AggregateRoot<ProductId>
{
    // 必須實作的方法：
    protected override void When(IDomainEvent @event) { ... }
    
    // 屬性
    public ProductId Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public ProductState State { get; private set; }
    public bool IsDeleted { get; private set; }
}
```

### 2. 建構子設計

```csharp
// ✅ 正確：提供兩個建構子
public class Product : AggregateRoot<ProductId>
{
    private readonly List<Task> _tasks = new();  // 在欄位宣告時初始化！
    
    // 用於 Event Sourcing 重建的建構子
    public Product(IEnumerable<IDomainEvent> events) : base(events)
    {
    }
    
    // 用於創建新實例的公開建構子
    public Product(ProductId id, string name, string creatorId)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentException.ThrowIfNullOrEmpty(name);
        ArgumentException.ThrowIfNullOrEmpty(creatorId);
        
        Apply(new ProductCreated(id, name, creatorId, DateTime.UtcNow));
        
        // 後置條件
        Contract.Ensure(Id.Equals(id), "ID must be set");
        Contract.Ensure(Name == name, "Name must be set");
    }
}

// ❌ 錯誤：使用 static factory method
public static Product Create(ProductId id, string name)
{
    // 不要使用 static factory method
}
```

### 3. Command Method 模式

```csharp
public void Rename(string newName)
{
    // 1. 前置條件檢查
    ArgumentException.ThrowIfNullOrEmpty(newName);
    Contract.Require(!IsDeleted, "Cannot rename deleted product");
    
    // 2. 避免不必要的 event（可選）
    if (Name == newName)
        return;  // 無需更新，不產生 event
    
    // 3. 發布事件
    Apply(new ProductRenamed(Id, newName, DateTime.UtcNow));
    
    // 4. 後置條件檢查
    Contract.Ensure(Name == newName, "Name must be updated");
    Contract.Ensure(
        GetLastDomainEvent() is ProductRenamed,
        "ProductRenamed event must be generated"
    );
}
```

---

## 🎯 Value Object 設計原則

### 1. 基本結構

```csharp
// ✅ 使用 record（推薦）
public sealed record ProductId(string Value)
{
    public ProductId() : this(Guid.NewGuid().ToString()) { }
    
    public static ProductId Create() => new();
    public static ProductId From(string value) => new(value);
    
    // 在建構子中驗證
    public ProductId
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
    }
}

// ✅ 使用 record struct（輕量級）
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Currency mismatch");
        return this with { Amount = Amount + other.Amount };
    }
}
```

### 2. 不可變性原則

```csharp
// ✅ 正確：返回新實例
public Money Add(Money other)
{
    if (Currency != other.Currency)
        throw new InvalidOperationException("Currency mismatch");
    return this with { Amount = Amount + other.Amount };
}

// ❌ 錯誤：修改內部狀態（不可能在 record 中發生，但 class 需注意）
public void Add(Money other)
{
    Amount = Amount + other.Amount;  // 違反不可變性！
}
```

### 3. 約束驗證（Constraint Validation）

Value Object 應在建構時驗證所有業務約束，確保不可能存在無效狀態的實例。

```csharp
// ✅ 正確：在建構子中封裝範圍、長度、格式約束
public sealed record Quantity(int Value)
{
    public Quantity
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(Value);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(Value, 10_000);
    }
}

public sealed record ProductName(string Value)
{
    public ProductName
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
        if (Value.Length > 200)
            throw new ArgumentOutOfRangeException(nameof(Value), "產品名稱不得超過 200 字元");
    }
}

public sealed record Email(string Value)
{
    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    public Email
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
        if (!EmailRegex.IsMatch(Value))
            throw new ArgumentException("無效的 Email 格式", nameof(Value));
    }

    public static Email From(string value) => new(value);
}

// ✅ 複合約束：多屬性一起驗證
public sealed record DateRange(DateTime Start, DateTime End)
{
    public DateRange
    {
        if (End <= Start)
            throw new ArgumentException("結束日期必須晚於起始日期");
    }

    public TimeSpan Duration => End - Start;
}
```

```csharp
// ❌ 錯誤：將約束驗證放在外部（Application Layer 或 Entity）
public class PlaceOrderHandler
{
    public void Handle(int quantity)
    {
        if (quantity <= 0 || quantity > 10_000)  // 約束應由 VO 封裝！
            throw new ArgumentException();

        var q = new Quantity(quantity);  // VO 沒有自我保護
    }
}
```

> **原則**：若某個值有業務約束（範圍、長度、格式、規則），應提取為 Value Object 並在建構時驗證。
> 這樣無論在何處使用，都能保證值的有效性（Make Illegal States Unrepresentable）。

---

## 🎯 Domain Event 設計規範

### 1. Event 結構

```csharp
// ✅ 正確：使用 sealed record
public sealed record ProductCreated(
    ProductId ProductId,
    string Name,
    string CreatorId,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}

public sealed record ProductRenamed(
    ProductId ProductId,
    string NewName,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}

public sealed record ProductDeleted(
    ProductId ProductId,
    string DeletedBy,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}
```

### 2. Event Handler

```csharp
// ✅ 正確：在 When() 方法中處理事件
protected override void When(IDomainEvent @event)
{
    switch (@event)
    {
        case ProductCreated e:
            Id = e.ProductId;
            Name = e.Name;
            State = ProductState.Active;
            IsDeleted = false;
            break;
            
        case ProductRenamed e:
            Name = e.NewName;
            break;
            
        case ProductDeleted e:
            State = ProductState.Deleted;
            IsDeleted = true;
            break;
    }
}

// ❌ 錯誤：在 Event Handler 中包含業務邏輯
protected override void When(IDomainEvent @event)
{
    switch (@event)
    {
        case TaskAdded e:
            _tasks.Add(e.Task);
            // 錯誤：業務邏輯不應在 Event Handler 中！
            if (_tasks.Count > MaxTasks)
                throw new BusinessException("Too many tasks");
            break;
    }
}
```

---

## 🎯 Entity vs Value Object 選擇

### 選擇 Entity 當：
- 需要唯一標識符
- 有生命週期
- 狀態會改變
- 例如：Task, Sprint, User

### 選擇 Value Object 當：
- 通過屬性值識別
- 不可變
- 可替換
- 例如：ProductId, Money, DateRange

---

## 🔍 檢查清單

### Aggregate Root
- [ ] 繼承 `AggregateRoot<TId>`
- [ ] 提供 Event Sourcing 重建建構子
- [ ] 提供公開建構子（非 static factory）
- [ ] 實作 `protected override void When(IDomainEvent @event)`
- [ ] 有 `IsDeleted` 欄位支援軟刪除
- [ ] Command method 有前置條件檢查
- [ ] Command method 有後置條件檢查
- [ ] 正確發布 Domain Event (Apply)
- [ ] 集合欄位在宣告時初始化

### Value Object
- [ ] 使用 `record` 或 `record struct`
- [ ] 不可變
- [ ] 有建構子驗證邏輯
- [ ] 使用 `ArgumentNullException.ThrowIfNull`

### Domain Event
- [ ] 使用 `sealed record`
- [ ] 實作 `IDomainEvent`
- [ ] 包含必要的 Aggregate ID
- [ ] 包含 `OccurredOn` (DateTime)
- [ ] 包含 `EventId` (Guid)

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| Aggregate 範例 | [../examples/aggregate/](../examples/aggregate/) |
| Domain Events | [../examples/aggregate/PlanEvents.cs](../examples/aggregate/PlanEvents.cs) |
| Value Objects | [../examples/aggregate/PlanId.cs](../examples/aggregate/PlanId.cs) |
| Outbox + Data 範例 | [../examples/outbox/](../examples/outbox/) |

---

## 相關文件

- [usecase-standards.md](usecase-standards.md)
- [mapper-standards.md](mapper-standards.md)
- [repository-standards.md](repository-standards.md)
- [test-standards.md](test-standards.md)
