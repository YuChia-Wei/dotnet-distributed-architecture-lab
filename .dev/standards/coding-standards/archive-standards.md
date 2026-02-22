# Archive 編碼規範 (.NET)

本文件定義 Archive Pattern 的編碼標準，負責處理 Query Model 的寫入資料庫需求。

---

## 📌 概述

Archive Pattern 用於軟刪除與歷史資料管理，在 CQRS 架構中專門用於「Query Model」寫入。

- **Query Model 寫入**：Archive 負責 Query Model 的寫入資料庫需求
- **與 Repository 區別**：Repository 只限定在 Command Model 寫入單一 Aggregate 使用
- **事件驅動**：Reactor 收到 Domain Event 時呼叫 Archive

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# Archive 規則（軟刪除支援）
Pattern (required, any): IsDeleted|IsArchived|ArchivedAt

# 禁止規則（不可硬刪除）
Pattern (forbidden): HardDelete
```

---

## 📌 核心概念

**Archive** 是一種資料庫寫入模式，在 CQRS 架構中，專門用於「Query Model」：

- 介面與 Write Model 的 Repository 相似，差別在於 Archive 負責 Query Model 的寫入資料庫需求
- Repository 只限定在 Command Model 寫入單一 Aggregate 使用
- 可寫入單表格或跨表格
- Handler 層的 Reactor 物件收到 Domain Event 時呼叫 Archive，將資料寫入資料庫

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. Archive Interface 設計

#### 命名空間

```csharp
// ✅ 正確：Archive 介面定義在 Application 層
namespace YourProject.Application.Users.Archives;

// ❌ 錯誤：不要放在 Infrastructure 層
namespace YourProject.Infrastructure.Persistence;  // 錯誤！
```

#### Interface 命名規範

```csharp
// ✅ 正確：使用 I[Entity]Archive 命名（單數形）
public interface IUserArchive { }

// ❌ 錯誤：不要使用其他命名模式
public interface IUserRepository { }  // Read Model 不要用 Repository
public interface UserArchive { }      // 要加 I 前綴
public interface IUserDtoArchive { }  // 不要用 DtoArchive
```

#### Interface 定義

```csharp
// ✅ 正確：定義 Archive Interface
public interface IUserArchive
{
    Task<UserData?> FindByIdAsync(string userId, CancellationToken ct = default);
    Task SaveAsync(UserData userData, CancellationToken ct = default);
    Task DeleteAsync(UserData userData, CancellationToken ct = default);
}

// ❌ 錯誤：不要返回領域物件
public interface IUserArchive
{
    Task<User?> FindByIdAsync(string userId);  // 錯誤！應返回 UserData
}

// ❌ 錯誤：不要返回 DTO
public interface IUserArchive
{
    Task<UserDto?> FindByIdAsync(string userId);  // 錯誤！應返回 UserData
}
```

---

### 2. Archive 實作

#### 實作位置

```csharp
// ✅ 正確：實作放在 Infrastructure 層
namespace YourProject.Infrastructure.Persistence.Archives;
```

#### EF Core Archive 實作

```csharp
// ✅ 正確：EF Core 實作
namespace YourProject.Infrastructure.Persistence.Archives;

public class EfCoreUserArchive : IUserArchive
{
    private readonly ApplicationDbContext _context;

    public EfCoreUserArchive(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<UserData?> FindByIdAsync(string userId, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(userId);
        
        return await _context.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == userId, ct);
    }

    public async Task SaveAsync(UserData userData, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(userData);
        
        var existing = await _context.Users
            .FirstOrDefaultAsync(x => x.Id == userData.Id, ct);
        
        if (existing is null)
        {
            await _context.Users.AddAsync(userData, ct);
        }
        else
        {
            _context.Entry(existing).CurrentValues.SetValues(userData);
        }
    }

    public async Task DeleteAsync(UserData userData, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(userData);
        
        var existing = await _context.Users
            .FirstOrDefaultAsync(x => x.Id == userData.Id, ct);
        
        if (existing is not null)
        {
            _context.Users.Remove(existing);
        }
    }
}
```

---

### 3. DI 註冊

```csharp
// ✅ 正確：在 ServiceExtensions 中註冊
public static class ArchiveServiceExtensions
{
    public static IServiceCollection AddArchives(this IServiceCollection services)
    {
        services.AddScoped<IUserArchive, EfCoreUserArchive>();
        // 其他 Archive 註冊...
        
        return services;
    }
}
```

---

## 🎯 使用場景指南

### 何時使用 Archive

- ✅ Query Model 的 CRUD 操作
- ✅ 跨 Bounded Context 的參考資料同步
- ✅ 事件驅動寫入 Read Model
- ❌ Write Model 的 CRUD 操作（使用 Repository）

### 與 Repository 的區別

```csharp
// Repository：Write Model 的 Aggregate 持久化
IRepository<Product, ProductId> repository;
await repository.FindByIdAsync(id);  // 返回 Product 領域物件
await repository.SaveAsync(product); // 儲存領域物件

// Archive：Read Model 的 Data 持久化
IUserArchive archive;
await archive.FindByIdAsync(userId);   // 返回 UserData
await archive.SaveAsync(userData);     // 儲存 Data 物件
```

---

## 🎯 事件驅動寫入範例

### Reactor 使用 Archive

```csharp
// ✅ 正確：使用 WolverineFx 處理 Domain Event
public class UserCreatedReactor
{
    private readonly IUserArchive _archive;

    public UserCreatedReactor(IUserArchive archive)
    {
        _archive = archive;
    }

    public async Task Handle(UserCreated @event, CancellationToken ct)
    {
        var userData = new UserData
        {
            Id = @event.UserId.Value,
            Name = @event.Name,
            Email = @event.Email,
            CreatedAt = @event.OccurredOn
        };

        await _archive.SaveAsync(userData, ct);
    }
}
```

---

## 🔍 檢查清單

### Archive Interface
- [ ] 定義在 `Application` 層
- [ ] 使用 `I[Entity]Archive` 命名
- [ ] 返回 Data (Persistence Object) 而非領域物件或 DTO
- [ ] 有 `FindByIdAsync`, `SaveAsync`, `DeleteAsync` 方法
- [ ] 支援 `CancellationToken`

### Archive 實作
- [ ] 實作在 `Infrastructure.Persistence.Archives`
- [ ] 使用 EF Core
- [ ] 使用 `ArgumentNullException.ThrowIfNull`
- [ ] 透過 DI 註冊

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| Inquiry + Archive 範例 | [../examples/inquiry-archive/](../examples/inquiry-archive/) |
| 使用指南 | [../examples/inquiry-archive/USAGE-GUIDE.md](../examples/inquiry-archive/USAGE-GUIDE.md) |

---

## 相關文件

- [repository-standards.md](repository-standards.md)
- [projection-standards.md](projection-standards.md)
- [usecase-standards.md](usecase-standards.md)
