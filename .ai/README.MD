# .ai

本目錄放置 agent-facing 的可重用 AI 資產，不是 human-facing guide 入口，也不是 skill runtime 安裝位置。

## 目錄角色

- reusable prompts
- shared rules
- automation / validation scripts
- sub-agent workflow reference

## 與其他目錄的分工

- `.ai/`
  - 給 agent 重用的 prompts、rules、scripts
- `.dev/guides/ai-collaboration-guides/`
  - 給人看的 AI collaboration guides、skill guide、prompt guide、workflow guide
- `.ai/assets/skills/`
  - canonical skill registry 與 skill specs
- `.agents/skills/` / `.claude/skills/`
  - repo-local runtime wrappers
- `.dev/workflows/`
  - 多 skill / subagent handoff artifacts

## Portable 使用原則

- `.ai/` 應作為可直接複製到其他 repo 的 agent-facing baseline
- 內容應優先保持 framework-level、agent-reusable、repo-agnostic
- 若某檔案開始描述當前專案的 source of truth，應回放到 `.dev/`
- 模板移植到新 repo 後，應優先使用 `repo-structure-sync` 來刷新 `agents.md`、`.dev/` 與必要的 `.ai/` 架構入口描述，而不是把 repo truth 直接堆進 `.ai/`
- 更完整的移植邊界見 `../.dev/PORTABLE-PACKAGING-GUIDE.MD`

## 核心文件

- `INDEX.MD`
  - `.ai/` 索引入口
- `SUB-AGENT-SYSTEM.MD`
  - sub-agent 系統與 routing 規則
- `CODE-REVIEW-INDEX.MD`
  - code review 入口
- `DIRECTORY-RULES.MD`
  - `.ai/` 與 `.dev/` 的放置規則

## 子目錄

- `assets/`
  - portable canonical source for skills、sub-agent role prompts、shared packages、templates
- `scripts/`
  - validation / review / generation scripts

## 多 Agent 情境下的 skill 收納

若同時使用 Codex、Gemini、GitHub Copilot：

- `.ai/` 應作為跨 agent 可重用資產
- `.dev/guides/ai-collaboration-guides/` 應作為 human-facing canonical guide
- `.ai/assets/skills/` 應作為 top-level skill 的 canonical source
- `.ai/assets/sub-agent-role-prompts/` 應作為 delegated sub-agent role 的 canonical source
- `.agents/skills/` 與 `.claude/skills/` 應作為 repo-local runtime wrappers

若要讓某 skill 成為 Codex 本機可直接使用的 runtime skill，應視為本機安裝/同步問題，而不是將 `.ai/` 或 `.dev/` 改成 runtime 路徑。

更完整的收納策略見：

- `../.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md`


