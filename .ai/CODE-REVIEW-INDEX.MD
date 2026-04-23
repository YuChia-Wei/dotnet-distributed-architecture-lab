# Code Review Checklist 快速索引（.NET）

## 🚨 當你收到 Code Review 請求時

**格式**: `code review [FileName]`

### ⚠️ 強制執行步驟（不可跳過）

1. **讀取此檔案** - 你正在讀它 ✓
2. **識別檔案類型** - 根據下表找到對應章節
3. **讀取對應章節** - 從 .NET `.dev/standards/CODE-REVIEW-CHECKLIST.md` 讀取完整內容
4. **執行檢查** - 逐項對照，建立檢查結果表格
5. **標記問題等級** - CRITICAL / MUST FIX / SHOULD FIX

### Rule Resolution Order

1. Aggregate 規則先做 type-first 判定：
   - `EsAggregateRoot<TId>` 套 ES 規則
   - `AggregateRoot<TId>`（非 ES）不套 `Apply/When` 規則
2. Repository 規則以 `IDomainRepository<TEntity, TId>` 為 write side 基準。
3. Query 能力必須在 `I<Domain>QueryService` + `I<Domain>QueryRepository`。
4. `.dev/project-config.yaml` 只做輔助判定，與型別衝突時以型別為準並標記 MUST FIX。

### 📋 檔案類型快速對應表

| 檔案模式 | 檢查清單位置 | 檢查重點 | 優先級 |
|---------|------------|---------|--------|
| `src/Domain/**/Aggregates/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Aggregate（先做 type-first 判定）** | 1. 先判定 `EsAggregateRoot` 或 `AggregateRoot`<br>2. ES 才檢查 Apply/When<br>3. non-ES 檢查 invariant 與事件一致性 | **CRITICAL** |
| `src/**/Applications/UseCases/**/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Use Case** | 1. 是否為顯式 inbound port<br>2. `Input/Output` 命名是否正確<br>3. HTTP use case 是否避免直接依賴 bus | HIGH |
| `src/**/Applications/Commands/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Message Handler** | 1. 是否為 message-oriented flow<br>2. Command 是否只操作 write model<br>3. 是否與同名 use case 無意義重複 | HIGH |
| `src/**/Applications/Queries/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Query / Projection** | 1. Query 是否無副作用<br>2. Query side 是否使用 query repository / service<br>3. Projection 使用正確 | HIGH |
| `src/**/Repositories/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Repository** | 1. write side 是否符合 `IDomainRepository<TEntity, TId>`<br>2. domain wrapper 是否僅薄封裝<br>3. query 方法是否從 domain repository 移除 | HIGH |
| `src/Api/Controllers/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Controller** | 1. Controller 是否足夠薄<br>2. DTO 是否獨立檔案<br>3. HTTP status 正確 | MEDIUM |
| `src/Application/**/Ports/**/*Mapper.cs`<br>`src/Infrastructure/**/Mappers/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Mapper** | 1. Mapper 是否為 static/sealed？<br>2. 一個 DTO 對一個 Mapper<br>3. Outbox toDomain 是否處理有/無 events 兩種情況 | **HIGH** |
| `src/Infrastructure/**/Outbox/*Data.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **Adapter / Mapper**<br>＋ [Outbox README](../.dev/standards/examples/outbox/README.md) | 1. 是否實作 `IOutboxData<TId>`<br>2. Domain events 欄位是否標記為 NotMapped<br>3. EF Core key/column naming 是否正確 | MEDIUM |
| `src/tests/**/*.cs` | [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)<br>→ **BDD 規範 / UseCase 測試** | 1. xUnit + BDDfy（Gherkin 風格命名）<br>2. 不使用 BaseTestClass<br>3. NSubstitute 使用 | HIGH |

---

### 🔴 Aggregate 具體檢查步驟（範例）

當收到 `code review Sprint.cs` 時：

#### Step 1: 讀取檢查清單
```
我現在要 code review Sprint.cs
這是一個 Aggregate Root，根據 DOTNET-CODE-REVIEW-INDEX.md，
我必須先讀取 CODE-REVIEW-CHECKLIST.md 的 Aggregate Root 檢查章節。
```

#### Step 2: 執行 CRITICAL 檢查項目

| 檢查項目 | 結果 | 位置 | 問題描述 |
|---------|------|------|---------|
| Constructor 是否直接設定狀態欄位？ | ❌ FAIL | 60-72 行 | 直接賦值 `this.id = sprintId` |
| 是否透過 Apply(event) 觸發 When()？ | ✅ PASS | 101 行 | 有呼叫 Apply(event) |
| 狀態欄位賦值是否只在 When() 中？ | ❌ FAIL | 60-72 行 & When() | 狀態被設定兩次 |

#### Step 3: 總結與評分
**Critical 問題數量**: 2
**評分**: ⭐⭐ (2/5) - MUST FIX

---

### 🟡 Outbox Mapper 具體檢查步驟（範例）

重點：`ToDomain()` 必須處理「有 events」與「無 events」兩種重建情境。

#### ✅ 正確的 ToDomain() 模式
```csharp
public static Plan ToDomain(PlanData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = data.DomainEventDatas.Select(DomainEventMapper.ToDomain)
            .Cast<PlanEvents.IPlanEvent>()
            .ToList();
        var plan = new Plan(events) { Version = (int)data.Version };
        plan.ClearDomainEvents();
        return plan;
    }

    // 無 events 時必須從 stored state 重建
    var reconstructed = new Plan(PlanId.ValueOf(data.PlanId), data.Name, data.UserId)
    {
        Version = (int)data.Version
    };
    reconstructed.ClearDomainEvents();
    return reconstructed;
}
```

#### ❌ 錯誤的 ToDomain() 模式
```csharp
public static Plan ToDomain(PlanData data)
{
    var events = data.DomainEventDatas.Select(DomainEventMapper.ToDomain).ToList();
    return new Plan(events); // 無 events 時會建立空 aggregate
}
```

---

### 📚 相關文件

- **完整檢查清單**: [CODE-REVIEW-CHECKLIST.md](../.dev/standards/CODE-REVIEW-CHECKLIST.md)
- **Aggregate 規範**: [aggregate-standards.md](../.dev/standards/coding-standards/aggregate-standards.md)
- **Mapper 規範**: [mapper-standards.md](../.dev/standards/coding-standards/mapper-standards.md)
- **Outbox 範例**: [examples/outbox/README.md](../.dev/standards/examples/outbox/README.md)

---

### ⚠️ 違反檢查流程的後果

如果你（AI）在 Code Review 時：
- ❌ 沒有先讀取 DOTNET-CODE-REVIEW-INDEX.md
- ❌ 沒有讀取對應的 CODE-REVIEW-CHECKLIST.md 章節
- ❌ 沒有建立檢查項目對照表
- ❌ 直接給出評價和建議

**後果**：
- Code Review 結果無效（需要重做）
- 可能遺漏關鍵錯誤（如 Aggregate Event Sourcing 違規）
- 不符合專案規範要求

---

## 💡 提醒

每次執行 Code Review 前，請先在腦海中默念：

> "我必須先讀取 DOTNET-CODE-REVIEW-INDEX.md，識別檔案類型，讀取對應的檢查清單章節，然後逐項檢查。絕對不能跳過這個流程。"

## Aggregate Pattern Rules

For aggregate review, use this detection order before applying rules:

1. Type hierarchy in BuildingBlocks domain (primary):
   - `EsAggregateRoot<TId>` => apply Event Sourcing checks (`Apply/When`) as CRITICAL.
   - `AggregateRoot<TId>` and not `EsAggregateRoot<TId>` => do NOT apply `Apply/When` checks.
2. `.dev/project-config.yaml` architecture pattern (secondary hint only).
3. If type and config disagree:
   - report `TYPE-CONFIG MISMATCH` as MUST FIX,
   - keep type hierarchy as final ruleset decision.

Report output must include:
- `Detected Aggregate Type`
- `Detected Pattern`
- `Ruleset Applied` (ES / non-ES)

## Repository Rules

Repository checks in review:

- Write side baseline: `IDomainRepository<TEntity, TId>`.
- Domain-specific repository interface is allowed only as a thin wrapper inheriting `IDomainRepository<TEntity, TId>` with no extra methods.
- Query capabilities must be placed in `I<Domain>QueryService` and `I<Domain>QueryRepository`.
- If query methods are found in a domain repository, classify as MUST FIX.

## Use Case Rules

Use case checks in review:

- HTTP application boundary should be an explicit `Use Case`, not `IMessageBus`.
- Use case naming should follow `I<Verb><Noun>UseCase` / `<Verb><Noun>UseCase`.
- Use case boundary models should use `<Verb><Noun>Input` / `<Verb><Noun>Output`.
- `Request` / `Response` remain adapter models, not use case boundary models.
- `Command` / `Query` / `Handler` should be treated as message-oriented vocabulary, not as synonyms of use case.
