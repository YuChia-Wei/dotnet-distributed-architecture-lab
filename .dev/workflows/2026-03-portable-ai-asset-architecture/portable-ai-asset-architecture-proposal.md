# Portable AI Asset Architecture Proposal

> Superseded proposal snapshot: 本文件保存提案階段的設計語境。最終落地模型已修正為 `top-level skills + delegated sub-agent-role prompts + shared/supporting materials`，不應再把其中早期的 command / prompt 假設視為現況。

## Goal

建立一套可攜、可版本控管、可跨多 agent 重用的 AI asset architecture，使 skill、commands、prompts、workflow rules 不必在各 agent 目錄手工維護完整副本。

## Problem Summary

目前 repo 已初步形成以下分工：

- `.ai/`
  - agent-facing reusable assets
- `.claude/skills/`
  - repo-local skill definitions
- `.dev/guides/ai-collaboration-guides/`
  - human-facing guides

這已經比直接把所有內容塞進單一目錄好，但仍缺少一層真正的 canonical source。  
因此目前的 skill 定義仍偏向某個 agent wrapper，而不是跨 agent 的中立資產。

## Proposed Model

### 1. Canonical Source Layer

目的：

- 保存單一真相
- 不依賴特定 agent runtime
- 支援後續匯出/同步成不同 wrapper

建議內容：

- skill spec
- command spec
- prompt packages
- shared rules
- workflow contracts

### 2. Human-Facing Guide Layer

保留在：

- `.dev/guides/ai-collaboration-guides/`

用途：

- 說明如何用
- 解釋 workflow
- 提供 prompt templates
- 說明何時用哪個 skill / prompt / command

### 3. Agent Wrapper Layer

現階段保留：

- `.claude/skills/`

未來可能增加：

- `.codex/`
- `.gemini/`
- `.github/`

原則：

- wrapper 只放 agent-specific metadata、trigger、runtime format
- wrapper 不應變成第二份 canonical source

### 4. Generation / Sync Layer

後續可選：

- `.ai/scripts/export-*`
- `.ai/scripts/sync-*`

用途：

- 從 canonical source 產出 agent wrappers
- 安裝或同步到本機 runtime

## Proposed Canonical Structure

這是目前建議的第一版候選結構：

```text
.ai/
  assets/
    skills/
      <skill-id>/
        skill.yaml
        prompts/
        references/
        examples/
    commands/
      <command-id>/
        command.yaml
        prompts/
        examples/
    shared/
      rules/
      templates/
      contracts/
```

## Known Repo-Level Agent Paths

根據目前 repo 內既有結構與 `README.md` 的描述，現階段可確認的 agent-related 路徑如下：

| Agent | Repo-Level Context / Instructions | Repo-Level Command / Prompt / Skill Wrapper |
|------|-----------------------------------|---------------------------------------------|
| Claude | `agents.md` + `.claude/skills/` | `.claude/skills/` |
| Codex | `agents.md` | `.codex/prompts/` |
| Gemini | `.gemini/settings.json` + `agents.md` | `.gemini/commands/` |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/prompts/` |

目前實體存在狀況：

- 已存在：`.claude/skills/`
- 已存在：`.gemini/settings.json`
- 尚未建立但 repo README 已視為預期位置：
  - `.codex/prompts/`
  - `.gemini/commands/`
  - `.github/prompts/`
  - `.github/copilot-instructions.md`

因此本次規劃應以這些 repo-level 路徑為「預期 wrapper interface」，而不是臨時發明新的 agent 目錄命名。

## Why `assets/`

- 比直接叫 `skills/` 更中立
- 可以同時容納 skills、commands、prompt packages
- 避免 `.ai/assets/` 被迫同時兼任 command catalog 與 generic fragments

## Wrapper Strategy Options

### Option A: Thin Wrappers

做法：

- `.claude/skills/<skill-id>/SKILL.md` 保留
- 內容只做 agent runtime glue
- 主要規則與內容指回 canonical source

優點：

- 快速落地
- 不需先做 generator

缺點：

- 仍要維護少量 wrapper 文件

### Option B: Generated Wrappers

做法：

- wrapper 由 canonical source 自動生成

優點：

- 最接近單一真相
- 長期維護成本最低

缺點：

- 初期成本最高
- 需要先穩定 schema

## Recommended Decision

建議採用：

1. 先做 canonical schema
2. 先保留 `.claude/skills/` 作為 thin wrappers
3. 先選一個 pilot skill 做 migration
4. 等 schema 穩定後，再做 generated wrappers

## Local Installation / Sync Note

本次重構仍應以 repo-level portability 為主。  
若需要讓 Codex 在本機直接讀取 repo 內的 `.codex/` 資源，可使用：

```powershell
setx CODEX_HOME "C:\Github\YuChia\dotnet-mq-arch-lab\.codex"
```

注意：

- 這是本機 runtime 指向 repo 內 `.codex/` 的作法，不是 canonical source 的位置。
- 切換後通常需要重新啟動 Codex。
- 工作結束後若不想影響其他 workspace，應還原或清除 `CODEX_HOME`。

理想作法仍然是：

- repo 內維護 portable canonical source
- `.codex/` 只作為 Codex runtime wrapper / install target

## Pilot Candidates

最適合作為 pilot 的候選：

### Candidate A: `ddd-ca-hex-architect`

優點：

- 已有明確 skill guide
- 已有 references 與 prompt pointer
- 能測試 skill spec + guide + wrapper 三層關係

風險：

- 結構比一般 skill 複雜

### Candidate B: `bdd-gwt-test-designer`

優點：

- scope 較集中
- 容易觀察 scenario-design prompts 的 packaging

風險：

- 對 command prompt portability 的驗證較少

### Candidate C: 一組 command prompts

例如：

- `command-sub-agent-prompt`
- `query-sub-agent-prompt`
- `reactor-sub-agent-prompt`

優點：

- 可先驗證 command spec

風險：

- 無法完整驗證 skill wrapper 問題

## Recommended Execution Order

1. 完成 inventory 與 asset taxonomy
2. 定義 canonical schema
3. 選 `ddd-ca-hex-architect` 或 `bdd-gwt-test-designer` 做第一個 pilot
4. 選一組 command prompts 做第二個 pilot
5. 再決定是否導入 generated wrapper strategy

## Decision Gates

在進入下一階段前應確認：

- canonical source 的最低欄位是否已足夠
- wrapper 是否能保持薄且不重複
- `.ai/` 是否仍維持跨 agent 可重用定位
- `.dev/guides/ai-collaboration-guides/` 是否仍維持 human-facing guide 定位

