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

不要直接從 framework repository 複製 `.ai/` 或 `.dev/`。請從對應版本的
GitHub Release 下載 package archive 與外部 `.sha256` sidecar，先驗證
checksum，再解壓縮至 target repository 以外的位置。

從解壓縮後的 envelope root 依 `INSTALL.md` 執行：

```bash
python -m pip install -r requirements.txt
python payload/.ai/scripts/plan-ai-context-package-apply.py \
  --package-root . \
  --target-root /path/to/target-repository
```

先審查 dry-run 的新增、取代、移除、重新命名與 reconciliation 結果；只有在
所有 reconciliation item 都已按 operation ID 處置後，才加入 `--apply`。
乾淨安裝完成後執行 `repo-structure-sync`，版本升級則使用
`ai-context-upgrader`。完整流程與 provenance 邊界以 package 內的
`INSTALL.md` 為準。

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
