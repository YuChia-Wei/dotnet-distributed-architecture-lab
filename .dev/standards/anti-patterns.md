# .NET DDD WolverineFx 反模式

## 概述

這份文件記錄在 .NET DDD + WolverineFx + EF Core 技術棧中應該避免的常見錯誤與反模式。

## 領域層反模式

### 1. ❌ Anemic Domain Model（貧血領域模型）
```csharp
// 錯誤：只有屬性，業務邏輯外移
public sealed class User
{
    public string Id { get; init; }
    public string Name { get; set; }
    public string Email { get; set; }
}

public sealed class UserService
{
    public void ChangeEmail(User user, string newEmail)
    {
        if (!Email.IsValid(newEmail))
        {
            throw new ArgumentException("Invalid email");
        }
        user.Email = newEmail;
    }
}
```

✅ **正確做法**：
```csharp
public sealed class User : AggregateRoot
{
    private UserId _id;
    private UserName _name;
    private Email _email;

    public void ChangeEmail(string newEmail)
    {
        Contract.Require("Email", () => newEmail is not null);
        var email = new Email(newEmail); // 驗證在 Value Object
        Apply(new UserEmailChanged(_id.Value, email.Value, DateProvider.Now()));
    }

    private void When(UserEmailChanged e)
    {
        _email = new Email(e.Email);
    }
}
```

### 2. ❌ 過大的 Aggregate
```csharp
// 錯誤：Company 內含大量集合
public sealed class Company
{
    public List<Employee> Employees { get; } = new();
    public List<Department> Departments { get; } = new();
    public List<Project> Projects { get; } = new();
}
```

✅ **正確做法**：
```csharp
public sealed class Company
{
    public CompanyId Id { get; init; }
    public CompanyName Name { get; init; }
}

public sealed class Employee
{
    public EmployeeId Id { get; init; }
    public CompanyId CompanyId { get; init; } // 以 ID 引用
}
```

### 3. ❌ 直接修改狀態
```csharp
// 錯誤：繞過事件直接修改
public void Complete()
{
    _status = TaskStatus.Completed;
    _completedAt = DateTime.UtcNow;
}
```

✅ **正確做法**：
```csharp
public void Complete()
{
    if (_status == TaskStatus.Completed)
    {
        throw new InvalidOperationException("Task already completed");
    }
    Apply(new TaskCompleted(_id.Value, DateProvider.Now()));
}

private void When(TaskCompleted e)
{
    _status = TaskStatus.Completed;
    _completedAt = e.CompletedAt;
}
```

## 應用層反模式

### 4. ❌ Use Case 中包含業務邏輯
```csharp
public sealed class CreateOrderHandler
{
    public Task<CqrsOutput> Handle(CreateOrderInput input)
    {
        // 錯誤：業務規則應該在 Domain
        if (input.Items.Count == 0)
            throw new BusinessException("Order must have items");
        // ...
        return Task.FromResult(CqrsOutput.Success());
    }
}
```

✅ **正確做法**：
```csharp
public sealed class CreateOrderHandler
{
    private readonly IRepository<Order, OrderId> _repository;

    public async Task<CqrsOutput> Handle(CreateOrderInput input)
    {
        var order = Order.Create(input.CustomerId, input.Items);
        await _repository.Save(order);
        return CqrsOutput.Success();
    }
}
```

### 5. ❌ 跨 Aggregate 事務
```csharp
// 錯誤：同一交易修改多個 Aggregate
public async Task TransferEmployee(string employeeId, string fromDeptId, string toDeptId)
{
    var employee = await _employeeRepo.FindById(employeeId);
    var fromDept = await _deptRepo.FindById(fromDeptId);
    var toDept = await _deptRepo.FindById(toDeptId);

    fromDept.RemoveEmployee(employee);
    toDept.AddEmployee(employee);
    employee.ChangeDepartment(toDeptId);

    await _deptRepo.Save(fromDept);
    await _deptRepo.Save(toDept);
    await _employeeRepo.Save(employee);
}
```

✅ **正確做法**：
```csharp
public async Task RequestTransfer(string employeeId, string toDeptId)
{
    var employee = await _employeeRepo.FindById(employeeId);
    employee.RequestTransfer(toDeptId);
    await _employeeRepo.Save(employee);
    // WolverineFx handler/reactor 負責跨 Aggregate 同步
}
```

## 持久化層反模式

### 6. ❌ 依賴 Lazy Loading
```csharp
// 錯誤：依賴 lazy loading 造成 Aggregate 不完整
public class PlanData
{
    public virtual ICollection<TaskData> Tasks { get; set; } // lazy
}
```

✅ **正確做法**：
- Aggregate 載入使用明確 Include 或完整載入
- 查詢使用 Projection/Read Model 以避免過載

### 7. ❌ Repository 添加自定義查詢方法
```csharp
// 錯誤：Repository 不得新增查詢方法
public interface IUserRepository : IRepository<User, UserId>
{
    IEnumerable<User> FindByEmail(string email);
    IEnumerable<User> FindActiveUsers();
}
```

✅ **正確做法**：
- Repository 僅保留 findById / save / delete
- 查詢用 Projection/Inquiry

### 8. ❌ Repository 包含業務邏輯
```csharp
public interface IUserRepository : IRepository<User, UserId>
{
    void DeactivateInactiveUsers(int days); // 業務規則
}
```

✅ **正確做法**：
將業務邏輯放在 Use Case/Domain，Repository 只做持久化。

## 測試反模式

### 9. ❌ 為每個 Repository 自建 InMemory 實作
```csharp
// 錯誤：手寫 InMemory Repo，容易不一致
public sealed class InMemoryPlanRepository : IPlanRepository
{
    private readonly Dictionary<string, Plan> _storage = new();
    public Task<Plan?> FindById(string id) => Task.FromResult(_storage.GetValueOrDefault(id));
    public Task Save(Plan plan) { _storage[plan.Id.Value] = plan; return Task.CompletedTask; }
}
```

✅ **正確做法**：
- 使用 EF Core InMemory/Sqlite provider + Outbox
- 或使用 Testcontainers + 真實 PostgreSQL
- 測試仍需遵守 Repository 三方法規則

### 10. ❌ 測試實現細節
```csharp
// 錯誤：測試私有欄位
Assert.True(ReflectionHelper.GetField(task, "_isCompleted"));
```

✅ **正確做法**：驗證行為與事件。

### 11. ❌ 過度 Mock
```csharp
// 錯誤：Mock 過多
var repo = Substitute.For<IRepository>();
var bus = Substitute.For<IMessageBus>();
var mapper = Substitute.For<IMapper>();
```

✅ **正確做法**：盡量使用真實組件或可控基礎設施（NSubstitute 只用於必要界面）。

## 架構反模式

### 12. ❌ 跳過架構層次
```csharp
// 錯誤：Controller 直接操作 Repository
[ApiController]
public sealed class UserController : ControllerBase
{
    private readonly IUserRepository _repository;

    [HttpGet("/users/{id}")]
    public async Task<User> Get(string id)
        => await _repository.FindById(id);
}
```

✅ **正確做法**：Controller → UseCase/Handler → Domain → Repository。

## 效能反模式

### 13. ❌ N+1 查詢
使用 Projection/Read Model 或 EF Core 的合理查詢策略避免 N+1。

### 14. ❌ 過度使用 Event Sourcing
查詢應使用 Projection，避免重播所有事件。

## 其他反模式

### 15. ❌ 直接使用系統時間 API
禁止在 Domain/Event 中直接使用 `DateTime.UtcNow`。

✅ **正確做法**：
```csharp
Apply(new PlanCreated(id, name, DateProvider.Now()));
```

### 16. ❌ 測試失敗時直接修改 BDD 規格
Gherkin 風格的情境命名代表業務規則，測試失敗時需先釐清原因並取得人類確認。

## 總結

避免反模式的關鍵：
1. 保持領域模型的豐富性
2. 遵守架構層次和一致性邊界
3. 正確使用 Event Sourcing 與 CQRS
4. 測試驗證行為而非實作細節
5. 使用可測試的時間來源（DateProvider/TimeProvider）
6. 尊重測試規格，失敗時先確認再修改
