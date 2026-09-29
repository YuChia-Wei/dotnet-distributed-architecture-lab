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

### 2. 安裝已發布的 AI Context Package

使用已發布版本的官方安裝說明，先由 catalog 與 selection 產生候選 subset，
再以固定 engine 的 API2 `plan` 和 `apply` 安裝。審查 plan 的新增、
替換與保留路徑；不要直接複製 framework repository 的舊 `.ai/assets/`
或執行 RC1 的 `plan-ai-context-package-apply.py`、`ai-context-init`、
`ai-context-upgrader` 命令。正式安裝會產生 `.ai/framework.lock`，
target 的選擇存於 `.ai/custom/installation.json`，專案規則仍由 target
擁有。具體命令與輸入格式以該版本的官方安裝說明為準。

### 3. 設定基礎相依
- WolverineFx
- EF Core (Npgsql/SqlServer)
- xUnit + BDDfy (Gherkin-style naming only)
- Target `testing.mocking` selection (NSubstitute by default)

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
