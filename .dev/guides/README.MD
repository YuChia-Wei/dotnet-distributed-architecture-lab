# Guides

本目錄放置 human-facing guides，依用途拆成子分類，避免將規範、操作指南、AI 協作文件混在同一層。

> Note:
> 本目錄已將高流量入口文件優先收斂為 .NET 命名。
> 若仍看到 Java/Spring/JPA 字樣，預設應先視為 historical context、ADR translation context、或 inventory/reference 紀錄，而非現行主動推薦做法。

## 子目錄

- `ai-collaboration-guides/`
  - AI collaboration、skill、prompt、workflow、contract 指南
- `design-guides/`
  - 架構設計、資料模型、整合設計、測試設計相關指南
- `implementation-guides/`
  - setup、configuration、implementation、troubleshooting 指南
- `learning-guides/`
  - onboarding、learning path、入門指南

## 快速選擇

- 要找規範、檢查表、單一真相文件：
  - 看 `.dev/standards/`
- 要找 AI 使用流程、skill guide、prompt guide：
  - 看 `ai-collaboration-guides/`
- 要找架構/設計方法或整合設計參考：
  - 看 `design-guides/`
- 要找 setup、設定、常見問題或排錯：
  - 看 `implementation-guides/`
- 要找 onboarding 或學習入口：
  - 看 `learning-guides/`

## 子目錄索引

### `ai-collaboration-guides/`

- `AI-COLLABORATION-WORKFLOW-GUIDE.md`
  - AI 協作總流程與 direct/workflow mode 判斷
- `AI-ASSET-LOCATION-STRATEGY.md`
  - 多 agent 情境下的 AI 資產收納策略
- `LOCAL-RUNTIME-WRAPPER-GUIDE.md`
  - repo wrapper 與本機 runtime 的使用方式
- `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
  - refactoring skills 的邊界與分工
- `AI-REFACTORING-SKILL-CONTRACTS.md`
  - refactoring skills 的 input/output contract
- `AI-SKILL-GUIDE-STANDARDS.md`
  - AI guide 文件撰寫規則
- `BDD-GWT-TEST-DESIGNER-PAIR-GUIDE.md`
  - BDD/GWT 測試設計與其他流程的配對方式
- `BDD-GWT-TEST-DESIGNER-SKILL-GUIDE.md`
  - BDD/GWT 測試設計 skill 使用說明
- `DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`
  - DDD + CA + HEX architect skill 使用說明
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`
  - 多 skill 協作時的最小 workflow mode
- `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY.md`
  - requirement/spec 設計是否要做成 skill 的策略
- `REQUIREMENT-DESIGNER-PROMPT-GUIDE.md`
  - requirement 設計 prompt 使用範本
- `SPEC-DESIGNER-PROMPT-GUIDE.md`
  - spec 設計 prompt 使用範本
- `STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
  - staged refactor implementer 使用說明
- `TACTICAL-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
  - tactical refactor implementer 使用說明

### `design-guides/`

- `DATA-CLASS-STANDARDS.md`
  - data class 設計準則與使用界線
- `EZDDD-FRAMEWORK-REFERENCE.md`
  - ezDDD framework 概念對照與參考
- `FRAMEWORK-API-INTEGRATION-GUIDE.md`
  - framework API integration 設計與使用方式
- `PROFILE-BASED-TESTING-GUIDE.md`
  - profile-based testing 設計方式
- `TEST-DATA-PREPARATION-GUIDE.md`
  - 測試資料準備與設計注意事項

### `implementation-guides/`

- `COMMON-MISTAKES-GUIDE.md`
  - 常見錯誤與避免方式
- `COMPLETE-ASPNET-CORE-SETUP-GUIDE.md`
  - ASP.NET Core setup 完整流程
- `CORS-SETUP.md`
  - CORS 設定
- `DUAL-PROFILE-CONFIGURATION-GUIDE.md`
  - dual-profile configuration 設定
- `FAQ.md`
  - 常見問題入口
- `NEW-PROJECT-TEST-SETUP-GUIDE.md`
  - 新專案測試設定流程
- `PREVENT-SERVICE-REGISTRATION-MISSING.md`
  - service registration / dependency resolution 問題排查指南
- `PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`
  - profile 複雜度處理方案
- `quick-setup.md`
  - 快速初始化流程
- `DOTNET-DI-TEST-GUIDE.md`
  - .NET DI 測試指南；現行使用 xUnit + `IServiceCollection` / fixture-based test setup
- `TEMPLATE-SYNC-GUIDE.md`
  - template sync 操作方式
- `TEMPLATE-USAGE-GUIDE.md`
  - template 使用方式
- `VERSION-PLACEHOLDER-GUIDE.md`
  - version placeholder 相關作法

### `learning-guides/`

- `LEARNING-PATH.md`
  - 專案學習路徑
- `NEW-PROJECT-GUIDE.md`
  - 新專案入門與 onboarding 指南

## 分工邊界

- `.dev/guides/`
  - how-to、setup、workflow、reference、onboarding 文件
- `.dev/standards/`
  - rules、checklists、single source of truth
- `.dev/workflows/`
  - 一次性重構工作紀錄、plan、task、review artifacts

## 新文件放置規則

- 新增規則、檢查表、唯一真相文件：
  - 放 `.dev/standards/`
- 新增長期保留的操作指南或參考文件：
  - 放 `.dev/guides/` 對應子目錄
- 新增 AI skill、prompt、workflow 的人類使用說明：
  - 放 `ai-collaboration-guides/`
- 新增單次重構提案、執行記錄、task artifact：
  - 放 `.dev/workflows/<workflow-id>/`

