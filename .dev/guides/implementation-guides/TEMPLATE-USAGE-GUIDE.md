# 範本使用指南 (.NET)

本指南說明各種 .NET 範本的使用時機、選擇標準與最佳實踐。

## 📋 目錄
1. [範本選擇決策樹](#範本選擇決策樹)
2. [按任務類型選擇範本](#按任務類型選擇範本)
3. [範本組合使用指南](#範本組合使用指南)
4. [常見場景範例](#常見場景範例)
5. [範本依賴關係](#範本依賴關係)

## 🌳 範本選擇決策樹

```
開始
├── 建立新功能？
│   ├── 是 → 需要持久化？
│   │   ├── 是 → Aggregate + Repository + EF Core Mapping
│   │   └── 否 → 只建立 Aggregate
│   └── 否 → 查看現有功能
│
├── 實作業務操作？
│   ├── 修改狀態 → UseCase (Command) + Handler
│   └── 查詢資料 → UseCase (Query) + Projection
│
├── API 開發？
│   ├── REST API → Controller + DTO
│   └── 內部呼叫 → 直接使用 UseCase
│
└── 資料轉換？
    ├── Domain ↔ DTO → Mapper
    └── Domain ↔ Persistence → Mapper
```

## 📊 按任務類型選擇範本

### 1. 創建新的業務實體
- Aggregate 模板
- Value Object 模板
- Repository 模板

### 2. 新增 Use Case
- Handler / Input / Output 模板
- 對應測試模板（xUnit + BDDfy）

### 3. 新增查詢
- Projection 模板
- DTO 模板

## 🔗 範本依賴關係

- Controller 依賴 UseCase/Handler
- UseCase 依賴 Domain
- Projection 依賴 DTO/Mapper
