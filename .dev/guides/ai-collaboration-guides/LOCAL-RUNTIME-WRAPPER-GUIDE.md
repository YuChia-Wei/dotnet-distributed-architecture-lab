# Local Runtime Wrapper Guide

本文件說明 repo-level portable AI assets 與本機 agent runtime 之間的關係。

## 原則

- repo 內的 canonical source 以 `.ai/assets/` 為主
- repo 內目前的 wrapper roots 是 `.agents/skills/` 與 `.claude/skills/`
- 本機 runtime 設定只是讓 agent 指到 repo wrapper，不是 canonical source 本身
- prompt wrappers 與 runtime skill wrappers 是不同層次，不應混為一談
- 目前不提供 sync/export tooling；wrapper 採 repo-local 管理

## Repo-Level Wrapper Roots

- Agents / Codex current runtime:
  - `.agents/skills/`
- Claude:
  - `.claude/skills/`

GitHub Copilot wrapper 尚未建立；`.github/prompts/` 與 `.github/copilot-instructions.md` 僅是規劃中的可選整合路徑，不是目前 repo runtime surface。

## Codex Local Runtime

目前 repo 內與 Codex skill 對應的 wrapper 以：

- `.agents/skills/`
  - current runtime skill wrappers

`.codex/` 若存在，應視為本機設定或 runtime-specific state，不是 canonical skill registry。

若本機需要設定 Codex 指向 repo-local runtime state：

```powershell
setx CODEX_HOME "<repo-path>\.codex"
```

注意：

- 變更後通常需要重新啟動 Codex
- 這是本機 runtime 指向 repo wrapper 的作法
- 它不改變 canonical source 位置
- Codex skill wrapper 的 canonical runtime 路徑應以 `.agents/skills/` 為準
- 目前不提供額外的 sync/export script；wrapper 採 repo-local version control 管理

若要清除：

```powershell
setx CODEX_HOME ""
```

## GitHub Copilot

目前 repo 不提供 GitHub Copilot runtime wrapper。若未來啟用，預計使用：

- `.github/copilot-instructions.md`
- `.github/prompts/`

建立並通過驗證前不得列為 current runtime。

## 建議使用順序

1. 先讀 `.ai/assets/` canonical source
2. top-level skill 優先讀 `.ai/assets/skills/README.MD` 與對應 `skill.yaml`
3. delegated worker roles 優先讀 `.ai/assets/sub-agent-role-prompts/`
4. 再分辨要讀的是 canonical source 還是 runtime skill wrapper
5. 再讀對應 agent 的 wrapper
6. Codex / agent runtime 若需 skill wrapper，優先讀 `.agents/skills/`
7. 需要人類說明時，再看 `.dev/guides/ai-collaboration-guides/`
