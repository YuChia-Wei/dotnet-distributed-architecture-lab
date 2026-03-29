# Codex Runtime Skill Wrappers

本目錄放置 repo-local 的 Codex runtime skill wrappers。

## 角色

- 提供 Codex 可直接辨識的 runtime skill 入口
- 將 runtime-facing `SKILL.md` 與 repo 內 canonical source 分離
- 避免把完整 skill 內容複製到 Codex-specific 目錄

## 與其他目錄的分工

- `.ai/assets/`
  - canonical source
- `.dev/guides/ai-collaboration-guides/`
  - human-facing guides
- `.codex/skills/`
  - runtime skill wrappers

## Wrapper Rules

- wrapper 必須薄
- `SKILL.md` 應清楚指向 canonical source 與 human-facing guide
- wrapper 不應成為第二份 skill 真相
- 若需要 references，優先使用薄指標檔而非複製全文
- Codex-specific invocation wording 可以放在 wrapper 中

## Expected Structure

```text
.codex/
  skills/
    <skill-id>/
      SKILL.md
      references/
```

## Current Skill Index

- `bdd-gwt-test-designer`
- `code-reviewer`
- `ddd-ca-hex-architect`
- `spec-compliance-validator`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`

