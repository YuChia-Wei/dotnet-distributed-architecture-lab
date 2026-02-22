# ADR-020: Archive Pattern Implementation (.NET)

## 狀態
接受 (Accepted)

## 上下文
在 CQRS 架構中：
- **Repository Pattern**：Write Model（Command Side）CRUD
- **Projection Pattern**：Read Model 查詢
- **Archive Pattern**：Read Model 的資料寫入（Query Side CRUD）

Archive Pattern 專門管理跨 Bounded Context 的參考資料（例如 Account BC 的 User）。

## 決策

### 1. Archive Pattern 定位
- Archive 專用於 Query Model 的 CRUD
- 與 Repository/Projection 組成完整資料管理架構
- 適合跨 BC 資料同步與維護

### 2. 介面設計規範
```csharp
// 命名空間：Application.UseCases.Ports.Out.Archive
public interface IUserArchive : IArchive<UserData, string>
{
    // 只使用繼承的 FindById/Save/Delete
    // 不新增自定義方法
}
```

### 3. 實作規範
```csharp
// 命名空間：Infrastructure.Persistence.Archive
public class EfCoreUserArchive : IUserArchive
{
    private readonly UserDbContext _db;

    public EfCoreUserArchive(UserDbContext db)
    {
        _db = db ?? throw new ArgumentNullException(nameof(db));
    }

    // 實作介面方法...
}
```

### 4. DI 註冊
```csharp
// Composition Root
services.AddScoped<IUserArchive, EfCoreUserArchive>();
```

### 5. 命名規範
- 介面命名：`XxxArchive`
- 實作命名：`EfCoreXxxArchive` / `InMemoryXxxArchive`

## 理由
1. **責任分離**：Write/Read/Archive 清楚區分
2. **跨 BC 資料管理**：適用於參考資料
3. **介面簡潔**：僅基本 CRUD，避免過度設計

## 範例：UserData 管理
```csharp
private void InitializeTestUsers(IUserArchive userArchive)
{
    var users = new[]
    {
        new UserData("user-001", "Alice Chen", "alice.chen@example.com"),
        new UserData("user-002", "Bob Wang", "bob.wang@example.com")
    };

    foreach (var user in users)
    {
        if (userArchive.FindById(user.Id) is null)
        {
            userArchive.Save(user);
        }
    }
}
```

## 後果
### 正面影響
- CQRS 架構清楚
- 易於測試與維護
- 支援跨 BC 參考資料

### 負面影響
- 需要額外抽象與註冊

## 相關文件
- `.dev/standards/coding-standards/archive-standards.md`
- `.dev/standards/coding-standards/repository-standards.md`
- `.dev/standards/coding-standards/projection-standards.md`
