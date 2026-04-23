# Docker Restore Cache Guide

本文件定義 .NET 多階段 Dockerfile 中，`dotnet restore` 前的 `*.csproj` 複製策略。

## 核心規則

在 `dotnet restore` 前，應顯式 `COPY` 入口專案及其遞迴 `ProjectReference` 所需的 `*.csproj`。

不要直接在 restore 前使用：

```dockerfile
COPY . .
```

## Why

- 保留 restore layer cache 命中率
- 避免任一 `.cs` 變更都讓 restore 重跑
- 在多 BC / 多 project reference 結構下，建置時間更穩定

## Tradeoff

顯式 `COPY` 的缺點是：

- 新增 `ProjectReference` 時要同步維護 Dockerfile

因此建議：

- 在 code review 檢查 Dockerfile 與 `ProjectReference` 是否同步
- 或用輔助腳本檢查缺漏的 `COPY *.csproj`

## Practical Rule

- restore 前：只 copy `*.csproj` 與必要 build metadata
- restore 後：再 `COPY . .`

## Example Shape

```dockerfile
COPY ["src/App/App.csproj", "src/App/"]
COPY ["src/Shared/Shared.csproj", "src/Shared/"]
RUN dotnet restore "src/App/App.csproj"

COPY . .
RUN dotnet publish "src/App/App.csproj" -c Release -o /app/publish
```

## Related

- `../../.ai/scripts/check-dockerfile-csproj-copy-sync.ps1`
- `./TEMPLATE-USAGE-GUIDE.md`
