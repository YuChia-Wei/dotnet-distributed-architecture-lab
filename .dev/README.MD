# .NET 專案文檔

> 此目錄包含 .NET 專案的技術規範、ADR、經驗教訓與標準。

## 📁 目錄結構

| 資料夾 | 說明 |
| :--- | :--- |
| `adr/` | .NET 架構決策紀錄 (ADR) |
| `guides/` | 一般 human-facing guides（ai collaboration / design / implementation / learning） |
| `lessons/` | 經驗教訓與錯誤案例 |
| `operations/` | 分散式系統 runtime / 維運文件（context map、event catalog、MQ topology、runbook） |
| `requirement/` | 技術需求與規格 |
| `workflows/` | 跨 skill / subagent workflow artifacts（plan / review-report / task） |
| `specs/` | 詳細規格指南 |
| `standards/` | 技術標準、Code Review Checklist、專案結構 |

## 🚀 Quick Start

1. **架構概覽**: 請先閱讀 [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
2. **技術選型**: [`requirement/TECH-STACK-REQUIREMENTS.MD`](requirement/TECH-STACK-REQUIREMENTS.MD)
3. **Code Review**: [`standards/CODE-REVIEW-CHECKLIST.md`](standards/CODE-REVIEW-CHECKLIST.md)
4. **ADR 索引**: [`adr/INDEX.md`](adr/INDEX.md)
5. **Application 詞彙邊界**: [`standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD)

## 🔗 相關資源

- Human-facing AI Collaboration Guides: `guides/ai-collaboration-guides/`
- AI Prompts: `.ai/`
- Portable Canonical AI Assets: `.ai/assets/`
- Portable Packaging Guide: `PORTABLE-PACKAGING-GUIDE.MD`
- Claude Skills: `.claude/skills/`
- Claude Skills Index: `.claude/skills/README.md`
- 專案入口: `AGENTS.md`

## 📌 內容定位

- `.dev/` 放給人看的知識、指南、規範與索引
- `.ai/` 放給 agent 重用的 prompts、shared rules、scripts
- `.claude/skills/` 放 skill 實作本體與 skill-local resources

### `.dev/` 內部常見協作文件

- `.dev/requirement/`: functional / non-functional requirement docs
- `.dev/specs/`: function specs 與行為規格
- `.dev/operations/`: distributed runtime truth 與維運文件
- `.dev/workflows/`: 多 skill / subagent handoff 所需的 `plan`、`review-report`、`task`

當工作涉及多 skill 接力、subagent 分工或 staged refactoring 時，優先從這四類文件建立共同上下文。

## Portable 使用原則

- `.dev/` 可作為新專案的知識治理骨架直接複製
- 但 `.dev/requirement/`、`.dev/specs/`、`.dev/operations/` 與具體 `ADR-*.md` 通常屬於專案真相，不應原封不動沿用
- 移植規則與保留/重寫邊界見 `PORTABLE-PACKAGING-GUIDE.MD`

