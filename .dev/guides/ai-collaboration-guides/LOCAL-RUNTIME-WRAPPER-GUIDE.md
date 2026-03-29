# Local Runtime Wrapper Guide

本文件說明 repo-level portable AI assets 與本機 agent runtime 之間的關係。

## 原則

- repo 內的 canonical source 以 `.ai/assets/` 為主
- repo 內的 wrapper roots 以 `.claude/skills/`、`.codex/skills/`、`.gemini/commands/`、`.github/prompts/` 為主
- 本機 runtime 設定只是讓 agent 指到 repo wrapper，不是 canonical source 本身
- prompt wrappers 與 runtime skill wrappers 是不同層次，不應混為一談
- 目前不提供 sync/export tooling；wrapper 採 repo-local 管理

## Repo-Level Wrapper Roots

- Claude:
  - `.claude/skills/`
- Codex:
  - `.codex/skills/`
- Gemini:
  - `.gemini/commands/`
- GitHub Copilot:
  - `.github/prompts/`
  - `.github/copilot-instructions.md`

## Codex Local Runtime

目前 repo 已有：

- `.codex/skills/`
  - Codex runtime skill wrappers

若要讓 Codex 直接讀取 repo 內 `.codex/`：

```powershell
setx CODEX_HOME "C:\Github\YuChia\dotnet-mq-arch-lab\.codex"
```

注意：

- 變更後通常需要重新啟動 Codex
- 這是本機 runtime 指向 repo wrapper 的作法
- 它不改變 canonical source 位置
- 若 `CODEX_HOME` 指到 repo 的 `.codex`，Codex runtime skill 應從 `.codex/skills/` 讀取
- 目前不提供額外的 sync/export script；維護方式是直接版本控管 `.codex/skills/` thin wrappers

若要清除：

```powershell
setx CODEX_HOME ""
```

## Gemini Local Runtime

目前 repo 內的 Gemini 入口以：

- `.gemini/settings.json`
- `.gemini/commands/`

為主。  
`settings.json` 用來補 default context，`commands/` 用來放 repo-local wrapper commands。

## GitHub Copilot

目前 repo 內的 Copilot 入口以：

- `.github/copilot-instructions.md`
- `.github/prompts/`

為主。

## 建議使用順序

1. 先讀 `.ai/assets/` canonical source
2. delegated worker roles 優先讀 `.ai/assets/sub-agent-role-prompts/`
3. 再分辨要讀的是 canonical source 還是 runtime skill wrapper
4. 再讀對應 agent 的 wrapper
5. Codex 若需原生 runtime skill，優先讀 `.codex/skills/`
6. 需要人類說明時，再看 `.dev/guides/ai-collaboration-guides/`
