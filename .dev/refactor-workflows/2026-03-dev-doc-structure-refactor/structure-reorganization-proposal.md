# Dev Documentation Structure Reorganization Proposal

## Purpose

本提案用來重整 `.dev` 內的文件資訊架構，降低 `guides`、`standards`、`guides/ai-collaboration-guides` 之間的重疊與語意漂移。

本文件先定義 target structure 與 migration mapping，不在這一輪直接搬移所有檔案。

## Current Problems

### 1. `.dev/guides/` 內容混雜

目前同時包含：

- learning / onboarding
- design decision support
- implementation / setup
- troubleshooting

### 2. `.dev/standards/` 角色不夠單一

目前同時包含：

- true standards / checklists
- setup guides
- references
- FAQ / troubleshooting 類文件

### 3. `.dev/guides/ai-collaboration-guides/` 已超出 skill guide 範圍

目前除了 skill guides，還包含：

- workflow guide
- contracts
- strategies
- prompt guides

因此資料夾名稱與實際內容已有落差。
這個問題應先以「更名」處理，而不是直接併入 `.dev/guides/`。

## Proposed Target Structure

```text
.dev/
  adr/
  requirement/
  specs/
  standards/
  guides/
    ai-collaboration-guides/
    design-guides/
    implementation-guides/
    learning-guides/
  lessons/
  refactor-workflows/
```

## Directory Roles

### `.dev/standards/`

只放：

- rules
- checklists
- anti-patterns / best-practices
- project structure
- single source of truth style documents

不放：

- setup walkthrough
- troubleshooting guide
- FAQ
- prompt guide

### `.dev/guides/design-guides/`

放：

- architecture-oriented design guidance
- data model / API integration design guidance
- testing design guidance

### `.dev/guides/implementation-guides/`

放：

- setup
- configuration
- operational implementation steps
- troubleshooting / fix-oriented guides

### `.dev/guides/learning-guides/`

放：

- onboarding
- learning path
- concept introduction

### `.dev/guides/ai-collaboration-guides/`

放：

- skill guides
- prompt guides
- workflow guides
- contracts
- strategies
- pairing guides

## Recommended Migration Mapping

### Keep In `standards/`

- `CODE-REVIEW-CHECKLIST.md`
- `coding-standards.md`
- `coding-guide.md`
- `project-structure.md`
- `best-practices.md`
- `anti-patterns.md`
- `ASPNET-CORE-CONFIGURATION-CHECKLIST.md`

### Move From `standards/` To `guides/implementation-guides/`

- `COMPLETE-ASPNET-CORE-SETUP-GUIDE.md`
- `quick-setup.md`
- `COMMON-MISTAKES-GUIDE.md`
- `FAQ.md`
- `TEMPLATE-USAGE-GUIDE.md`
- `TEMPLATE-SYNC-GUIDE.md`

### Move From `standards/` To `guides/design-guides/`

- `EZDDD-FRAMEWORK-REFERENCE.md`

### Move From `guides/` To `guides/learning-guides/`

- `LEARNING-PATH.md`
- `NEW-PROJECT-GUIDE.md`

### Move From `guides/` To `guides/design-guides/`

- `DATA-CLASS-STANDARDS.md`
- `FRAMEWORK-API-INTEGRATION-GUIDE.md`
- `PROFILE-BASED-TESTING-GUIDE.md`
- `TEST-DATA-PREPARATION-GUIDE.md`

### Move From `guides/` To `guides/implementation-guides/`

- `CORS-SETUP.md`
- `DUAL-PROFILE-CONFIGURATION-GUIDE.md`
- `NEW-PROJECT-TEST-SETUP-GUIDE.md`
- `PREVENT-REPOSITORY-BEAN-MISSING.md`
- `PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`
- `SPRING-DI-TEST-GUIDE.md`
- `VERSION-PLACEHOLDER-GUIDE.md`

### Rename `.dev/ai-skill-guides/` To `.dev/guides/ai-collaboration-guides/`

建議先修正名稱，再收納到 `guides/` 之下。
理由是目前這批文件已經是一個 AI collaboration knowledge base，但仍屬於 human-facing guides。

## Suggested Migration Principle

1. 先將 `.dev/ai-skill-guides/` 更名並收納到 `.dev/guides/ai-collaboration-guides/`
2. 再建立 `guides/design-guides/`、`guides/implementation-guides/`、`guides/learning-guides/`
3. 再搬 `guides/` 其餘文件
4. 最後清理 `standards/`

## Risks

- 舊連結會失效
- `README` / `INDEX` / `AGENTS` 需同步更新
- 一次搬太多會讓變更難 review

## Suggested Execution Style

- 分 stage 進行
- 每次只搬一類文件
- 每輪搬遷後立即更新索引與入口

## Recommendation

我建議先做這個順序：

1. 先將 `.dev/ai-skill-guides/` 更名並收納到 `.dev/guides/ai-collaboration-guides/`
2. 再將 `.dev/guides/` 拆出 `design-guides/`、`implementation-guides/`、`learning-guides/`
3. 再將 `standards/` 中不屬於標準的文件移出

這樣可以先把最明顯的語意錯位修正，再做細部清理。
