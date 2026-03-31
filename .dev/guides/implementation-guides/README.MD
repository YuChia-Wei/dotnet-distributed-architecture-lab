# Implementation Guides

本目錄放置偏實作、設定、排錯、操作流程的 human-facing guides。

> Note:
> 本目錄已將高流量入口文件優先改為 .NET 命名。
> 若仍看到 Java/Spring/JPA 字樣，預設應視為 historical context 或遷移紀錄，而非現行主動推薦做法。

## 適合放這裡的文件

- setup / initialization / configuration guide
- troubleshooting / solution note
- FAQ
- operational implementation walkthrough
- framework、template、test setup 操作文件

## 不適合放這裡的文件

- 架構設計原則或模型設計說明
- onboarding / learning path
- 單一真相規範或 checklist
- AI collaboration / skill / prompt guides
- 單次重構 task、plan、提案紀錄

這些內容應分別放到：

- `.dev/guides/design-guides/`
- `.dev/guides/learning-guides/`
- `.dev/standards/`
- `.dev/guides/ai-collaboration-guides/`
- `.dev/refactor-workflows/`

## 文件索引

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
  - DI registration / dependency resolution 問題排查指南
- `PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`
  - profile 複雜度處理方案
- `quick-setup.md`
  - 快速初始化流程
- `DOTNET-DI-TEST-GUIDE.md`
  - .NET DI 測試指南，現行請對照 xUnit fixture 與 `IServiceCollection`
- `TEMPLATE-SYNC-GUIDE.md`
  - template sync 操作方式
- `TEMPLATE-USAGE-GUIDE.md`
  - template 使用方式
- `VERSION-PLACEHOLDER-GUIDE.md`
  - version placeholder 相關作法
