# Stage A Codex Skill Root

本階段補上 Codex runtime skill wrapper 的根目錄與基本慣例，將 `.codex/prompts/` 與 `.codex/skills/` 分成不同責任。

## Completed

- 建立 `.codex/skills/` 作為 runtime skill wrapper root
- 建立 root README，定義 wrapper rules 與預期結構

## Outcome

目前 Codex 相關層次變成：

- `.codex/prompts/`
  - prompt-oriented wrappers
- `.codex/skills/`
  - runtime skill wrappers

這讓後續可以用同一個 canonical skill source，同時支援：

- prompt-style invocation
- runtime skill-style invocation
