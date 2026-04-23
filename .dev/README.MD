# .NET 專案文檔

> 此目錄包含 .NET 專案的技術規範、歷史決策紀錄、經驗教訓與標準。

## 📁 目錄結構

| 資料夾 | 說明 |
| :--- | :--- |
| `adr/` | ADR 治理層（template / index / 建立時機） |
| `guides/` | 一般 human-facing guides（ai collaboration / design / implementation / learning） |
| `lessons/` | 經驗教訓與錯誤案例 |
| `operations/` | 分散式系統 runtime / 維運文件（context map、event catalog、MQ topology、runbook） |
| `requirement/` | 技術需求與規格 |
| `workflows/` | 跨 skill / subagent workflow artifacts（plan / review-report / task） |
| `specs/` | 詳細規格指南 |
| `standards/` | 技術標準、Code Review Checklist、專案結構 |
| `TEAM-GIT-FLOW-RULES.MD` | 團隊 git flow / branch naming 規則草案，可在發佈前改寫成目標專案版本 |

## 🚀 Quick Start

1. **架構概覽**: 請先閱讀 [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
2. **技術選型**: [`requirement/TECH-STACK-REQUIREMENTS.MD`](requirement/TECH-STACK-REQUIREMENTS.MD)
3. **Code Review**: [`standards/CODE-REVIEW-CHECKLIST.md`](standards/CODE-REVIEW-CHECKLIST.md)
4. **架構規則入口**: [`standards/README.md`](standards/README.md)
5. **Application 詞彙邊界**: [`standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD)

## 🔗 相關資源

- Human-facing AI Collaboration Guides: `guides/ai-collaboration-guides/`
- AI Prompts: `.ai/`
- Portable Canonical AI Assets: `.ai/assets/`
- Portable Packaging Guide: `PORTABLE-PACKAGING-GUIDE.MD`
- Repo Structure Sync Guide: `guides/ai-collaboration-guides/REPO-STRUCTURE-SYNC-SKILL-GUIDE.md`
- Team Git Flow Rules: `TEAM-GIT-FLOW-RULES.MD`
- Canonical Skill Registry: `.ai/assets/skills/README.MD`
- Agents Runtime Wrappers: `.agents/skills/README.md`
- Claude Runtime Wrappers: `.claude/skills/README.md`
- 專案入口: `AGENTS.md`

## 📌 內容定位

- `.dev/` 放給人看的知識、指南、規範與索引
- `.ai/` 放給 agent 重用的 prompts、shared rules、scripts
- `.ai/assets/skills/` 放 canonical skill specs
- `.agents/skills/` 與 `.claude/skills/` 放 runtime wrappers

### `.dev/` 內部常見協作文件

- `.dev/requirement/`: functional / non-functional requirement docs
- `.dev/specs/`: function specs 與行為規格
- `.dev/operations/`: distributed runtime truth 與維運文件
- `.dev/workflows/`: 多 skill / subagent handoff 所需的 `plan`、`review-report`、`task`

當工作涉及多 skill 接力、subagent 分工或 staged refactoring 時，優先從這四類文件建立共同上下文。

## Portable 使用原則

- `.dev/` 可作為新專案的知識治理骨架直接複製
- 但 `.dev/requirement/`、`.dev/specs/`、`.dev/operations/` 與任何 project-specific 歷史決策紀錄通常屬於專案真相，不應原封不動沿用
- 移植規則與保留/重寫邊界見 `PORTABLE-PACKAGING-GUIDE.MD`
