# MQArchLab 專案開發指南與 AI 助理提示 (Project Development Guide & AI Assistant Prompt)

## 1. 總覽 (Overview)

本文件為 `dotnet-mq-arch-lab` 專案提供開發準則，旨在確保程式碼的一致性、品質以及遵循既定架構。所有 AI 助理的互動與產出都應嚴格遵守本文件定義的規則。

## 2. 架構原則 (Architectural Principles)

軟體架構必須遵循以下核心原則：

- **乾淨架構 (Clean Architecture, CA):** 強制執行關注點分離與依賴規則。
- **領域驅動設計 (Domain-Driven Design, DDD):** 專注於核心領域與領域邏輯。
- **命令查詢責任分離 (Command Query Responsibility Segregation, CQRS):** 將讀取與寫入操作分離。

## 3. 核心技術 (Core Technologies)

- **主框架 (Main Framework):** .NET 9
- **主要語言 (Primary Language):** C#
- **容器化 (Containerization):** Docker

## 4. 專案結構 (Project Structure)

專案遵循基於「乾淨架構」的嚴格分層目錄結構。**所有原始碼專案都必須放置在 `src` 資料夾下。**

### 命名慣例 (Naming Conventions):

- **複數命名:** `Applications`, `Repositories`, `Domains` 等分層專案的名稱，以及專案內的資料夾，在適當時應優先使用**複數形式 (plural form)**。

### 服務結構範例 (例如 "Orders" 服務):

```
dotnet-mq-arch-lab/
├── src/
│   └── Orders/
│       ├── Orders.Api/
│       │   └── Dockerfile
│       ├── Orders.Applications/
│       ├── Orders.Domains/
│       └── Orders.Infrastructure/
├── docker-compose/
│   └── docker-compose.yml
├── .gitignore
└── MQArchLab.slnx
```

### 規則 (Rules):

1.  **原始碼位置:** 所有 .NET 專案 **必須** 建立在 `src` 目錄下的獨立資料夾中。
2.  **Docker Compose:** `docker-compose` 目錄專門用於存放本機開發與測試環境的設定。
3.  **方案檔案:** 根目錄的 `MQArchLab.slnx` 是整個方案的解決方案檔案。新專案必須加入此方案，並建議使用方案資料夾進行分組。

## 5. Dockerfile 要求 (Dockerfile Requirements)

**每一個**位於 `src` 目錄下的可執行專案（例如 API 或背景服務）都 **必須** 包含一個 `Dockerfile`。

### Dockerfile 範本 (Dockerfile Template):

請使用以下的多階段建置 (multi-stage build) 範本以確保最佳化、安全的映像檔。

```Dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/<ProjectName>/<ProjectName>.csproj", "<ProjectName>/"]
RUN dotnet restore "<ProjectName>/<ProjectName>.csproj"
COPY src/<ProjectName>/ .
WORKDIR "/src/<ProjectName>"
RUN dotnet build "<ProjectName>.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "<ProjectName>.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "<ProjectName>.dll"]
```

## 6. 開發流程 (Development Workflow)

### 建立新專案 (Creating a New Project)

當需要建立一個新的服務或應用程式時，請遵循以下步驟：

1.  **確認專案類型與名稱:** 向使用者確認要建立的 .NET 專案範本（例如 `webapi`, `console`）和專案名稱（例如 `PublisherService`）。
2.  **建立專案目錄:** 在 `src` 下建立一個與專案同名的資料夾。
3.  **執行 `dotnet new`:**
    ```shell
    dotnet new <template> -n <ProjectName> -o src/<ProjectName>
    ```
4.  **加入方案:** 將新專案加入到根目錄的 `.slnx` 檔案中。
    ```shell
    dotnet sln add src/<ProjectName>/<ProjectName>.csproj
    ```
5.  **建立 Dockerfile:** 在 `src/<ProjectName>/` 路徑下，根據上述範本建立 `Dockerfile`。
6.  **更新 Docker Compose (可選):** 如果需要在本機進行整合測試，請在 `docker-compose/docker-compose.yml` 中為新服務新增一個 service entry。

## 7. 程式碼風格 (Coding Conventions)

- 遵循 Microsoft 官方的 [C# 程式碼撰寫慣例](https://docs.microsoft.com/zh-tw/dotnet/csharp/fundamentals/coding-style/coding-conventions)。
- **命名:** 分層專案 (`Applications`, `Repositories`) 和內部資料夾優先使用複數形式。
- 優先使用 File-scoped namespaces。
- 在適當的情況下（如 `Program.cs`）使用 Top-level statements。