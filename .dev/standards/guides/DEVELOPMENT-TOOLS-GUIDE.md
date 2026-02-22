# 開發工具與常用命令指南 (.NET)

## 📋 概述
提供 .NET 版本專案的常用工具與命令參考。

## 🛠️ .NET CLI 命令

### 基本命令
```bash
# 編譯專案
dotnet build

# 執行所有測試
dotnet test

# 執行特定測試類
dotnet test --filter FullyQualifiedName~CreatePlanUseCaseTests

# 執行特定測試方法
dotnet test --filter FullyQualifiedName~CreatePlanUseCaseTests&FullyQualifiedName~ShouldCreate

# 跳過測試打包
dotnet publish -c Release -p:RunTests=false

# 監看並重新編譯
dotnet watch --project src/Api
```

### 依賴管理
```bash
dotnet list package
dotnet add package WolverineFx
dotnet restore
```

## 🔍 Git 命令

```bash
git status
git add -A
git commit -m "feat: Add new feature"
git push origin main
```

### 提交規範
```
feat: 新功能
fix: 修復錯誤
docs: 文檔更新
style: 格式調整
refactor: 重構
perf: 效能改進
test: 新增測試
chore: 輔助工具調整
```

## 🐳 Docker 命令

### PostgreSQL 本地開發
```bash
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=aiplan \
  -p 5432:5432 \
  -d postgres:15

docker exec -it postgres-dev psql -U postgres -d aiplan
```

## 🗃️ EF Core Migration 命令
```bash
dotnet ef migrations add Init --project src/Infrastructure --startup-project src/Api
dotnet ef database update --project src/Infrastructure --startup-project src/Api
```

## 🔧 IDE 快捷鍵

### Visual Studio
```
Ctrl + T           # Go to All
Ctrl + .           # Quick Actions
F12                # Go to Definition
Ctrl + Shift + F   # Find in Files
```

### VS Code
```
Cmd + P            # 快速開啟
Cmd + Shift + P    # 命令面板
Cmd + Shift + F    # 全域搜尋
F12                # 跳轉定義
```

## 🐛 調試技巧

```bash
dotnet watch --project src/Api
```

### 日誌級別調整
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft": "Warning"
    }
  }
}
```

## 🚀 效能分析

```bash
dotnet-counters monitor --process-id <pid>
dotnet-trace collect --process-id <pid>
```

## 📝 實用腳本

```bash
# 取代類名（.cs）
rg -l "OldClassName" src | xargs sed -i '' 's/OldClassName/NewClassName/g'

# 統計程式碼行數
rg --files src tests | xargs wc -l
```

## 🔗 相關資源
- https://learn.microsoft.com/dotnet
- https://learn.microsoft.com/ef/core
