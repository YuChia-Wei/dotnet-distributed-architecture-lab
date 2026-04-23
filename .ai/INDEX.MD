# .ai Index

本文件是 `.ai/` 的 agent-facing 索引。

## Core

- `README.MD`
  - `.ai/` 目錄用途與分工
- `DIRECTORY-RULES.MD`
  - `.ai/` 與 `.dev/` 的放置規則
- `SUB-AGENT-SYSTEM.MD`
  - sub-agent 系統、routing、artifact 讀寫規則
- `CODE-REVIEW-INDEX.MD`
  - code review workflow 入口

## Prompt Assets

- `assets/`
  - canonical source root for portable AI assets
- `assets/shared/`
  - shared rules / prompt fragments / reusable supporting materials
- `assets/sub-agent-role-prompts/`
  - delegated sub-agent role prompt canonical assets
- `assets/skills/`
  - canonical skill registry and skill specs
- `assets/templates/`
  - canonical templates for skills / prompts / commands

## Script Assets

- `scripts/`
  - validation / review / generation scripts
- `scripts/generated/`
  - generated check scripts
- `scripts/README.md`
  - scripts 使用入口

## Supporting References

- `BUILDING-BLOCKS-CLASS-INDEX.MD`
  - BuildingBlocks 類型索引
- `FAILURE-CASES.MD`
  - 常見錯誤案例
- `COMMON-PITFALLS.MD`
  - 常見陷阱與解法
- `CODE-TEMPLATES.MD`
  - .NET 程式碼模板

## Related Human-Facing Docs

- `../.dev/guides/README.MD`
  - human-facing guides 入口
- `../.dev/guides/ai-collaboration-guides/README.MD`
  - AI collaboration guides 入口
- `../.dev/guides/ai-collaboration-guides/REPO-STRUCTURE-SYNC-SKILL-GUIDE.md`
  - template 移植到新 repo 後的架構同步指南
- `../.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md`
  - 多 agent 情境下的 skill / prompt / guide 收納策略
- `../.claude/skills/README.md`
  - repo-local skill definition 入口
