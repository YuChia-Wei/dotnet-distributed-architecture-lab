# .NET DDD 快速設置指南

## 新專案設置

### 1. 初始化專案結構
```bash
mkdir -p src tests .ai .dev
dotnet new sln -n MyApp
dotnet new webapi -o src/Api
dotnet new classlib -o src/Domain
dotnet new classlib -o src/Application
dotnet new classlib -o src/Infrastructure
dotnet new classlib -o src/Contracts
dotnet new xunit -o tests/Application.Tests
dotnet new xunit -o tests/Domain.Tests
dotnet sln MyApp.slnx add src/Api src/Domain src/Application src/Infrastructure src/Contracts
dotnet sln MyApp.slnx add tests/Application.Tests tests/Domain.Tests
```

### 1.1 `.slnx` 方案資料夾命名（固定格式）
```bash
# 固定使用前後斜線的邏輯分組
dotnet sln MyApp.slnx add src/Order/DomainCore/Order.Applications/Order.Applications.csproj --solution-folder "/Order/DomainCore/"
dotnet sln MyApp.slnx add src/Order/Presentation/Order.WebApi/Order.WebApi.csproj --solution-folder "/Order/Presentation/"
dotnet sln MyApp.slnx add tests/Order.Tests/Order.Tests.csproj --solution-folder "/tests/"
```

### 2. 複製必要檔案
```bash
# 從此 repo 複製 AI 與規格資料
cp -r /path/to/ai-plan/.ai .ai
cp -r /path/to/ai-plan/.dev .dev
```

### 3. 設定基礎相依
- WolverineFx
- EF Core (Npgsql/SqlServer)
- xUnit + BDDfy (Gherkin-style naming only)
- NSubstitute

### 4. 建立第一個 Aggregate
使用 AI 指令建立 Aggregate：

```
請使用 feature-implementation workflow 創建 User aggregate
需要包含：
- userId (AggregateId)
- email (唯一)
- name
- 基本的 CRUD 操作
```
