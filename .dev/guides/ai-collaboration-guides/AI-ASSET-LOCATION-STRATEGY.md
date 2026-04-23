# AI Asset Location Strategy

本文件定義本 repo 在多 agent 協作情境下，`skill`、`prompt`、`guide`、`workflow artifact` 的放置策略。

目前主要目標是同時支援：

- Codex
- Gemini
- GitHub Copilot

## 核心原則

- 先區分 `canonical source` 與 `agent runtime wrapper`
- 先區分 human-facing 文件與 agent-facing 資產
- 不把所有 agent 的專屬格式硬塞進同一個資料夾

## 建議分工

| 路徑 | 主要讀者 | 角色 |
|------|---------|------|
| `.ai/assets/` | Agent | canonical source for portable skills、sub-agent-role-prompts、shared packages |
| `.dev/guides/ai-collaboration-guides/` | Human | human-facing guides、workflow、prompt 使用說明 |
| `.dev/workflows/` | Human + Agent | plan / review-report / task artifact |
| `.ai/` | Agent | reusable prompts、shared rules、scripts |
| `.agents/skills/` | Agent | current runtime skill wrappers |
| `.claude/skills/` | Agent | Claude runtime skill wrappers |

## Skill 應不應該搬到 `.agents/skills/`

### 結論

- repo 內可版本控管且跨 agent 可共用的 skill 真相，應放在 `.ai/assets/skills/`
- `.agents/skills/` 與 `.claude/skills/` 都只是 runtime wrapper，不應再承擔 canonical skill 定義

### 目前建議

- repo 內保留 `.agents/skills/` 與 `.claude/skills/` 作為 runtime wrapper 資產
- `.ai/` 保留跨 agent 可重用的 prompts / rules / scripts
- `.dev/guides/ai-collaboration-guides/` 保留人類入口
- `.codex/` 若存在，僅保留 Codex runtime config 或狀態

### Codex 的實務做法

- `.agents/skills/` 作為目前 repo 內的 Codex / agent runtime skill wrappers
- 若要讓 Codex 直接把某 skill 當成可用 skill，應優先維護 `.agents/skills/`
- `.codex/` 若存在，處理的是本機 runtime 設定，不是 canonical skill registry

## 為什麼不建議把 repo skill 真相放到 runtime wrapper

- 你目前同時使用 Codex、Gemini、GitHub Copilot
- `.agents/skills/` 或 `.claude/skills/` 都屬於 wrapper layer
- 未來若還要補 `.gemini/` 或 Copilot 對應配置，會更難建立一致的 cross-agent 分工

## 更穩定的收納方式

### Canonical Source

- `.ai/assets/`
  - canonical skill specs
  - canonical sub-agent role prompt specs
  - legacy command specs during migration
  - shared prompt packages
- `.ai/`
  - 通用 prompt 元件
  - shared rules
  - scripts
- `.dev/guides/ai-collaboration-guides/`
  - human-facing 使用方式
  - workflow guide
  - prompt guide

### Agent Runtime Wrapper

- `.agents/skills/`
  - current runtime skill wrappers
- `.claude/skills/`
  - Claude runtime skill wrappers
- `.gemini/commands/`
  - Gemini compatibility wrappers
- `.github/prompts/`
  - GitHub Copilot prompt-oriented wrappers
- `.github/copilot-instructions.md`
  - GitHub Copilot repo-level instructions

如果未來要支援更多 agent-specific runtime 格式，再額外增加：

- `.gemini/...`
- `.github/copilot/...`
- `.codex/...`

但這些應視為 wrapper / adapter，不應取代 `.ai/` 與 `.dev/` 的 canonical source 角色。

## 目前 repo 的建議決策

1. 將 `.ai/assets/skills/` 作為 canonical skill registry 與 spec 位置
2. 保留 `.claude/skills/` 作為 Claude runtime skill wrapper 位置
3. `.agents/skills/` 作為目前主要 runtime skill wrapper layer
4. delegated worker roles 收斂於 `.ai/assets/sub-agent-role-prompts/`
5. 將「Codex 直接可用」視為 wrapper + 本機設定問題，不是 canonical source 位置問題
6. 將 `.ai/` 與 `.dev/guides/ai-collaboration-guides/` 視為跨 agent 長期可重用資產

## 目前對 runtime wrapper 的限制

無論是 `.agents/skills/` 或 `.claude/skills/`，仍應遵守下列限制：

- 不將 canonical source 改放到 runtime wrapper
- 不把完整 references 複製到 runtime wrappers
- 目前不導入 sync/export tooling
- 若未來擴大遷移更多 skills，應先決定是手動 thin wrapper 還是 generated wrapper

