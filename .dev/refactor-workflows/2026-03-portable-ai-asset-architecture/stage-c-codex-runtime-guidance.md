# Stage C Codex Runtime Guidance

本階段將 `.codex/skills/` pilot 寫回索引與使用說明，讓文件與實際 repo 狀態一致。

## Completed

- 更新 AI asset location strategy，將 `.codex/skills/` 從 planned 狀態改為已存在的 runtime wrapper layer
- 更新 local runtime wrapper guide，說明 `CODEX_HOME=.codex` 時 prompt wrappers 與 runtime skill wrappers 的差異
- 更新 workflow follow-up 說明，記錄目前已有 root 與 pilot wrapper

## Outcome

目前 Codex 在 repo 內有兩種不同入口：

- `.codex/prompts/`
  - prompt-oriented wrappers
- `.codex/skills/`
  - runtime skill wrappers

這個分流已正式進入 human-facing guide 與 workflow 記錄。
