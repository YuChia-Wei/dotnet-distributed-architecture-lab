# .NET DDD WolverineFx 最佳實踐

## 概述

本文件總結在 .NET DDD + WolverineFx + EF Core 技術棧中應遵守的最佳實踐。

## 領域建模最佳實踐

### 1. ✅ 小而聚焦的 Aggregate
```csharp
public sealed class Plan : AggregateRoot
{
    private PlanId _id;
    private PlanName _name;
    private UserId _ownerId;
    private readonly List<Project> _projects = new();

    public ProjectId CreateProject(string name)
    {
        Contract.Require("Project name", () => name is not null);
        var projectId = ProjectId.New();
        Apply(new ProjectCreated(_id.Value, projectId.Value, name));
        return projectId;
    }
}
```

### 2. ✅ 豐富的 Value Object
```csharp
public sealed record Email
{
    public string Value { get; }

    public Email(string value)
    {
        Contract.Require("Email", () => value is not null);
        if (!IsValid(value))
        {
            throw new ArgumentException("Invalid email format", nameof(value));
        }
        Value = value.ToLowerInvariant();
    }

    private static bool IsValid(string email)
        => Regex.IsMatch(email, "^[A-Za-z0-9+_.-]+@(.+)$");
}
```

### 3. ✅ 明確的領域事件
```csharp
public static class PlanEvents
{
    public sealed record TaskMovedToProject(
        string PlanId,
        string TaskId,
        string FromProjectId,
        string ToProjectId,
        IDictionary<string, string> Metadata
    ) : IDomainEvent;
}
```

## 應用層最佳實踐

### 4. ✅ 薄的 Use Case 層
```csharp
public sealed class CreatePlanHandler
{
    private readonly IRepository<Plan, PlanId> _repository;

    public async Task<CqrsOutput<PlanDto>> Handle(CreatePlanInput input)
    {
        var plan = new Plan(PlanId.New(), input.Name, input.UserId);
        await _repository.Save(plan);
        return CqrsOutput.Of(PlanMapper.ToDto(plan));
    }
}
```

### 5. ✅ 清晰的輸入輸出 DTO
```csharp
public sealed record CreateTaskInput(
    string PlanId,
    string ProjectId,
    string TaskName,
    string Description,
    DateOnly? Deadline);
```

### 6. ✅ 使用 Reactor/Handler 處理跨 Aggregate
```csharp
public sealed class UnassignTaskWhenTagDeleted
{
    private readonly IFindPlansByTagIdInquiry _inquiry;
    private readonly IRepository<Plan, PlanId> _planRepository;

    public async Task Handle(TagDeleted e)
    {
        var planIds = await _inquiry.FindByTagId(e.TagId);
        foreach (var planId in planIds)
        {
            var plan = await _planRepository.FindById(planId);
            if (plan is null) continue;
            plan.RemoveTagFromAllTasks(e.TagId, e.UserId);
            await _planRepository.Save(plan);
        }
    }
}
```

## 測試最佳實踐

### 7. ✅ BDD 風格的測試
```gherkin
Feature: Create Plan
  Scenario: Successfully create a plan
    Given a valid plan input
    When the create plan use case is executed
    Then a new plan should be created
```

```csharp
public sealed class CreatePlanSteps
{
    [Given(@"a valid plan input")]
    public void GivenValidInput() { /* ... */ }
}
```

### 8. ✅ 使用 Test Data Builder
```csharp
public sealed class PlanTestDataBuilder
{
    private string _name = "Default Plan";
    private string _userId = "user123";

    public static PlanTestDataBuilder APlan() => new();
    public PlanTestDataBuilder WithName(string name) { _name = name; return this; }
    public Plan Build() => new(PlanId.New(), _name, _userId);
}
```

## 持久化最佳實踐

### 9. ✅ 嚴格遵守 Repository 限制規則
- Repository 只允許 findById / save / delete
- 查詢使用 Projection/Inquiry

### 10. ✅ 明確的數據映射
```csharp
public static class PlanMapper
{
    public static PlanData ToData(Plan plan) => new()
    {
        Id = plan.Id.Value,
        Name = plan.Name.Value
    };

    public static PlanDto ToDto(Plan plan) => new(plan.Id.Value, plan.Name.Value);
}
```

### 11. ✅ 使用 Projection 優化查詢
```csharp
public sealed class PlanSummaryProjection
{
    private readonly DbContext _db;

    public Task<List<PlanSummaryDto>> Query(string userId)
        => _db.Set<PlanData>()
            .Where(p => p.UserId == userId)
            .Select(p => new PlanSummaryDto(p.Id, p.Name))
            .AsNoTracking()
            .ToListAsync();
}
```

## 架構最佳實踐

### 12. ✅ 依賴注入使用建構子
使用 constructor injection，避免 Service Locator。

### 13. ✅ 使用 DateProvider / TimeProvider 產生時間戳記
所有 Domain Events 使用可測試的時間來源。

### 14. ✅ 統一的錯誤處理
使用 `ProblemDetails` 或全域例外處理中介軟體。

## 效能最佳實踐

### 15. ✅ 合理使用快取
使用 `IMemoryCache` 或分散式快取處理熱資料。

### 16. ✅ 批量操作優化
必要時以批量查詢/批量保存降低往返。

## 開發流程最佳實踐

### 17. ✅ 遵循 TDD 循環
Red → Green → Refactor。

### 18. ✅ 持續更新文檔
規格改動需同步更新 `.dev/specs` 與範例。

### 19. ✅ BDD 規格保護
Gherkin 風格的情境命名代表業務規則，測試失敗時需先確認原因。

### 20. ✅ Code Review 檢查清單
- [ ] Domain 邏輯在 Domain 層
- [ ] Use Case 足夠薄
- [ ] 事件命名可表達業務含義
- [ ] 測試覆蓋主要場景
- [ ] 遵循既定編碼規範

## 總結

最佳實踐的核心原則：
1. 領域優先
2. 簡單明確
3. 測試驅動
4. 持續改進
